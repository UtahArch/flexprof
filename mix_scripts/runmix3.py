import time
import os
import subprocess
from sys import argv

os.chdir("../")
# Define the lists of fractions and benchmarks
fractions_list = []

benchmarks = [d for d in os.listdir("output/profile/") if os.path.isdir(os.path.join("input/domains", d))]
banks = [4]
domains =  7
try:
    input_file = argv[1]
    output_folder = argv[2]
except IndexError:
    print("Usage: python3 run.py <config_file> <output_folder>")
    exit(1)

#create the output folder if it does not exist
if not os.path.exists(output_folder):
    os.makedirs(output_folder)
    

max_processes = 20
def wait_for_available_slot(processes, max_processes):
    while len(processes) >= max_processes:
        for p in processes.copy():
            if p.poll() is not None:  # Process has finished
                processes.remove(p)
        time.sleep(1)  # Wait a bit before checking again
processes = []


#Start the first set of commands
#['cactuBSSN', 'xalanc', 'omnetpp', 'bwaves', 'ua', 'cg', 'mcf']
cmd1 = f"python3 pattern_finder.py 7/100 0/100 5/100 0/100 0/100 0/100 0/100 input/patterns/runmix3.8pattern {banks[0]}"
processes.append(subprocess.Popen(cmd1, shell=True))
time.sleep(2) 
cmd2 = (f"bin/usimm-fsbta-rwopt {input_file} "
        f"input/mix3/cactuBSSN0 input/mix3/xalanc1 "
        f"input/mix3/omnetpp2 input/mix3/bwaves3 "
        f"input/mix3/ua4 input/mix3/cg5 "
        f"input/mix3/mcf6 "
        f"input/patterns/runmix3.8pattern > {output_folder}/rwopt-runmix3")
processes.append(subprocess.Popen(cmd2, shell=True))
wait_for_available_slot(processes, max_processes)
# Start the second set of commands
cmd5 = (f"bin/usimm-fsbta {input_file} "
        f"input/mix3/cactuBSSN0 input/mix3/xalanc1 "
        f"input/mix3/omnetpp2 input/mix3/bwaves3 "
        f"input/mix3/ua4 input/mix3/cg5 "
        f"input/mix3/mcf6 "
        f"> {output_folder}/fsbta-runmix3")
processes.append(subprocess.Popen(cmd5, shell=True))
wait_for_available_slot(processes, max_processes)
cmd6 = (f"bin/usimm-rta {input_file} "
        f"input/mix3/cactuBSSN0 input/mix3/xalanc1 "
        f"input/mix3/omnetpp2 input/mix3/bwaves3 "
        f"input/mix3/ua4 input/mix3/cg5 "
        f"input/mix3/mcf6 "
        f"> {output_folder}/rta-runmix3")
processes.append(subprocess.Popen(cmd6, shell=True))
wait_for_available_slot(processes, max_processes)
cmd7 = (f"bin/usimm {input_file} "
        f"input/mix3/cactuBSSN0 input/mix3/xalanc1 "
        f"input/mix3/omnetpp2 input/mix3/bwaves3 "
        f"input/mix3/ua4 input/mix3/cg5 "
        f"input/mix3/mcf6 "
        f"> {output_folder}/base-runmix3")
processes.append(subprocess.Popen(cmd7, shell=True))
wait_for_available_slot(processes, max_processes)

# Wait for all processes to complete
for p in processes:
    p.wait()

