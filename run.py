import time
import os
import subprocess
from sys import argv
# Define the lists of fractions and benchmarks
fractions_list = []

benchmarks = [d for d in os.listdir("output/profile/") if os.path.isdir(os.path.join("input/domains", d))]
banks = [4]
domains =  7
try:
    input_file = argv[1]
    output_folder = argv[2]
except IndexError:
    print("Usage: python3 run.py <input_file> <output_folder>")
    exit(1)

#create the output folder if it does not exist
if not os.path.exists(output_folder):
    os.makedirs(output_folder)
    

for bm in benchmarks:
    performance = []
    std_outs = [file for file in os.listdir(f"output/profile/{bm}") if os.path.isfile(os.path.join(f"output/profile/{bm}", file))]
    std_outs = [f"output/profile/{bm}/{file}" for file in std_outs]
    for file in std_outs:
        with open(file, "r") as f:
            for line in f:
                if "Total Simulation Cycles" in line:
                    performance.append((file, int(line.split()[3])))
                    break
    performance.sort(key=lambda x: x[1])
    best = performance[0]

    fractions_list.append((bm, f"{best[0].split('_')[1].split('.')[0]}/100"))

max_processes = 20
def wait_for_available_slot(processes, max_processes):
    while len(processes) >= max_processes:
        for p in processes.copy():
            if p.poll() is not None:  # Process has finished
                processes.remove(p)
        time.sleep(1)  # Wait a bit before checking again
processes = []

for fractions in fractions_list:
    benchmark = fractions[0]
    fractions_str = (fractions[1] + " ") * domains

   #Start the first set of commands
    cmd1 = f"python3 pattern_finder.py {fractions_str} input/patterns/{benchmark}.8pattern {banks[0]}"
    processes.append(subprocess.Popen(cmd1, shell=True))
    time.sleep(2) 
    cmd2 = (f"bin/usimm-fsbta-rwopt {input_file} "
            f"input/domains/{benchmark}/core_0-2 input/domains/{benchmark}/core_1-2 "
            f"input/domains/{benchmark}/core_2-2 input/domains/{benchmark}/core_3-2 "
            f"input/domains/{benchmark}/core_4-2 input/domains/{benchmark}/core_5-2 "
            f"input/domains/{benchmark}/core_6-2 "
            f"input/patterns/{benchmark}.8pattern > {output_folder}/rwopt-{benchmark}")
    processes.append(subprocess.Popen(cmd2, shell=True))
    wait_for_available_slot(processes, max_processes)
    # Start the second set of commands
    cmd5 = (f"bin/usimm-fsbta {input_file} "
            f"input/domains/{benchmark}/core_0-2 input/domains/{benchmark}/core_1-2 "
            f"input/domains/{benchmark}/core_2-2 input/domains/{benchmark}/core_3-2 "
            f"input/domains/{benchmark}/core_4-2 input/domains/{benchmark}/core_5-2 "
            f"input/domains/{benchmark}/core_6-2 "
            f"> {output_folder}/fsbta-{benchmark}")
    processes.append(subprocess.Popen(cmd5, shell=True))
    wait_for_available_slot(processes, max_processes)
    cmd6 = (f"bin/usimm-rta {input_file} "
            f"input/domains/{benchmark}/core_0-2 input/domains/{benchmark}/core_1-2 "
            f"input/domains/{benchmark}/core_2-2 input/domains/{benchmark}/core_3-2 "
            f"input/domains/{benchmark}/core_4-2 input/domains/{benchmark}/core_5-2 "
            f"input/domains/{benchmark}/core_6-2 "
            f"> {output_folder}/rta-{benchmark}")
    processes.append(subprocess.Popen(cmd6, shell=True))
    wait_for_available_slot(processes, max_processes)
    cmd7 = (f"bin/usimm {input_file} "
            f"input/domains/{benchmark}/core_0-2 input/domains/{benchmark}/core_1-2 "
            f"input/domains/{benchmark}/core_2-2 input/domains/{benchmark}/core_3-2 "
            f"input/domains/{benchmark}/core_4-2 input/domains/{benchmark}/core_5-2 "
            f"input/domains/{benchmark}/core_6-2 "
            f"> {output_folder}/base-{benchmark}")
    processes.append(subprocess.Popen(cmd7, shell=True))
    wait_for_available_slot(processes, max_processes)

# Wait for all processes to complete
for p in processes:
    p.wait()

