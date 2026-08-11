import os
os.environ['UF1_REPEATS']='1'
import json, b_meter_residual as B
res = B.run_shape(8064,256,256,[1,2],seed=1)
print(json.dumps(B.summarize(res), indent=2))
