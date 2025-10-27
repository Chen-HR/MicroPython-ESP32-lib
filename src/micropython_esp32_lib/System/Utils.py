# System/Utils.py

# Common constants
UINT16_MAX = 65535
UINT08_MAX = 255

def map(x: float | int, in_min: float | int, in_max: float | int, out_min: float | int, out_max: float | int) -> float | int:
  """
  Re-maps a number from one range to another.

  This is similar to Arduino's map function. It interpolates a value `x`
  from an input range (`in_min` to `in_max`) to an output range
  (`out_min` to `out_max`). The function also clamps the output value
  to be within the `out_min` and `out_max` bounds.

  Args:
    x (float | int): The number to map.
    in_min (float | int): The lower bound of the input range.
    in_max (float | int): The upper bound of the input range.
    out_min (float | int): The lower bound of the output range.
    out_max (float | int): The upper bound of the output range.

  Returns:
    float | int: The re-mapped number, clamped to the output range.

  Raises:
    ValueError: If `in_min` is equal to `in_max` to prevent division by zero.
  """
  if in_min == in_max:
    raise ValueError("Input range (in_min, in_max) cannot be equal.")
  
  # Calculate the mapped value
  result = (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min
  
  # Determine the actual min/max for clamping based on the output range direction
  actual_min = min(out_min, out_max)
  actual_max = max(out_min, out_max)
  
  # Clamp the result to the output range
  if result < actual_min:
    return actual_min
  elif result > actual_max:
    return actual_max
  else:
    return result