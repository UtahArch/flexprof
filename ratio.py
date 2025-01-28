import os
bms = [d for d in os.listdir("input/domains") if os.path.isdir(os.path.join("input/domains", d))]

for bm in bms:
    for i in range(8):
        with open(f"input/domains/{bm}/core_{i}-2", 'r') as f:
            #Tell me how many 'W's and 'R's are in the file
            w = 0
            r = 0
            count = 0
            lines = f.readlines()
            for line in lines:
                w += line.count('W')
                r += line.count('R')

            #Print the ratio of 'W's to 'R's
            print(f"{i}: {bm}  {w/(r+w)}")