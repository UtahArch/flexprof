#!/bin/bash


configs=("input/7domains_8banks_8ranks_addressmapping2.cfg")
output=("output/7domains_8banks_8ranks_addressmapping2") 


i=0
for config in "${configs[@]}"
do
    python3 run.py "$config" "${output[$i]}"
    python3 stats.py > fig4.stats
    python3 graphs.py fig4.stats #fig 7
    python3 util_graph.py #fig 2
    python3 whats_sent_graph.py #fig 3
    python3 true_ratio_best_ratio_graph.py #fig 5
    python3 response_graph.py #fig 8
    i=$((i+1))
done
