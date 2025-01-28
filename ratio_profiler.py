from sys import argv
import subprocess
import threading
from concurrent.futures import ThreadPoolExecutor

python_script = "pattern_finder.py"

ratios = []
for i  in range(0, 50):
    ratios.append(f"{i}/100")

output_files = []

try:
    trace_file = argv[1]
    with open(trace_file, "r") as f:
        pass
except FileNotFoundError:
    print(f"File {trace_file} not found")
    print("Usage: python3 ratio_profiler.py <trace_file> banks output_folder input_file")
    exit(1)
except IndexError:
    print("Usage: python3 ratio_profiler.py <trace_file> banks output_folder input_file")
    exit(1)

banks = argv[2]

dummy = "input/dummy"

if len(argv) != 5:
    output_folder = "any"
else:
    output_folder = argv[3]

input_file = argv[4]

ratio = 0
for r in ratios:
    t = r.split("/")[0]
    b = r.split("/")[1]
    subprocess.run(["mkdir", "-p", f"profile/{output_folder}"])
    output_files.append(f"profile/{output_folder}/output_{t}.{b}.txt")
    subprocess.run(["python3", python_script, r, r, r, r, r, r, r, f"profile/{output_folder}/output_{t}.{b}.txt", banks])


std_outs = []
processes = []
lock = threading.Lock() 

def run_process(output_file):
    subprocess.run(["mkdir", "-p", f"output/profile/{output_folder}"])
    with open(f"output/{output_file}.stdout", "w") as f:
        p = subprocess.Popen(["bin/usimm-fsbta-rwopt", f"{input_file}", trace_file, dummy, dummy, dummy, dummy, dummy, dummy, output_file], stdout=f)
        with lock:
            processes.append(p)
        std_outs.append(f"output/{output_file}.stdout") 
        p.wait()

def monitor_processes():
    finished_processes = 0 
    while True:
        with lock:
            for p in processes.copy():  # Iterate over a copy of the list to safely modify the original list
                if p.poll() is not None: 
                    processes.remove(p) 
                    finished_processes += 1
                    if finished_processes == 50: 
                        for other_p in processes:  
                            other_p.kill()
                        return  

# Start the monitoring thread
monitoring_thread = threading.Thread(target=monitor_processes)
monitoring_thread.start()

# Run processes in parallel
with ThreadPoolExecutor() as executor:
    futures = [executor.submit(run_process, o) for o in output_files]
monitoring_thread.join()