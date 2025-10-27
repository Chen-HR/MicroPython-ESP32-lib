# System/Enum.py
class Unit:
  def __init__(self, name: str, value: int):
    """
    Initialize a Code object with a name and code.

    Args:
      name  (str): The name of the value.
      value (int): The value associated with the name.

    Attributes:
      name  (str): The name of the value.
      value (int): The value associated with the name.
    """
    self.name : str = name
    self.value: int = value
  def __str__(self) -> str:
    return self.name
  def __int__(self) -> int:
    return self.value
  def __repr__(self) -> str:
    return f"Unit({self.name}, {self.value})"
  def __eq__(self, other) -> bool:
    if isinstance(other, Unit):
      return self.value == other.value
    raise ValueError(f"Can't compare with {type(other)}")
  def __ne__(self, other) -> bool:
    return not self.__eq__(other)