#include "utils.h"
#include "utlist.h"
#include <stdio.h>
#include <stdlib.h>

#include "memory_controller.h"
#include "params.h"


extern long long int CYCLE_VAL;

/* A data structure to see if a bank is a candidate for precharge. */
int recent_colacc[MAX_NUM_CHANNELS][MAX_NUM_RANKS][MAX_NUM_BANKS];

/* Keeping track of how many preemptive precharges are performed. */
long long int num_aggr_precharge = 0;
int len_if_cmd(int channel){
  int len = 0;
  opt_queue_t *rq_ptr = NULL;
  LL_FOREACH(channel_fs_data[channel].command_order, rq_ptr) {len++;}
  return len;
}
void init_scheduler_vars() {
  // initialize all scheduler variables here
  int i, j, k;
  for (i = 0; i < MAX_NUM_CHANNELS; i++) {
    for (j = 0; j < MAX_NUM_RANKS; j++) {
      for (k = 0; k < MAX_NUM_BANKS; k++) {
        recent_colacc[i][j][k] = 0;
      }
    }
  }

  for (i = 0; i < MAX_NUM_CHANNELS; i++) {
    channel_fs_data[i].last_req_issue_cycle = 0;
    channel_fs_data[i].domain_turn = 0;
    channel_fs_data[i].bank_turn = 0;
    channel_fs_data[i].domain_zero_starter = 0;
    channel_fs_data[i].command_order = NULL;
    channel_fs_data[i].drain_writes = 0;
  }
  
  //set security policy and deadtime
  SECURED = 1;
  DEADTIME = 15;

  return;
}

int send_read(int channel, int domain_turn, int bank_turn){
  request_t *rq_ptr = NULL;
  LL_FOREACH(domain_read_queues[channel][domain_turn], rq_ptr){
    //if issuable, is an act, matches bank, and is deadtime
    //must send an act to bank_turn
    if (rq_ptr->command_issuable && 
        rq_ptr->next_command == ACT_CMD && 
        rq_ptr->dram_addr.bank_id % 3 == bank_turn)
    {
      issue_request_command(rq_ptr);
      opt_queue_t *opt = malloc(sizeof(opt_queue_t));
      opt->domain_id = domain_turn;
      opt->next = NULL;
      opt->write = rq_ptr->operation_type;
      opt->addr = rq_ptr->dram_addr.actual_address;
      LL_APPEND(channel_fs_data[channel].command_order, opt);
      return 1;
    }
  }
  return 0;
}

int send_write(int channel, int domain_turn, int bank_turn){
  request_t *rq_ptr = NULL;
  LL_FOREACH(domain_write_queues[channel][domain_turn], rq_ptr){
    //if issuable, is an act, matches bank, and is deadtime
    //must send an act to bank_turn
    if (rq_ptr->command_issuable && 
        rq_ptr->next_command == ACT_CMD && 
        rq_ptr->dram_addr.bank_id % 3 == bank_turn)
    {
      issue_request_command(rq_ptr);
      opt_queue_t *opt = malloc(sizeof(opt_queue_t));
      opt->domain_id = domain_turn;
      opt->next = NULL;
      opt->write = rq_ptr->operation_type;
      opt->addr = rq_ptr->dram_addr.actual_address;
      LL_APPEND(channel_fs_data[channel].command_order, opt);
      return 1;
    }
  }
  return 0;
}

int next_request_is_write(int channel, int domain_turn, int bank_turn){
  request_t *read_ptr = NULL;
  request_t *write_ptr = NULL;
  LL_FOREACH(domain_read_queues[channel][domain_turn], read_ptr){
    if (read_ptr->command_issuable && 
        read_ptr->next_command == ACT_CMD && 
        read_ptr->dram_addr.bank_id % 3 == bank_turn)
    {
      break;
    }
  }
  LL_FOREACH(domain_write_queues[channel][domain_turn], write_ptr){
    if (write_ptr->command_issuable && 
        write_ptr->next_command == ACT_CMD && 
        write_ptr->dram_addr.bank_id % 3 == bank_turn)
    {
      break;
    }
  }
  if(write_ptr == NULL){
    return 0;
  } else if (read_ptr == NULL){
    return 1;
  }
  
  if (read_ptr->arrival_time < write_ptr->arrival_time){
    return 0;
  } else {
    return 1;
  }
}

