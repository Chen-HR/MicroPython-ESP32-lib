# System/Code.py
class Code:
  def __init__(self, name: str, code: int):
    """
    Initialize a Code object with a name and code.

    Args:
      name (str): The name of the code.
      code (int): The code value associated with the name.

    Attributes:
      name (str): The name of the code.
      code (int): The code value associated with the name.
    """
    self.name: str = name
    self.code: int = code
  @classmethod
  def define(cls, name: str, code: int):
    """
    Defines a Code object with the given name and code.

    Args:
      name (str): The name of the code.
      code (int): The code value associated with the name.

    Returns:
      Code: The Code object with the given name and code.
    """
    return cls(name, code)
  def __str__(self) -> str:
    return self.name
  def __int__(self) -> int:
    return self.code
  def __repr__(self) -> str:
    return f"Code({self.name}, {self.code})"
  def __eq__(self, other) -> bool:
    _other: Code = other
    return self.code == _other.code
  def __ne__(self, other) -> bool:
    _other: Code = other
    return self.code != _other.code