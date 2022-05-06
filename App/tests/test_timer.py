
from lib.repeated_timer import RepeatedTimer
from time import sleep
from time import time

def foo():
    global old_time

    now_time = time()
    diff = now_time - old_time
    old_time = now_time
    sleep(0.2)
    print (diff)



global old_time
old_time = time()
print ("starting...")
rt = RepeatedTimer(0.5, foo) # it auto-starts, no need of rt.start()
try:
    sleep(5) # your long-running job goes here...
finally:
    rt.stop() # better in a try/finally block to make sure the program ends!
