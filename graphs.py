import matplotlib.pyplot as plt
import numpy as np

def read_data(filename):
    with open (filename, 'r') as f:
        lines = f.readlines()
        data = {}
        grouped = [lines[i:i+14] for i in range(0, len(lines), 14)]
        for group in grouped:
            benchmark = group[0].split(":")[0]
            data[benchmark] = {}
            data[benchmark]['performance_baseline']= {
                'FlexProf': float(group[1].strip().split("=")[1]),
                'fsbta': float(group[3].strip().split("=")[1]),
                'rta': float(group[4].strip().split("=")[1])
            }
    return data

gmeans = {
    'FlexProf': 0.0,
    'fsbta': 0.0,
    'rta': 0.0
}

from sys import argv
if len(argv) < 2:
    filename = argv[2]
else:
    filename = argv[1]

data = read_data(filename)

benchmarks = list(data.keys())
performance_rwopt_7 = [data[b]['performance_baseline']['FlexProf'] for b in benchmarks]
performance_rta = [data[b]['performance_baseline']['rta'] for b in benchmarks]
performance_fsbta = [data[b]['performance_baseline']['fsbta'] for b in benchmarks]

x = np.arange(len(benchmarks)) 
width = 0.2  

fig, ax1 = plt.subplots()

colors_FlexProf = '#fb9062'
colors_rta = '#ce4993'    
colors_fsbta = '#6a0d83' 
colors = plt.colormaps['tab10']
rects1 = ax1.bar(x, performance_rwopt_7, width, label='FlexProf', color=colors(0))
rects3 = ax1.bar(x + width, performance_rta, width, label='RQA', color=colors(1))
rects4 = ax1.bar(x + 2 * width, performance_fsbta, width, label='FS-BTA', color=colors(2))

ax1.set_xlabel('Benchmarks')
ax1.set_ylabel('Performance from Baseline')
ax1.set_xticks(x)
ax1.set_xticklabels(benchmarks, rotation=60)
ax1.legend()

plt.grid(which='major', axis='y', color='gray', linestyle='--', linewidth=0.5)
plt.ylim(0, 1.0)

fig.set_size_inches(18.5, 10.5)

for k in gmeans.keys():
    gmeans[k] = 1

for b in benchmarks:
    for k in gmeans.keys():
        gmeans[k] *= data[b]['performance_baseline'][k]  # Multiply the values

import math
for k in gmeans.keys():
    gmeans[k] = math.pow(gmeans[k], 1 / len(benchmarks))

# Add a final gmean line
ax1.axhline(y=gmeans['FlexProf'], color=colors(0), linestyle='--', label='GMEAN FlexProf')
ax1.axhline(y=gmeans['rta'], color=colors(1), linestyle='--', label='GMEAN RQA')
ax1.axhline(y=gmeans['fsbta'], color=colors(2), linestyle='--', label='GMEAN FS-BTA')

fig.set_size_inches(16.5, 5)

plt.xticks(fontsize=18)
plt.yticks(fontsize=18)
plt.legend(fontsize=18)
plt.ylabel('Slowdown', fontsize=18, labelpad=10)
plt.xlabel('Benchmarks', fontsize=18)

plt.title("Performance Normalized Against The Non-Secure Baseline (Higher is Better)", fontsize=18, pad=12)
plt.legend(loc='center left', bbox_to_anchor=(1, 0.5), fontsize=18)

plt.tight_layout()
plt.savefig("fig7.png")

