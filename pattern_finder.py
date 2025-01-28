from sys import argv
from itertools import cycle
'''
to run: python3 pattern_finder.py domain1_ratio domain2_ratio domain3_ratio outputfile ...
example: python3 pattern_finder.py 1/5 2/5 2/5 1/5 out.txt
'''
R = 0
W = 1
if(len(argv) < 4):
    print("to run: python3 pattern_finder.py domain1_ratio domain2_ratio domain3_ratio outputfile banks ...\nexample: python3 pattern_finder.py 1/5 2/5 2/5 1/5 out.txt")
    exit(1)
fractions = []
for i in range(1, len(argv)-2):
    fractions.append(argv[i])

domains = []
try:
    for f in fractions:
        domains.append([W if x < int(f.split("/")[0]) else R for x in range(0, int(f.split("/")[1]))])
except:
    print("Invalid fractions")
    print(fractions)
    exit(1)

banks = [x for x in range(int(argv[-1]))]

def initialize_banks(num_banks, num_slots):
    return {bank: {slot: 0 for slot in range(num_slots)} for bank in range(num_banks)}

banks_read = initialize_banks(len(banks), len(domains))
banks_write = initialize_banks(len(banks), len(domains))

def pretty_print(path):
    for point in path:
        domain, operation, bank = point
        print(f"Domain {domain} {'W' if operation == 1 else 'R'} -> Bank {bank}")


def fin_r():
    for bank in banks:
        for domain in range(len(domains)):
            if banks_read[bank][domain] < len([x for x in domains[domain] if x == R]):
                return False
    return True

def fin_w():
    for bank in banks:
        for domain in range(len(domains)):
            if banks_write[bank][domain] < len([x for x in domains[domain] if x == W]):
                return False
    return True

def find_path_at_once():
    reads = []
    writes = []
    path = []
    pointer = 0
    starter = 0
    try_read = True
    bank = 0
    while not (fin_r() and fin_w()):
        if(try_read):
            if banks_read[bank][pointer] < len([x for x in domains[pointer] if x == R]):
                path.append((pointer, R, bank))
                banks_read[bank][pointer] += 1
                bank = (bank + 1) % len(banks)
            elif banks_write[bank][pointer] < len([x for x in domains[pointer] if x == W]):
                path.append((pointer, W, bank))
                banks_write[bank][pointer] += 1
                bank = (bank + 1) % len(banks)
            pointer = (pointer + 1) % len(domains)
            # if(pointer == starter and bank == 0):
            #     pointer = (pointer + 1) % len(domains)
            #     starter = pointer
        else:
            if banks_write[bank][pointer] < len([x for x in domains[pointer] if x == W]):
                path.append((pointer, W, bank))
                banks_write[bank][pointer] += 1
                bank = (bank + 1) % len(banks)
            elif banks_read[bank][pointer] < len([x for x in domains[pointer] if x == R]):
                path.append((pointer, R, bank))
                banks_read[bank][pointer] += 1
                bank = (bank + 1) % len(banks)
            pointer = (pointer + 1) % len(domains)
            # if(pointer == starter and bank == 0):
            #     pointer = (pointer + 1) % len(domains)
            #     starter = pointer
        if pointer == 0:
            try_read = not try_read

    return path

  

def format_print(path):
    string = ""
    for p in path:
        # for point in p:
        domain, operation, bank = p
        string += f"{domain} {operation} {bank}\n"
    with open(argv[-2], "w") as f:
        f.write(string)


path = find_path_at_once()

    

format_print(path)
