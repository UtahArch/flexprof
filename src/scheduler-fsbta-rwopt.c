#include "utils.h"
#include "utlist.h"
#include <stdio.h>
#include <stdlib.h>

#include "memory_controller.h"
#include "params.h"
//rwopt is the prior name for FlexProf. (Read Write Opt - rwopt)

extern long long int CYCLE_VAL;
int size_of_command(){
  int size = 0;
  opt_queue_t *rq_ptr = NULL;
  LL_FOREACH(channel_fs_data[0].command_order, rq_ptr) {size++;}
  return size;
}
/* Keeping track of how many preemptive precharges are performed. */
long long int num_aggr_precharge = 0;
int recent_colacc[MAX_NUM_CHANNELS][MAX_NUM_RANKS][MAX_NUM_BANKS];

int max(int a, int b) {
    return (a > b) ? a : b;
}


int get_ratio(int domain){
  switch(domain){
    case 0:
      return D1;
    case 1:
      return D2;
    case 2:
      return D3;
    case 3:
      return D4;
    case 4:
      return D5;
    case 5:
      return D6;
    case 6:
      return D7;
    case 7:
      return D8;
    case 8:
      return D9;
    case 9:
      return D10;
    case 10:
      return D11;
    case 11:
      return D12;
    default:
      return 0;
  }
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
    channel_fs_data[i].rwopt_pointer = 0;
    channel_fs_data[i].deadtime = 6;

    channel_fs_data[i].domain_reads = NULL;
    channel_fs_data[i].domain_writes = NULL;
    channel_fs_data[i].command_order = NULL;
    channel_fs_data[i].pointer = 0;
    channel_fs_data[i].rank_used = -1;
    channel_fs_data[i].bank_used = -1;
    channel_fs_data[i].request_sent = 0;
    channel_fs_data[i].first_read_sent = 0;
    channel_fs_data[i].second_read_sent = 0;
    channel_fs_data[i].turn_len = 11;
    channel_fs_data[i].bubble = 0;
    channel_fs_data[i].prev = 0;
    channel_fs_data[i].current_turn_time = 0;
    channel_fs_data[i].write_ready = 0;
    channel_fs_data[i].read_ready = 0;

  }

  //set security policy and deadtime
  SECURED = 1;
  DEADTIME = 15;
  RWOPT = 1;
  ALTERATION = 4;
  return;
}
int len_if_cmd(int channel){
  int len = 0;
  opt_queue_t *rq_ptr = NULL;
  LL_FOREACH(channel_fs_data[channel].command_order, rq_ptr) {len++;}
  return len;
}

int is_write_ready(int channel, int domain_turn, int bank_turn){
  request_t *rq_ptr = NULL;
  LL_FOREACH(domain_write_queues[channel][domain_turn], rq_ptr){
    if (rq_ptr->next_command == ACT_CMD && 
        rq_ptr->dram_addr.rank % ALTERATION == bank_turn){
      return 1;
    }
  }
  return 0;
}

int is_read_ready(int channel, int domain_turn, int bank_turn){
  request_t *rq_ptr = NULL;
  LL_FOREACH(domain_read_queues[channel][domain_turn], rq_ptr){
    if (rq_ptr->next_command == ACT_CMD && 
        rq_ptr->dram_addr.rank % ALTERATION == bank_turn){
      return 1;
    }
  }
  return 0;
}

int read_count(int channel, int domain_turn, int bank_turn){
  request_t *rq_ptr = NULL;
  int count = 0;

  LL_FOREACH(domain_read_queues[channel][domain_turn], rq_ptr){
    if (rq_ptr->next_command == ACT_CMD && 
        rq_ptr->dram_addr.rank % ALTERATION == bank_turn){
      count++;
    }
  }
  return count;
}

int write_count(int channel, int domain_turn, int bank_turn){
  request_t *rq_ptr = NULL;
  int count = 0;

  LL_FOREACH(domain_write_queues[channel][domain_turn], rq_ptr){
    if (rq_ptr->next_command == ACT_CMD && 
        rq_ptr->dram_addr.rank % ALTERATION == bank_turn){
      count++;
    }
  }
  return count;
}

