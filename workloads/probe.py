"""Real Linux CPU/memory probe. Values from this script are guest measurements."""
import gc
import hashlib
import json
import os
import resource
import sys
import time

kind,duration,allocation=sys.argv[1],float(sys.argv[2]),int(sys.argv[3])
print("READY",flush=True)
started=time.monotonic()
if kind=="memory":
    blocks=bytearray(allocation*1024*1024)
    for i in range(0,len(blocks),4096): blocks[i]=1
    time.sleep(duration/2)
    del blocks
    gc.collect()
    print("FREED",flush=True)
    time.sleep(duration/2)
elif kind=="cpu":
    count=0
    while time.monotonic()-started<duration:
        hashlib.sha256(b"a"*1024*64).digest()
        count+=1
    print(json.dumps({"sha256_operations":count}),flush=True)
else:
    time.sleep(duration)
print(json.dumps({"guest_peak_rss_bytes":resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024,
                  "guest_elapsed_seconds":time.monotonic()-started}),flush=True)
