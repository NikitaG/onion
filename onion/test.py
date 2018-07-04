import sys
import time

i = 0
s = time.time()
for line in sys.stdin.buffer:
    i+=1
    if i%1000==0:
        print(i, i / (time.time()-s))
    if time.time() - s > 10:
        print("finished", str(i))
        break