void schedule(int channel) {
  long long last_req_issue_cycle = channel_fs_data[channel].last_req_issue_cycle;
  int domain_turn = channel_fs_data[channel].domain_turn;
  int bank_turn = channel_fs_data[channel].bank_turn;
  int domain_zero_starter = channel_fs_data[channel].domain_zero_starter;

  //if it is the deadtime cycle, send a ready act to bank_turn
  if (CYCLE_VAL - last_req_issue_cycle >= DEADTIME || CYCLE_VAL == 0){
    //if bank refreshing 
    if(refresh_issue_deadline[channel][0] <= CYCLE_VAL + 200){ //if close to refresh, dont wait.
      //do nothing
    } else {
      int drain_write = next_request_is_write(channel, domain_turn, bank_turn);
      if(drain_write == 1){
        //send write req to bank_turn, if nothing try read
        if (send_write(channel, domain_turn, bank_turn) == 1){
        } 
      } else {
        //send read req to bank_turn, if nothing try write
        if (send_read(channel, domain_turn, bank_turn) == 1){
        }
      }
     
    }
    last_req_issue_cycle = CYCLE_VAL;
    bank_turn = (bank_turn + 1) % 3;
    domain_turn = (domain_turn + 1) % DOMAIN_COUNT;

  }
  //continue on man!
  else {
    if (channel_fs_data[channel].command_order != NULL){
      request_t *ptr = NULL;
      LL_FOREACH(domain_read_queues[channel][channel_fs_data[channel].command_order->domain_id], ptr){
        if (ptr->command_issuable && 
           ptr->next_command != ACT_CMD &&
           ptr->operation_type == channel_fs_data[channel].command_order->write &&
           ptr->dram_addr.actual_address == channel_fs_data[channel].command_order->addr){

          assert(ptr->next_command != PRE_CMD); //we should never need to issue a precharge as it is close page
          assert(len_if_cmd(channel) <= 2);
          opt_queue_t *opt = channel_fs_data[channel].command_order;
          LL_DELETE(channel_fs_data[channel].command_order, opt);
          free(opt);
          
          recent_colacc[channel][ptr->dram_addr.rank][ptr->dram_addr.bank] = 1;
        
          issue_request_command(ptr);
          break;
        }
      }
      
      if(!command_issued_current_cycle[channel]){
        LL_FOREACH(domain_write_queues[channel][channel_fs_data[channel].command_order->domain_id], ptr){
          if (ptr->command_issuable && 
            ptr->next_command != ACT_CMD &&
            ptr->operation_type == channel_fs_data[channel].command_order->write &&
            ptr->dram_addr.actual_address == channel_fs_data[channel].command_order->addr){

            assert(ptr->next_command != PRE_CMD); //we should never need to issue a precharge as it is close page
            assert(len_if_cmd(channel) <= 2);
            opt_queue_t *opt = channel_fs_data[channel].command_order;
            LL_DELETE(channel_fs_data[channel].command_order, opt);
            free(opt);
            
            recent_colacc[channel][ptr->dram_addr.rank][ptr->dram_addr.bank] = 1;
          
            issue_request_command(ptr);
            break;
          }
        }
      }
    }
  }

  if (!command_issued_current_cycle[channel]) {
    for (int i = 0; i < NUM_RANKS; i++) {
      for (int j = 0; j < NUM_BANKS; j++) { /* For all banks on the channel.. */
        if (recent_colacc[channel][i][j]) { /* See if this bank is a candidate. */
          if (issue_precharge_command(channel, i, j)) {
            num_aggr_precharge++;
            recent_colacc[channel][i][j] = 0;
          }
        }
      }
    }
  }
  //update the scheduler variables
  channel_fs_data[channel].last_req_issue_cycle = last_req_issue_cycle;
  channel_fs_data[channel].domain_turn = domain_turn;
  channel_fs_data[channel].bank_turn = bank_turn;
  channel_fs_data[channel].domain_zero_starter = domain_zero_starter;
}

void scheduler_stats() {
  /* Nothing to print for now. */
  printf("Number of aggressive precharges: %lld\n", num_aggr_precharge);
}
