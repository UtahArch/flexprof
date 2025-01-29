#ifndef __SCHEDULER_H__
#define __SCHEDULER_H__
//Called RTA but this is RQA. We do not have an implementation of RTA as it is insecure.

void init_scheduler_vars(); // called from main
void scheduler_stats();     // called from main
void schedule(int);         // scheduler function called every cycle

#endif //__SCHEDULER_H__
