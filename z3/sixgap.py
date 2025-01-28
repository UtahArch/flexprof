from z3 import *

#defining the variables
k = Int('k')
k_prime = Int('k_prime')
l = Int('l')
tCAS = Int('tCAS')
tRCD = Int('tRCD')
tCWD = Int('tCWD')
tBURST = Int('tBURST')
tRTRS = Int('tRTRS')
tRRD = Int('tRRD')
tFAW = Int('tFAW')
tWTR = Int('tWTR')
s = Optimize()

#set dram timings
s.add(tCAS == 11)
s.add(tRCD == 11)
s.add(tCWD == 5)
s.add(tBURST == 4)
s.add(tRTRS == 2)
s.add(tRRD == 5)
s.add(tFAW == 24)
s.add(tWTR == 6)

s.add(k > 0)
s.add(k_prime == k + 1) #the next data transfer
s.add(l >= tBURST + tRTRS)

s.add(((k*l) - tCAS) != ((k_prime * l) - tCWD)) #equation 1
s.add(((k*l) - tCWD) != ((k_prime * l) - tCWD - tRCD)) #equation 3
s.add(((k*l) - tCAS) != ((k_prime * l) - tCWD - tRCD)) #equation 5
s.add(((k*l) - tCAS) != ((k_prime * l) - tCAS - tRCD)) #equation 6
s.add(((k*l) - tCAS - tRCD) != ((k_prime * l) - tCWD - tRCD)) #equation 7
s.minimize(l)

if s.check() == sat:
    model = s.model()
    print(f"Minimum gap needed is {model.evaluate(l)}")

else:
    print("No solution")
    print(s.check())