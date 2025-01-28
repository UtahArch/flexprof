output_dir = "output/7domains_8banks_8ranks_addressmapping2"
import os
bm = [x for x in os.listdir(output_dir) if x.startswith("rta-")]
bm = [x.split("-")[1] for x in bm]

bm_stats = {}
for bm_name in bm:
    rta_out = f"{output_dir}/rta-{bm_name}"
    with open(rta_out, 'r') as f:
        total = 0
        zero_norm = 0
        one_norm = 0
        two_norm = 0

        total_requests = 0
        for line in f:
            if "Number of request sent" in line:
                #Number of request sent: 0: 1777334, 1: 612566, 2:43717
                zero_norm_t = int(line.split(",")[0].split(":")[-1])
                one_norm_t = int(line.split(",")[1].split(":")[1])
                two_norm_t = int(line.split(",")[2].split(":")[1])

                #normalize it
                total = zero_norm_t + one_norm_t + two_norm_t
                zero_norm = zero_norm_t / total
                one_norm = one_norm_t / total
                two_norm = two_norm_t / total

                total_requests = total

                #get intensity
                bm_stats[bm_name] = (zero_norm, one_norm, two_norm, total_requests)
                break
# rects1 = ax.bar(ind, zero_norm, width, color='#ef767a')
# rects2 = ax.bar(ind + width, one_norm, width, color='#456990')
# rects3 = ax.bar(ind + 2*width, two_norm, width, color='#49beaa')

import matplotlib.pyplot as plt
import numpy as np

#stacked bar plot

bm_stats = {k: v for k, v in sorted(bm_stats.items(), key=lambda item: item[1][3])}
labels = list(bm_stats.keys())
ind = np.arange(len(bm_stats))
zero_norm = [x[0] for x in bm_stats.values()]
one_norm = [x[1] for x in bm_stats.values()]
two_norm = [x[2] for x in bm_stats.values()]
total_requests = [x[3] for x in bm_stats.values()]

p1 = plt.bar(ind, zero_norm, color='#ef767a')
p2 = plt.bar(ind, one_norm, color='#456990', bottom=zero_norm)
p3 = plt.bar(ind, two_norm, color='#49beaa', bottom=np.array(zero_norm)+np.array(one_norm))

plt.ylabel('Percentage of Turns', fontsize=16)
plt.title('Average Request Sent Per Given Turn ', fontsize=16)
plt.xticks(ind, labels, rotation=90, fontsize=16)
plt.yticks(np.arange(0, 1.1, 0.2))
plt.gca().set_yticklabels(['{:.0f}%'.format(x*100) for x in plt.gca().get_yticks()], fontsize=16)
plt.legend((p3[0], p2[0], p1[0]), ('2 Sent', '1 Sent', '0 Sent'), fontsize=16)

plt.tight_layout()

plt.savefig("fig2.png", bbox_inches='tight')