int send_read(int channel, int domain_turn, int bank_turn, int special){
  request_t *rq_ptr = NULL;

  LL_FOREACH(domain_read_queues[channel][domain_turn], rq_ptr){
    if (rq_ptr->next_command == ACT_CMD && 
        rq_ptr->dram_addr.rank % ALTERATION == bank_turn &&
        rq_ptr->command_issuable == 1){

      if(special == 1){
        if(channel_fs_data[channel].rank_used != -1){
          if(rq_ptr->dram_addr.rank != channel_fs_data[channel].rank_used){
              continue; // we are doing two reads to the same rank
          }
        }
      }

      issue_request_command(rq_ptr);

      opt_queue_t *opt = malloc(sizeof(opt_queue_t));
      opt->domain_id = domain_turn;
      opt->next = NULL;
      opt->write = 0;
      opt->addr = rq_ptr->dram_addr.actual_address;
      LL_APPEND(channel_fs_data[channel].command_order, opt);
      bank_reads[rq_ptr->dram_addr.rank]++;
      channel_fs_data[channel].rank_used = rq_ptr->dram_addr.rank;
      channel_fs_data[channel].bank_used = rq_ptr->dram_addr.bank;
      return 1;
    }
  }
  return 0;
}

int send_write(int channel, int domain_turn, int bank_turn, int special){
  request_t *rq_ptr = NULL;
  LL_FOREACH(domain_write_queues[channel][domain_turn], rq_ptr){
    if (rq_ptr->next_command == ACT_CMD && 
        rq_ptr->dram_addr.rank % ALTERATION == bank_turn &&
        rq_ptr->command_issuable == 1){

      if(special == 1){
        if(channel_fs_data[channel].rank_used != -1){
          if(rq_ptr->dram_addr.rank != channel_fs_data[channel].rank_used){
              continue; // we are doing two reads to the same rank
          }
        }
      }

      issue_request_command(rq_ptr);

      opt_queue_t *opt = malloc(sizeof(opt_queue_t));
      opt->domain_id = domain_turn;
      opt->next = NULL;
      opt->write = 1;
      opt->addr = rq_ptr->dram_addr.actual_address;
      LL_APPEND(channel_fs_data[channel].command_order, opt);
      bank_writes[rq_ptr->dram_addr.rank]++;
      channel_fs_data[channel].rank_used = rq_ptr->dram_addr.rank;
      channel_fs_data[channel].bank_used = rq_ptr->dram_addr.bank;
      return 1;
    }
  }
  return 0;
}


