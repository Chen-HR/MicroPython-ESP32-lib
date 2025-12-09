"""
# file: ./Utils/py
"""
import urandom

# Common constants
UINT16_MAX = 65535
UINT08_MAX = 255

def mapping(x: float | int, in_min: float | int, in_max: float | int, out_min: float | int, out_max: float | int) -> float | int:
  """
  Re-mappings a number from one range to another.

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

class RGB:
  def __init__(self, r: int, g: int, b: int) -> None:
    self.set(r, g, b)
  def set(self, r: int, g: int, b: int) -> None:
    if 0 <= r <= UINT08_MAX and 0 <= g <= UINT08_MAX and 0 <= b <= UINT08_MAX: # Using UINT08_MAX
      self.r, self.g, self.b = r, g, b
    else:
      raise ValueError("r, g, b must be 0 <= value <= 255") # Changed Exception to ValueError
  def get(self) -> tuple[int, int, int]:
    return self.r, self.g, self.b
  def __str__(self) -> str:
    return f"RGB({self.r}, {self.g}, {self.b})"

class RGBA:
  def __init__(self, r: int, g: int, b: int, a: int = UINT08_MAX) -> None: # Using UINT08_MAX
    self.set(r, g, b, a)
  def set(self, r: int, g: int, b: int, a: int = UINT08_MAX) -> None: # Using UINT08_MAX
    if 0 <= r <= UINT08_MAX and 0 <= g <= UINT08_MAX and 0 <= b <= UINT08_MAX and 0 <= a <= UINT08_MAX:
      self.r, self.g, self.b, self.a = r, g, b, a
    else:
      raise ValueError("r, g, b, a must be 0 <= value <= 255") # Changed Exception to ValueError
  def get(self) -> tuple[int, int, int, int]:
    return self.r, self.g, self.b, self.a
  def __str__(self) -> str:
    return f"RGBA({self.r}, {self.g}, {self.b}, {self.a})"

class Counter:
  def __init__(self, name: str = "", start: int = 0) -> None:
    self.name: str = name
    self.cnt: int = start
  def increment(self) -> None:
    self.cnt += 1
  def decrement(self) -> None:
    self.cnt -= 1
  def reset(self) -> None:
    self.cnt = 0
  def get(self) -> int:
    return self.cnt
  def get_name(self) -> str:
    return self.name

# class IdManager:
#   def __init__(self, max_id: int, isSequence: bool = True) -> None:
#     self.max_id = max_id
#     self.used_ids = set()
#     self.unused_ids = list(range(max_id))
#     self.isSequence = isSequence
#   def _get_sequence(self) -> int:
#     if self.unused_ids:
#       id = self.unused_ids.pop(0)
#       self.used_ids.add(id)
#       return id
#     raise ValueError("All IDs are used")
#   def _get_random(self) -> int:
#     if self.unused_ids:
#       id = urandom.choice(self.unused_ids)
#       self.used_ids.add(id)
#       return id
#     raise ValueError("All IDs are used")
#   def get(self) -> int:
#     if self.isSequence:
#       return self._get_sequence()
#     else:
#       return self._get_random()
#   def set(self, id: int, autoRedirect: bool = True):
#     if id not in self.used_ids:
#       self.used_ids.add(id)
#       self.unused_ids.remove(id)
#       return id
#     elif autoRedirect:
#       return self.get()
#     raise ValueError(f"ID {id} is already in use")

class IdManager:
  """
  An optimized ID manager that is memory-efficient for large ID spaces.

  This implementation avoids storing a list of unused IDs, making it suitable
  for scenarios where `max_id` is very large. It only stores the set of
  IDs that are currently in use.
  """
  def __init__(self, max_id: int, isSequence: bool = True) -> None:
    """
    Initializes the IdManager.

    Args:
      max_id: The maximum number of IDs (exclusive, from 0 to max_id - 1).
      isSequence: If True, allocates IDs sequentially; otherwise, randomly.
    """
    if not isinstance(max_id, int) or max_id <= 0:
      raise ValueError("max_id must be a positive integer")
    
    self.max_id = max_id
    self.used_ids = set()
    self.isSequence = isSequence
    self._next_sequential_id = 0

  def _check_if_full(self) -> None:
    """Checks if all IDs are used and raises an error if so."""
    if len(self.used_ids) >= self.max_id:
      raise ValueError("All IDs are used")

  def _get_sequence(self) -> int:
    """
    Gets the next available sequential ID.
    
    Time Complexity: Average O(1), Worst O(k) where k is the number of
    consecutively used IDs from the last allocation point.
    """
    self._check_if_full()
    
    # Find the next available ID starting from the last known position
    candidate_id = self._next_sequential_id
    while candidate_id in self.used_ids:
      candidate_id += 1
      # This check prevents an infinite loop if the remaining IDs are at the
      # beginning of the range, though _check_if_full() makes it rare.
      if candidate_id >= self.max_id:
        candidate_id = 0

    self.used_ids.add(candidate_id)
    self._next_sequential_id = candidate_id + 1
    return candidate_id

  def _get_random(self) -> int:
    """
    Gets a random available ID.

    Time Complexity: Average O(1) when the load factor is low.
    Performance degrades as the ID space fills up due to collisions.
    """
    self._check_if_full()
    
    while True:
      candidate_id = urandom.randrange(0, self.max_id)
      if candidate_id not in self.used_ids:
        self.used_ids.add(candidate_id)
        return candidate_id

  def get(self) -> int:
    """
    Retrieves an ID based on the configured mode (sequential or random).
    
    Returns:
      An available integer ID.

    Raises:
      ValueError: If all IDs are in use.
    """
    if self.isSequence:
      return self._get_sequence()
    else:
      return self._get_random()

  def set(self, id: int, autoRedirect: bool = True) -> int:
    """
    Manually reserves a specific ID.

    Args:
      id: The integer ID to reserve.
      autoRedirect: If the ID is already used, get a new one automatically.

    Returns:
      The reserved ID or a new ID if autoRedirect is True.

    Raises:
      ValueError: If the ID is out of range, or if the ID is in use and
                  autoRedirect is False.
    """
    if not 0 <= id < self.max_id:
        raise ValueError(f"ID {id} is out of the valid range [0, {self.max_id - 1}]")

    if id not in self.used_ids:
      self.used_ids.add(id)
      return id
    elif autoRedirect:
      return self.get()
    
    raise ValueError(f"ID {id} is already in use")

