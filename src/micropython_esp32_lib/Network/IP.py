"""
# Network/IP.py
"""
class IPV4Address:
  NONE = (-1, -1, -1, -1)
  def __init__(self, addr: tuple[int, int, int, int] | str | None = None) -> None:
    """
    Initializes an instance of the IPV4Address class.

    Args:
      ip (tuple[int, int, int, int] | None): The IPv4 address as a tuple of integers.
        If None, the address is set to (0, 0, 0, 0).

    Raises:
      ValueError: If the length of the input tuple is not 4,
        or if any of the integers are not between 0 and 255.
    """
    # Parse addr into a tuple and store it in _addr
    _addr = tuple()
    if addr is None: # if addr is None
      _addr = IPV4Address.NONE
    elif isinstance(addr, str): # if addr is str
      try:
        _addr = tuple(map(int, addr.split("."))) # type: ignore
      except ValueError:
        raise ValueError(f"Invalid IP address string: {addr}")
    elif isinstance(addr, tuple): # if addr is tuple
      _addr = addr
    # Validate the _addr format
    if isinstance(_addr, tuple): # if addr is tuple
      if len(_addr) != 4: # check length
        raise ValueError("IPV4 address must have exactly 4 octets")
      if all(0 <= a <= 255 for a in _addr): # check range
        self.addr: tuple[int, int, int, int] = _addr
        return
      else:
        raise ValueError("Each number must be between 0 and 255")
    raise TypeError("Address must be a tuple of 4 integers, a string, or None")
  def __str__(self) -> str:
    if all(0 <= a <= 255 for a in self.addr): # check range
      return ".".join(map(str, self.addr))
    else:
      return "None"    
  def __repr__(self) -> str:
    return f"IPV4Address({self.addr})"
  def str(self) -> str:
    return self.__str__()
