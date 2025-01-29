import os
import numpy as np
from matplotlib.ticker import FuncFormatter
import matplotlib.pyplot as plt
from fractions import Fraction

class bm_struct:
    def __init__(self, name):
        self.name = name
        self.true_ratio = 0
        self.best_ratio = 0
        self.avg_gap_btw_reqs = 0

# Get benchmark directories
bms = [d for d in os.listdir("output/profile") if os.path.isdir(os.path.join("output/profile", d))]
bms = [bm_struct(bm) for bm in bms]
bms_sorted_by_request_intensity = []
# Calculate true ratio of 'W's to 'R's
for bm in bms:
    with open(f"input/domains/{bm.name}/core_0-2", 'r') as f:
        content = f.read()
        w = content.count('W')
        r = content.count('R')
        bm.true_ratio = w / (r + w) if (r + w) > 0 else 0
        #get average gap between requests, each line split [0] is the cycle gap before the last request
        gaps = [int(line.split()[0]) for line in content.split("\n") if line]
        bm.avg_gap_btw_reqs = sum(gaps) / len(gaps) if gaps else 0

# Get the best ratio which supplied lowest cycles
for bm in bms:
    try:
        std_outs = [file for file in os.listdir(f"output/profile/{bm.name}") if os.path.isfile(os.path.join(f"output/profile/{bm.name}", file))]
        std_outs = [f"output/profile/{bm.name}/{file}" for file in std_outs]
        performance = []
        for file in std_outs:
            with open(file, "r") as f:
                for line in f:
                    if "Total Simulation Cycles" in line:
                        performance.append((file, int(line.split()[3])))
                        break
        performance.sort(key=lambda x: x[1])
        if performance:
            bm.best_ratio = performance[0][0].split("_")[-1].split(".")[0] + "/" + performance[0][0].split("_")[-1].split(".")[1]
    except:
        print(f"Error processing {bm.name}")

bms = sorted(bms, key=lambda x: x.avg_gap_btw_reqs)
#print best ratios
for bm in bms:
    print(f"{bm.name} {bm.best_ratio}")
    
labels = [bm.name for bm in bms]
true_ratios = [bm.true_ratio for bm in bms]
best_ratios = [float(bm.best_ratio.split('/')[0]) / float(bm.best_ratio.split('/')[1]) if bm.best_ratio != 0 else 0 for bm in bms]

x = np.arange(len(labels))
fig, ax = plt.subplots(figsize=(10, 6))


ax.scatter(x, true_ratios, label='Write Ratio', color='#fb6f92', s=300, zorder=3, marker='o', linewidths=2)
ax.scatter(x, best_ratios, label='Write-Mode Usage', color='#448EE4', s=300, zorder=3, marker='x', linewidths=2)

# Function to format the tick labels as fractions, x/100
def as_fraction(x, pos):
    frac = Fraction(x).limit_denominator(100)
    return str(frac)

formatter = FuncFormatter(as_fraction)
plt.gca().yaxis.set_major_formatter(formatter)
plt.yticks(fontsize=21, rotation=45)

ax.set_ylabel('Ratio', fontsize=21)
ax.set_xlabel('Benchmarks', fontsize=21)
ax.set_title('Program Read Write Ratio vs Needed Write-Mode Usage', fontsize=21)
ax.set_xticks(x)
ax.set_xticklabels(labels, rotation=45, ha='right', fontsize=21)
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'{x:.0%}'))

# Place the legend above the plot
ax.legend(fontsize=21, loc='lower center', bbox_to_anchor=(0.5, 1.15), ncol=3)

plt.grid(True)

# Adjust layout to make space for the legend
plt.subplots_adjust(top=0.85)

plt.savefig("fig5.png", dpi=500, format="png", bbox_inches='tight')
