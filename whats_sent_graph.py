

output_dir = "output/7domains_8banks_8ranks_addressmapping2"
import os
bm = [x for x in os.listdir(output_dir) if x.startswith("rta-")]
bm = [x.split("-")[1] for x in bm]

bm_stats = {}
for bm_name in bm:
    rta_out = f"{output_dir}/rta-{bm_name}"
    with open(rta_out, 'r') as f:
        both = 0
        reads = 0
        writes = 0
        total_sim_cycles = 0

        total_requests = 0
        for line in f:
            if "Number of both types sent:" in line:
                both = int(line.split(":")[1])
            if "Number of only reads sent:" in line:
                reads = int(line.split(":")[1])
            if "Number of only writes sent:" in line:
                writes = int(line.split(":")[1])
            if "Total Simulation Cycles" in line:
                total_sim_cycles = int(line.split()[3])
                break
        try:
            total = both + reads + writes
            bm_stats[bm_name] = (both/total, reads/total, writes/total, total_sim_cycles)
        except:
            continue


import matplotlib.pyplot as plt
import numpy as np


bm_stats = {k: v for k, v in sorted(bm_stats.items(), key=lambda item: item[1][3])}
labels = list(bm_stats.keys())
ind = np.arange(len(bm_stats))
both = [x[0] for x in bm_stats.values()]
reads = [x[1] for x in bm_stats.values()]
writes = [x[2] for x in bm_stats.values()]
total_requests = [x[3] for x in bm_stats.values()]

#stacked bar plot
p1 = plt.bar(ind, both, color='#a1c181')
p2 = plt.bar(ind, reads, color='#619b8a', bottom=both)
p3 = plt.bar(ind, writes, color='#233d4d', bottom=np.array(both)+np.array(reads))

plt.ylabel('Percentage of Turns', fontsize=16)
plt.title('Requests Sent by Type', fontsize=16)
plt.xticks(ind, labels, rotation=90, fontsize=16)
plt.yticks(np.arange(0, 1.1, 0.2))
plt.gca().set_yticklabels(['{:.0f}%'.format(x*100) for x in plt.gca().get_yticks()], fontsize=16)
plt.legend((p3[0], p2[0], p1[0]), ('Writes', 'Reads', 'Both'), fontsize=16)


plt.tight_layout()
plt.savefig(f"fig3.png")