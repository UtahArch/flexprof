
import matplotlib.pyplot as plt
import numpy as np
import os
from math import trunc

dir = "output/7domains_8banks_8ranks_addressmapping2"
bm = [x for x in os.listdir(dir) if x.startswith("base-")]
bm = [x.split("-")[1] for x in bm]
ratio = []
avg_gap_btw_reqs = []

for bm_name in bm:
    with open(f"input/domains/{bm_name}/core_1-2", 'r') as f:
        content = f.read()
        gaps = [int(line.split()[0]) for line in content.split("\n") if line]
        avg_gap_btw_reqs.append(( bm_name,sum(gaps) / len(gaps) if gaps else 0))

avg_gap_btw_reqs.sort(key=lambda x: x[1])
bm = [x[0] for x in avg_gap_btw_reqs]

bms = []

for bm_name in bm:
    bms.append([bm_name])
    baseline = f"{dir}/base-{bm_name}"
    opt = f"{dir}/rwopt-{bm_name}"
    fsb = f"{dir}/fsbta-{bm_name}"
    rta = f"{dir}/rta-{bm_name}"
    #opt_b = f"output/4domains_16banks_8ranks/rwopt-{bm_name}-backup"

    #find line Total Simulation Cycles and grab the number of cycles
    base_read_latency = 1
    with open(f"{baseline}", "r") as f:
        reads_served = 0
        writes_served = 0
        for line in f:
            if "Total Reads Serviced" in line:
                reads_served = int(float(line.split()[-1]))
                continue
            if "Total Writes Serviced" in line:
                writes_served = int(float(line.split()[-1]))
                continue
            if "Average Read Latency" in line:
                base_read_latency = int(float(line.split()[-1]))
                continue
            if "Average Write Latency" in line:
                base_write_latency = int(float(line.split()[-1]))
                avg = ((reads_served * base_read_latency) + (writes_served* base_write_latency)) / (reads_served + writes_served)
                bms[-1].append(avg)
    
        # Process opt latency
    with open(f"{opt}", "r") as f:
        reads_served = 0
        writes_served = 0
        opt_read_latency = 0
        opt_write_latency = 0
        for line in f:
            if "Total Reads Serviced" in line:
                reads_served = int(float(line.split()[-1]))
                continue
            if "Total Writes Serviced" in line:
                writes_served = int(float(line.split()[-1]))
                continue
            if "Average Read Latency" in line:
                opt_read_latency = int(float(line.split()[-1]))
                continue
            if "Average Write Latency" in line:
                opt_write_latency = int(float(line.split()[-1]))
                avg = ((reads_served * opt_read_latency) + (writes_served * opt_write_latency)) / (reads_served + writes_served)
                bms[-1].append(avg)

    # Process rta latency
    with open(f"{rta}", "r") as f:
        reads_served = 0
        writes_served = 0
        rta_read_latency = 0
        rta_write_latency = 0
        for line in f:
            if "Total Reads Serviced" in line:
                reads_served = int(float(line.split()[-1]))
                continue
            if "Total Writes Serviced" in line:
                writes_served = int(float(line.split()[-1]))
                continue
            if "Average Read Latency" in line:
                rta_read_latency = int(float(line.split()[-1]))
                continue
            if "Average Write Latency" in line:
                rta_write_latency = int(float(line.split()[-1]))
                avg = ((reads_served * rta_read_latency) + (writes_served * rta_write_latency)) / (reads_served + writes_served)
                bms[-1].append(avg)

    # Process fsb latency
    with open(f"{fsb}", "r") as f:
        reads_served = 0
        writes_served = 0
        fsb_read_latency = 0
        fsb_write_latency = 0
        for line in f:
            if "Total Reads Serviced" in line:
                reads_served = int(float(line.split()[-1]))
                continue
            if "Total Writes Serviced" in line:
                writes_served = int(float(line.split()[-1]))
                continue
            if "Average Read Latency" in line:
                fsb_read_latency = int(float(line.split()[-1]))
                continue
            if "Average Write Latency" in line:
                fsb_write_latency = int(float(line.split()[-1]))
                avg = ((reads_served * fsb_read_latency) + (writes_served * fsb_write_latency)) / (reads_served + writes_served)
                bms[-1].append(avg)

# Assuming bms is your benchmark data
bms = np.array(bms)

# Extracting benchmarks and latencies
benchmarks = bms[:, 0]
base_latency = bms[:, 1].astype(float)
opt_latencies = bms[:, 2].astype(float)
rta_latencies = bms[:, 3].astype(float)

# Calculating percentage increase compared to the base latency
opt_percentage_increase = opt_latencies
rta_percentage_increase = rta_latencies

# Set up the plot
index = np.arange(len(benchmarks))
bar_width = 0.3

fig, ax = plt.subplots()

# Bar plot showing the percentage increase for FlexProf and RQA latencies
bars_opt = ax.bar(index - bar_width / 2, opt_percentage_increase, bar_width, label='FlexProf Latency')
bars_rta = ax.bar(index + bar_width / 2, rta_percentage_increase, bar_width, label='RQA Latency')

# Update axis labels
ax.set_xlabel('Benchmark', fontsize=14)
ax.set_ylabel('Cycles', fontsize=14)
ax.set_title('Average Latency Comparison', fontsize=14)
ax.set_xticks(index)
ax.set_xticklabels(benchmarks, fontsize=14)
ax.legend()

# Grid and formatting
plt.grid(which='major', axis='y', color='gray', linestyle='--', linewidth=0.5)
plt.xticks(rotation=90)
plt.tight_layout()

# Show plot
plt.savefig("fig8.png")