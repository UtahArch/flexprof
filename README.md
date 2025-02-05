# ASPLOS Artifact :
The most computainally expensive part of running this simulation is performing the profiling stage. 
Depening on your system it can take anywhere between 1 to 3 days. Using a 32Gb system with an Intel i7-13700k, profiling took 20 hours.
As we show in our paper, only a select programs benifit from profiling as such we provide a path assuming profiling has been done. 
Using the no_profile script can be used in case of time or system constraints.
We also provide the ability to perform the profiling from scatch.

Before the name FlexProf, we internally used the acronym "rwopt" (Read Write OPTimization); if this is seen anywhere in the code, it is synonymous with FlexProf. Additonally there are many mentions of "rta" this is synonymous with secured "rqa" as mentioned in the paper. We do not implement base rta as it is insecure.

If you have a decent cpu, we recommend opening `run.py` and modifying line 38, `max_processes = 20` to how every many threads you can spare.

### Requirements:
1. `gcc12`
2. `python 3.12`
3. `git`
4. `pip install -r requirements.txt`
### Compiling:
`cd src`\
`make all`\
`cd ..`
### Running USIMM:
As this is a traced based, cycle accurate simulation the results should be exactly the same.  

#### Profiling:
Skip this if you want to use the preprofiled version.
1. run `./one_script.sh` (you may need to give it execute permissions `chmod +x one_script.sh`) (this will take upwards of 1-3 days to finish, it is not "stuck")
2. Once complete, a handful of figures will appear in the root directory. No need to run the no-profiling script.
#### No-Profiling:
1. run `./no_profile_one_script.sh` (you may need to give it execute permissions `chmod +x no_profile_one_script.sh`) (this will take upwards of 1 day to finish, it is not "stuck")
2. This will only work if:
   1. You have not ran `one_script.sh`, as it overrides the provided profiled data.
   2. You have ran `one_script.sh`, but let it finish profiling.
   3. If you have ran `one_script.sh` and did not let the profiling finish and do not want to profile, you must redownload the repo and start over.


#### Mixed Benchmakrs:
We assume all programs are already profiled by the time we get here
1. run `./two_script.sh` (you may need to give it execute permissions `chmod +x two_script.sh`)

### Running Z3
We encourage users too look into the source code to view the equations being evaluated

`cd z3`\
`python3 sevengap.py` This evaluates the gap needed going from a write to read\
`python3 sixgap.py` This evaluates the gap needed for everything else



