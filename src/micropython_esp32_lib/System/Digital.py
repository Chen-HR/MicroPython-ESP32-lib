"""
# file: ./System/Digital.py
"""
import machine

try:
  from ..Utils import Enum
  from ..Utils import Logging
except ImportError:
  from micropython_esp32_lib.Utils import Enum
  from micropython_esp32_lib.Utils import Logging

# Selects the pin mode.
#   Pin.IN
#   Pin.OUT
#   Pin.OPEN_DRAIN
#   Pin.ALT
#   Pin.ALT_OPEN_DRAIN
#   Pin.ANALOG
class Mode(Enum.Unit): # Inherit from Enum.Unit
  pass
class MODE:
  IN: Mode = Mode("IN", machine.Pin.IN)
  OUT: Mode = Mode("OUT", machine.Pin.OUT)
  OPEN_DRAIN: Mode = Mode("OPEN_DRAIN", machine.Pin.OPEN_DRAIN)
  try:
    ALT: Mode | None = Mode("ALT", machine.Pin.ALT)
    ALT_OPEN_DRAIN: Mode | None = Mode("ALT_OPEN_DRAIN", machine.Pin.ALT_OPEN_DRAIN)
    ANALOG: Mode | None = Mode("ANALOG", machine.Pin.ANALOG)
  except AttributeError:
    Logging.Log("Mode", Logging.LEVEL.WARNING).warning("ALT, ALT_OPEN_DRAIN, and ANALOG are not available on this port.")
    ALT = None
    ALT_OPEN_DRAIN = None
    ANALOG = None

# Selects whether there is a pull up/down resistor. Use the value None for no pull.
#   Pin.PULL_UP
#   Pin.PULL_DOWN
#   Pin.PULL_HOLD
class Pull(Enum.Unit): # Inherit from Enum.Unit
  """Pull Direction Wrapper Class, extending System.Code."""
  def __init__(self, name: str, pull_value: int):
    super().__init__(name, pull_value)
  def __repr__(self) -> str:
    return f"Pull({self.name}, {self.value})"
class PULL:
  """Standard pull direction constants (UP, DOWN)."""
  UP: Pull = Pull("UP", machine.Pin.PULL_UP)
  DOWN: Pull = Pull("DOWN", machine.Pin.PULL_DOWN)
  try:
    HOLD: Pull | None = Pull("HOLD", machine.Pin.PULL_HOLD)
  except AttributeError:
    Logging.Log("Pull", Logging.LEVEL.WARNING).warning("HOLD is not available on this port.")
    HOLD = None

# Selects the pin drive strength. A port may define additional drive constants with increasing number corresponding to increasing drive strength.
#   Pin.DRIVE_0
#   Pin.DRIVE_1
#   Pin.DRIVE_2
class Drive(Enum.Unit): # Inherit from Enum.Unit
  pass
class DRIVE:
  try:
    DRIVE_0: Drive | None = Drive("DRIVE_0", machine.Pin.DRIVE_0)
    DRIVE_1: Drive | None = Drive("DRIVE_1", machine.Pin.DRIVE_1)
    DRIVE_2: Drive | None = Drive("DRIVE_2", machine.Pin.DRIVE_2)
  except AttributeError:
    Logging.Log("Drive", Logging.LEVEL.WARNING).warning("DRIVE_0, DRIVE_1, and DRIVE_2 are not available on this port.")
    DRIVE_0 = None
    DRIVE_1 = None
    DRIVE_2 = None

# Selects the IRQ trigger type.
#   Pin.IRQ_FALLING
#   Pin.IRQ_RISING
#   Pin.IRQ_LOW_LEVEL
#   Pin.IRQ_HIGH_LEVEL
class IRQ(Enum.Unit): # Inherit from Enum.Unit
  """IRQ Trigger Wrapper Class, extending System.Code."""
  def __or__(self, other: Enum.Unit):
    return self.value | other.value
class IRQCode:
  IRQ_FALLING: IRQ = IRQ("IRQ_FALLING", machine.Pin.IRQ_FALLING)
  IRQ_RISING: IRQ = IRQ("IRQ_RISING", machine.Pin.IRQ_RISING)
  # IRQ_LOW_LEVEL: IRQ = IRQ("IRQ_LOW_LEVEL", machine.Pin.IRQ_LOW_LEVEL)
  # IRQ_HIGH_LEVEL: IRQ = IRQ("IRQ_HIGH_LEVEL", machine.Pin.IRQ_HIGH_LEVEL)
  try:
    IRQ_LOW_LEVEL: IRQ | None = IRQ("IRQ_LOW_LEVEL", machine.Pin.IRQ_LOW_LEVEL)
    IRQ_HIGH_LEVEL: IRQ | None = IRQ("IRQ_HIGH_LEVEL", machine.Pin.IRQ_HIGH_LEVEL)
  except AttributeError:
    Logging.Log("IRQ", Logging.LEVEL.WARNING).warning("IRQ_LOW_LEVEL and IRQ_HIGH_LEVEL are not available on this port.")
    IRQ_LOW_LEVEL = None
    IRQ_HIGH_LEVEL = None

class Signal(Enum.Unit): # Inherit from Enum.Unit
  """Digital Signal Wrapper Class, extending System.Code."""
  def __init__(self, name: str, signal_value: int):
    super().__init__(name, signal_value)
  def __repr__(self) -> str:
    return f"Signal({self.name}, {self.value})"
  def __bool__(self) -> bool:
    """Returns True if the signal is non-zero (HIGH), False otherwise (LOW)."""
    return self.value != 0
  def __eq__(self, other) -> bool:
    if isinstance(other, Signal):
      return self.value == other.value
    elif isinstance(other, int):
      return self.value == other
    raise ValueError(f"Can't compare with {type(other)}")
  def __ne__(self, other) -> bool:
    return not self.__eq__(other)
class SIGNAL:
  """Standard digital signal constants (HIGH, LOW)."""
  HIGH: Signal = Signal("HIGH", 1)
  LOW : Signal = Signal("LOW", 0)
  @classmethod
  def inverse(cls, signal: Signal) -> Signal:
    if signal == SIGNAL.HIGH: return SIGNAL.LOW
    elif signal == SIGNAL.LOW: return SIGNAL.HIGH
    raise ValueError(f"Signal value must be 0 or 1, not {signal}")
  @classmethod
  def query(cls, value: int) -> Signal:
    if   value == 1: return SIGNAL.HIGH
    elif value == 0: return SIGNAL.LOW
    raise ValueError(f"Signal value must be 0 or 1, not {value}")
    
    
