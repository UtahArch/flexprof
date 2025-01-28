dir = "output/7domains_8banks_8ranks_addressmapping2"
import os
bm = [x for x in os.listdir(dir) if x.startswith("rwopt-")]
bm = [x.split("-")[1] for x in bm]
avg_gap_btw_reqs = []

for bm_name in bm:
    with open(f"input/domains/{bm_name}/core_1-2", 'r') as f:
        content = f.read()
        gaps = [int(line.split()[0]) for line in content.split("\n") if line]
        avg_gap_btw_reqs.append(( bm_name,sum(gaps) / len(gaps) if gaps else 0))

avg_gap_btw_reqs.sort(key=lambda x: x[1])
bm = [x[0] for x in avg_gap_btw_reqs]

for bm_name in bm:
    baseline = f"{dir}/base-{bm_name}"
    opt = f"{dir}/rwopt-{bm_name}"
    fsb = f"{dir}/fsbta-{bm_name}"
    rta = f"{dir}/rta-{bm_name}"

    #find line Total Simulation Cycles and grab the number of cycles
    base_cycles = 1
    with open(f"{baseline}", "r") as f:
        for line in f:
            if "Total Simulation Cycles" in line:
                base_cycles = int(line.split()[3])
                break
    opt_cycles = 1
    with open(f"{opt}", "r") as f:
        for line in f:
            if "Total Simulation Cycles" in line:
                opt_cycles = int(line.split()[3])
                break
    
    fsb_cycles = 1
    with open(f"{fsb}", "r") as f:
        for line in f:
            if "Total Simulation Cycles" in line:
                fsb_cycles = int(line.split()[3])
                break

    rta_cycles = 1
    with open(f"{rta}", "r") as f:
        for line in f:
            if "Total Simulation Cycles" in line:
                rta_cycles = int(line.split()[3])
                break
    

    print(f"{bm_name}:")
    print(f"FlexProf performance from baseline  = {base_cycles/opt_cycles:.2f}")
    print(f"....")
    print(f"fsbta performance from baseline              = {base_cycles/fsb_cycles:.2f}")
    print(f"rta performance from baseline                = {base_cycles/rta_cycles:.2f}")    
    print(f"FlexProf speedup from fsbta               = {fsb_cycles/opt_cycles:.2f}")
    print(f"FlexProf speedup from rta                 = {rta_cycles/opt_cycles:.2f}")
    print(f"FlexProf speedup from rwopt_10_gap_alt4   = {opt_cycles/opt_cycles:.2f}")
    print("Cycle Completion")
    print(f"FlexProf cycle completion = {opt_cycles}")
    print(f"....")
    print(f"fsbta cycle completion             = {fsb_cycles}")
    print(f"rta cycle completion               = {rta_cycles}")
    print()
