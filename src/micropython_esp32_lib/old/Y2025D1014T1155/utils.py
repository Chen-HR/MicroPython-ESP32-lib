import machine

try:
  from . import Wait
  from . import Digital
except ImportError:
  from HRChen import Wait
  from HRChen import Digital

UINT16_MAX = 65535
UINT08_MAX = 255

def map(x, in_min, in_max, out_min, out_max):
  if in_min == in_max:
    raise Exception("in_min == in_max")
  # if not ((in_min >= x >= in_max) or (in_min <= x <= in_max)):
  #   d_in_min, d_in_max = abs(in_min - x), abs(in_max - x)
  #   return out_min if d_in_min < d_in_max else out_max
  # return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min
  result = (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min
  actual_min, actual_max = min(out_min, out_max), max(out_min, out_max)
  return actual_min if result < actual_min else actual_max if result > actual_max else result
