#!/bin/bash


configs=("input/7domains_8banks_8ranks_addressmapping2.cfg")
output=("output/7domains_8banks_8ranks_addressmapping2") 


i=0
for config in "${configs[@]}"
do
    python3 ratio_profiler.py input/domains/lbm/core_0-2 4 lbm "$config"

    python3 ratio_profiler.py input/domains/namd/core_0-2 4 namd "$config"
    python3 ratio_profiler.py input/domains/perl/core_0-2 4 perl "$config"
    python3 ratio_profiler.py input/domains/xalanc/core_0-2 4 xalanc "$config"
    python3 ratio_profiler.py input/domains/bwaves/core_0-2 4 bwaves "$config"
    python3 ratio_profiler.py input/domains/cactuBSSN/core_0-2 4 cactuBSSN "$config"

    python3 ratio_profiler.py input/domains/cam4/core_0-2 4 cam4 "$config"
    python3 ratio_profiler.py input/domains/deepsjeng/core_0-2 4 deepsjeng "$config"

    python3 ratio_profiler.py input/domains/fotonik3d/core_0-2 4 fotonik3d "$config"
    python3 ratio_profiler.py input/domains/mcf/core_0-2 4 mcf "$config"
    python3 ratio_profiler.py input/domains/gcc/core_0-2 4 gcc "$config"
    python3 ratio_profiler.py input/domains/roms/core_0-2 4 roms "$config"

    python3 ratio_profiler.py input/domains/omnetpp/core_1-2 4 omnetpp "$config"

    # NPB
    python3 ratio_profiler.py input/domains/bt/core_0-2 4 bt "$config"
    python3 ratio_profiler.py input/domains/dc/core_0-2 4 dc "$config"
    python3 ratio_profiler.py input/domains/ep/core_0-2 4 ep "$config"
    python3 ratio_profiler.py input/domains/ft/core_0-2 4 ft "$config"
    python3 ratio_profiler.py input/domains/is/core_0-2 4 is "$config"

    python3 ratio_profiler.py input/domains/lu/core_0-2 4 lu "$config"
    
    python3 ratio_profiler.py input/domains/mg/core_0-2 4 mg "$config"
    python3 ratio_profiler.py input/domains/sp/core_0-2 4 sp "$config"
    python3 ratio_profiler.py input/domains/ua/core_0-2 4 ua "$config"
    python3 ratio_profiler.py input/domains/cg/core_0-2 4 cg "$config"


    python3 run.py "$config" "${output[$i]}"
    python3 stats.py > fig7.stats
    python3 graphs.py fig7.stats #fig 7
    python3 util_graph.py #fig 2
    python3 whats_sent_graph.py #fig 3
    python3 true_ratio_best_ratio_graph.py #fig 5
    python3 response_graph.py #fig 8
    i=$((i+1))
done
