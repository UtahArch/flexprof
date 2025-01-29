#include "utils.h"
#include "utlist.h"
#include <stdio.h>
#include <stdlib.h>

#include "memory_controller.h"
#include "params.h"

/* Copied from scheduler-close.c
    Will be modified to work as Fixed Service: Bank Triple Alteration (FSBTA)
   scheduler.
*/

//Called RTA but this is RQA. We do not have an implementation of RTA as it is insecure.

int len_if_cmd(int channel){
  int len = 0;
  opt_queue_t *rq_ptr = NULL;
  LL_FOREACH(channel_fs_data[channel].command_order, rq_ptr) {len++;}
  return len;
}

int ALTERATION = 4;
extern long long int CYCLE_VAL;

/* A data structure to see if a bank is a candidate for precharge. */
int recent_colacc[MAX_NUM_CHANNELS][MAX_NUM_RANKS][MAX_NUM_BANKS];

/* Keeping track of how many preemptive precharges are performed. */
long long int num_aggr_precharge = 0;

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
    channel_fs_data[i].current_turn_time = 0;
    channel_fs_data[i].rank_used = -1;
    channel_fs_data[i].type_sent = -1;
    channel_fs_data[i].bank_used = -1;
    channel_fs_data[i].drain_writes = 0;
    channel_fs_data[i].turn_counter = 0;
    channel_fs_data[i].request_sent = 0;
    channel_fs_data[i].reads_sent = 0;
    channel_fs_data[i].writes_sent = 0;
  }

  for(int i = 0; i < 3; i++){
    total_request_sent[i] = 0;
  }
  both_types_sent = 0;
    reads_sent = 0;
    writes_sent = 0;
  
  //set security policy and deadtime
  SECURED = 1;
  TURN_LEN = 14;

  return;
}

int send_read(int channel, int domain_turn, int turn_counter){
    request_t *rq_ptr = NULL;
    int rank_used = channel_fs_data[channel].rank_used;
    int type_sent = channel_fs_data[channel].type_sent;
    LL_FOREACH(domain_read_queues[channel][domain_turn], rq_ptr){
        if  ((rq_ptr->next_command == ACT_CMD) && 
             rq_ptr->dram_addr.rank % ALTERATION == turn_counter % ALTERATION){
            
            if (rank_used == rq_ptr->dram_addr.rank){
                if (type_sent != rq_ptr->operation_type){
                    continue;
                }
                if(rq_ptr->dram_addr.bank == channel_fs_data[channel].bank_used){
                    continue;
                }
            }

            if(rq_ptr->command_issuable != 1){
                printf("Error: Command not issuable\n");
            }
            issue_request_command(rq_ptr);
            channel_fs_data[channel].rank_used = rq_ptr->dram_addr.rank;
            channel_fs_data[channel].type_sent = rq_ptr->operation_type;
            opt_queue_t *opt = malloc(sizeof(opt_queue_t));
            opt->domain_id = domain_turn;
            opt->next = NULL;
            opt->write = rq_ptr->operation_type;
            opt->addr = rq_ptr->dram_addr.actual_address;
            LL_APPEND(channel_fs_data[channel].command_order, opt);
            bank_reads[rq_ptr->dram_addr.rank]++;
            return 1;
        }
    }
    return 0;
}

int send_write(int channel, int domain_turn, int turn_counter){
    request_t *rq_ptr = NULL;
    int rank_used = channel_fs_data[channel].rank_used;
    int type_sent = channel_fs_data[channel].type_sent;
    LL_FOREACH(domain_write_queues[channel][domain_turn], rq_ptr){
        if  (
            (rq_ptr->next_command == ACT_CMD) && 
             rq_ptr->dram_addr.rank % ALTERATION == turn_counter % ALTERATION)
            {
            if (rank_used == rq_ptr->dram_addr.rank){
                if (type_sent != rq_ptr->operation_type){
                    continue;
                }
                if(rq_ptr->dram_addr.bank == channel_fs_data[channel].bank_used){
                    continue;
                }
            }
            assert(rq_ptr->command_issuable == 1);
            assert(rq_ptr->next_command != PRE_CMD); 
            issue_request_command(rq_ptr);
            channel_fs_data[channel].rank_used = rq_ptr->dram_addr.rank;
            channel_fs_data[channel].type_sent = rq_ptr->operation_type;
            opt_queue_t *opt = malloc(sizeof(opt_queue_t));
            opt->domain_id = domain_turn;
            opt->next = NULL;
            opt->write = rq_ptr->operation_type;
            opt->addr = rq_ptr->dram_addr.actual_address;
            LL_APPEND(channel_fs_data[channel].command_order, opt);
            bank_writes[rq_ptr->dram_addr.rank]++;
            return 1;
        }
    }
    return 0;
}