void schedule(int channel) {
  //if refresing, do nothing, just wait ig idk!
  int current_turn_time = channel_fs_data[channel].current_turn_time;
  int domain_turn = rwopt_buffer[channel_fs_data[channel].rwopt_pointer].domain_id;
  int write_mode = rwopt_buffer[channel_fs_data[channel].rwopt_pointer].op;
  int bank_turn = (channel_fs_data[channel].rwopt_pointer) % ALTERATION;
  int reqeust_sent = channel_fs_data[channel].request_sent;
  int turn_len = channel_fs_data[channel].turn_len;

  //if it is the deadtime cycle, send a ready act to bank_turn
  if(channel_fs_data[channel].bubble == 1){
    //blem
  } else {
    if(refresh_issue_deadline[channel][0] <= CYCLE_VAL + 200){ //do not send request if close to refresh
    //do nothing
    } else {
      //int drain_writes = start_write_drain(channel, domain_turn);
      //maybe the op type was not ready, so let see if we can send any request regardless of op type
      if(write_mode == 0){
        if(current_turn_time == 0){
          int read_ready = is_read_ready(channel, domain_turn, bank_turn);
          if(read_ready == 1){
            channel_fs_data[channel].read_ready = 1;
          }
        }
        if(channel_fs_data[channel].read_ready == 1){
          if(current_turn_time == 0){
              if (send_read(channel, domain_turn, bank_turn, 0)){
                  reqeust_sent++;

              }
          }
          if(current_turn_time == 6){
              if (send_read(channel, domain_turn, bank_turn, 0)){
                  reqeust_sent++;
              }
          }
        } else {
          //try a two writes to same rank
          if(current_turn_time == 6){
            if (send_write(channel, domain_turn, bank_turn, 1)){
                reqeust_sent++;
            }
          }
          if(current_turn_time == 11){
            if (send_write(channel, domain_turn, bank_turn, 1)){
                reqeust_sent++;
            }
          }
        }
      } else {
        //check if any write is ready
        if(current_turn_time == 0){
          int reads = read_count(channel, domain_turn, bank_turn);
          if(reads == 2){
            channel_fs_data[channel].write_ready = 0;
          }  else {
            int write_ready = is_write_ready(channel, domain_turn, bank_turn);
            if(write_ready == 1){
              channel_fs_data[channel].write_ready = 1;
            } else {
              channel_fs_data[channel].write_ready = 0;
            }
          }
        }

        if(channel_fs_data[channel].write_ready == 1){
          if(current_turn_time == 6){
            if (send_write(channel, domain_turn, bank_turn, 0)){
                reqeust_sent++;
            }
          }
          if(current_turn_time == 12){
            if (send_write(channel, domain_turn, bank_turn, 0)){
                reqeust_sent++;
            }
          }
        } else {
          //we doing one reads to the same rank
          if(current_turn_time == 0){
            if (send_read(channel, domain_turn, bank_turn, 0)){
                reqeust_sent++; 
            }
          }
          if(current_turn_time == 6){
            if (send_read(channel, domain_turn, bank_turn, 0)){
                reqeust_sent++;
            }
          }
        }
      }
    } 
  }

  //continue on man!
  if (!command_issued_current_cycle[channel]) {
    if (channel_fs_data[channel].command_order != NULL){
      request_t *ptr = NULL;
      if(channel_fs_data[channel].command_order->write == 0){
        LL_FOREACH(domain_read_queues[channel][channel_fs_data[channel].command_order->domain_id], ptr){
          if (ptr->next_command != ACT_CMD && 
            ptr->operation_type == channel_fs_data[channel].command_order->write &&
            ptr->dram_addr.actual_address == channel_fs_data[channel].command_order->addr &&
            ptr->domain_id == channel_fs_data[channel].command_order->domain_id && 
            ptr->command_issuable == 1){
            assert(ptr->activation_cycle == CYCLE_VAL - T_RCD);
            assert(ptr->next_command != PRE_CMD); //we should never need to issue a precharge as it is close page
            assert(len_if_cmd(channel) <= 4);
            LL_DELETE(channel_fs_data[channel].command_order, channel_fs_data[channel].command_order);
            
            recent_colacc[channel][ptr->dram_addr.rank][ptr->dram_addr.bank] = 1;
          
            issue_request_command(ptr);
            break;
          }
        }
      } else {
        LL_FOREACH(domain_write_queues[channel][channel_fs_data[channel].command_order->domain_id], ptr){
          if (ptr->next_command != ACT_CMD && 
            ptr->operation_type == channel_fs_data[channel].command_order->write &&
            ptr->dram_addr.actual_address == channel_fs_data[channel].command_order->addr &&
            ptr->domain_id == channel_fs_data[channel].command_order->domain_id && 
            ptr->command_issuable == 1){
            assert(ptr->activation_cycle == CYCLE_VAL - T_RCD);
            assert(ptr->next_command != PRE_CMD);
            assert(len_if_cmd(channel) <= 4);
            LL_DELETE(channel_fs_data[channel].command_order, channel_fs_data[channel].command_order);
            
            recent_colacc[channel][ptr->dram_addr.rank][ptr->dram_addr.bank] = 1;
          
            issue_request_command(ptr);
            break;
          }
        }
      }
      
    }
  }

  channel_fs_data[channel].request_sent = reqeust_sent;

  if(current_turn_time >= turn_len && channel_fs_data[channel].bubble == 0){
    channel_fs_data[channel].current_turn_time = 0;
    channel_fs_data[channel].rank_used = -1;
    channel_fs_data[channel].bank_used = -1;
    channel_fs_data[channel].request_sent = 0;
    channel_fs_data[channel].first_read_sent = 0;
    channel_fs_data[channel].second_read_sent = 0;
    channel_fs_data[channel].write_ready = 0;
    channel_fs_data[channel].read_ready = 0;
    int curr_mode = rwopt_buffer[channel_fs_data[channel].rwopt_pointer].op;
    channel_fs_data[channel].prev = curr_mode;
    channel_fs_data[channel].rwopt_pointer = (channel_fs_data[channel].rwopt_pointer + 1) % rwopt_len;
    int next_mode = rwopt_buffer[channel_fs_data[channel].rwopt_pointer].op;

    if(next_mode == 0){
      channel_fs_data[channel].turn_len = 11;
    } else {
      channel_fs_data[channel].turn_len = 12;
    }

  } else {
    if(channel_fs_data[channel].bubble == 0){
      channel_fs_data[channel].current_turn_time++;
    }
      channel_fs_data[channel].bubble = 0;
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
}

void scheduler_stats() {
  /* Nothing to print for now. */
  printf("Number of aggressive precharges: %lld\n", num_aggr_precharge);
}