void schedule(int channel) {

    int domain_turn = channel_fs_data[channel].domain_turn;
    int current_turn_time = channel_fs_data[channel].current_turn_time;
    int turn_counter = channel_fs_data[channel].turn_counter;
    int reqeust_sent = channel_fs_data[channel].request_sent;
    int first_read_sent = channel_fs_data[channel].first_read_sent;
    int second_read_sent = channel_fs_data[channel].second_read_sent;
    int read_sent = channel_fs_data[channel].reads_sent;
    int write_sent = channel_fs_data[channel].writes_sent;

    if(reqeust_sent != 2){
        if(refresh_issue_deadline[channel][0] <= CYCLE_VAL + 200){ //if refresh is up coming do nothing
        //do nothing
        } else {
            //maybe the op type was not ready, so let see if we can send any request regardless of op type
            if(current_turn_time == 0){
                //attempt read
                if (send_read(channel, domain_turn, turn_counter)){
                    reqeust_sent++;
                    first_read_sent = 1;
                    read_sent++;
                }
            }
            if(current_turn_time == 6 && first_read_sent == 0){
                //attempt write
                if (send_write(channel, domain_turn, turn_counter)){
                    reqeust_sent++;
                    first_read_sent = 1;
                    write_sent++;
                }
            }
            if(current_turn_time == 7){
                //attempt read
                if (send_read(channel, domain_turn, turn_counter)){
                    reqeust_sent++;
                    second_read_sent = 1;
                    read_sent++;
                }
            }
            if(current_turn_time == 13 && second_read_sent == 0){
                //attempt write
                if (send_write(channel, domain_turn, turn_counter)){
                    reqeust_sent++;
                    second_read_sent = 1;
                    write_sent++;
                }
            }
        } 
    }

    assert(reqeust_sent <= 2);


    if (!command_issued_current_cycle[channel]) {
        if (channel_fs_data[channel].command_order != NULL){
            request_t *ptr = NULL;
            if(channel_fs_data[channel].command_order->write == 0){
                LL_FOREACH(domain_read_queues[channel][channel_fs_data[channel].command_order->domain_id], ptr){
                    if (ptr->command_issuable && 
                    ptr->next_command != ACT_CMD &&
                    ptr->operation_type == channel_fs_data[channel].command_order->write &&
                    ptr->dram_addr.actual_address == channel_fs_data[channel].command_order->addr){
                    
                    assert(ptr->activation_cycle == CYCLE_VAL - T_RCD);
                    assert(ptr->next_command != PRE_CMD); //we should never need to issue a precharge as it is close page
                    assert(len_if_cmd(channel) <= 3);

                    opt_queue_t *opt = channel_fs_data[channel].command_order;
                    LL_DELETE(channel_fs_data[channel].command_order, opt);
                    free(opt);
                    
                    recent_colacc[channel][ptr->dram_addr.rank][ptr->dram_addr.bank] = 1;
                    issue_request_command(ptr);
                    break;
                    }
                }
            } else {
                LL_FOREACH(domain_write_queues[channel][channel_fs_data[channel].command_order->domain_id], ptr){
                    if (ptr->command_issuable && 
                    ptr->next_command != ACT_CMD &&
                    ptr->operation_type == channel_fs_data[channel].command_order->write &&
                    ptr->dram_addr.actual_address == channel_fs_data[channel].command_order->addr){
                    assert(ptr->activation_cycle == CYCLE_VAL - T_RCD);
                    assert(ptr->next_command != PRE_CMD); //we should never need to issue a precharge as it is close page
                    assert(len_if_cmd(channel) <= 3);

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
    channel_fs_data[channel].first_read_sent = first_read_sent;
    channel_fs_data[channel].second_read_sent = second_read_sent;
    channel_fs_data[channel].request_sent = reqeust_sent;
    channel_fs_data[channel].reads_sent = read_sent;
    channel_fs_data[channel].writes_sent = write_sent;
        if(current_turn_time >= 13){
            if(second_read_sent)
                second_used++;
            channel_fs_data[channel].current_turn_time = 0;
            channel_fs_data[channel].domain_turn = (domain_turn + 1) % DOMAIN_COUNT;
            channel_fs_data[channel].turn_counter = (turn_counter + 1) % ALTERATION;
            channel_fs_data[channel].rank_used = -1;
            channel_fs_data[channel].type_sent = -1;
            channel_fs_data[channel].request_sent = 0;
            channel_fs_data[channel].first_read_sent = 0;
            channel_fs_data[channel].second_read_sent = 0;
            
            if (channel_fs_data[channel].reads_sent && channel_fs_data[channel].writes_sent){
                both_types_sent++;
            } else if (channel_fs_data[channel].reads_sent >= 1) {
                reads_sent += 1;
            } else if (channel_fs_data[channel].writes_sent >= 1) {
                writes_sent += 1;
            }

            channel_fs_data[channel].reads_sent = 0;
            channel_fs_data[channel].writes_sent = 0;

            //how many requests were sent
            if(reqeust_sent == 0){
                total_request_sent[0] += 1;
            } else if(reqeust_sent == 1){
                total_request_sent[1] += 1;
            } else if(reqeust_sent == 2){
                total_request_sent[2] += 1;
            }
        } else {
            channel_fs_data[channel].current_turn_time++;
        }
  
}

void scheduler_stats() {
  /* Nothing to print for now. */
  printf("Number of aggressive precharges: %lld\n", num_aggr_precharge);
  printf("Number of second used: %d\n", second_used);
  printf("Number of request sent: 0: %d, 1: %d, 2:%d\n", total_request_sent[0], total_request_sent[1], total_request_sent[2]);
    printf("Number of both types sent: %d\n", both_types_sent);
    printf("Number of only reads sent: %d\n", reads_sent);
    printf("Number of only writes sent: %d\n", writes_sent);
}
