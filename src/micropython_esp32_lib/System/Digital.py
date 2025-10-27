# System/Digital.py
import machine

try:
  from . import Time
  from . import Sleep
  from . import Enum
  from . import Logging
except ImportError:
  from micropython_esp32_lib.System import Time
  from micropython_esp32_lib.System import Sleep
  from micropython_esp32_lib.System import Enum
  from micropython_esp32_lib.System import Logging

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
  DRIVE_0: Drive = Drive("DRIVE_0", machine.Pin.DRIVE_0)
  DRIVE_1: Drive = Drive("DRIVE_1", machine.Pin.DRIVE_1)
  DRIVE_2: Drive = Drive("DRIVE_2", machine.Pin.DRIVE_2)

# Selects the IRQ trigger type.
#   Pin.IRQ_FALLING
#   Pin.IRQ_RISING
#   Pin.IRQ_LOW_LEVEL
#   Pin.IRQ_HIGH_LEVEL
class IRQ(Enum.Unit): # Inherit from Enum.Unit
  """IRQ Trigger Wrapper Class, extending System.Code."""
  pass
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

def isChanged_sync(pin: machine.Pin, start_signal: Signal, end_signal: Signal, threshold: int = 10, interval_ms: int = 1) -> bool:
  """Synchronously detects if the pin's value briefly changes from `start_signal` to `end_signal`.  
  
  This is a transient check, not guaranteeing stability at `end_signal`.   
  It checks if `end_signal` is observed at least once within `threshold` checks after the pin is no longer `start_signal`.  

  Args:
    pin (machine.Pin): The digital pin to monitor.
    start_signal (Signal): The expected initial stable signal.
    end_signal (Signal): The signal we are looking for a change towards.
    threshold (int, optional): The number of consecutive checks for `end_signal` to confirm a change. Defaults to 10.
    interval_ms (int, optional): The delay in milliseconds between pin readings. Defaults to 1.

  Returns:
    bool: True if a change from `start_signal` to `end_signal` is detected
          (i.e., `end_signal` is read at least once within `threshold` checks
          after the pin is no longer `start_signal`), False otherwise.
  """
  if pin.value() != start_signal.value:
    return False
  
  # Wait until the signal leaves start_signal
  while pin.value() == start_signal.value:
    Sleep.sync_ms(interval_ms)

  # After leaving start_signal, check if end_signal is observed within a short window
  for _ in range(threshold): 
    if pin.value() == end_signal.value:
      return True
    Sleep.sync_ms(interval_ms)
  return False

async def isChanged_async(pin: machine.Pin, start_signal: Signal, end_signal: Signal, threshold: int = 10, interval_ms: int = 1) -> bool:
  """Asynchronously detects if the pin's value briefly changes from `start_signal` to `end_signal`.  
  
  This is a transient check, not guaranteeing stability at `end_signal`.  
  It checks if `end_signal` is observed at least once within `threshold` checks after the pin is no longer `start_signal`.  

  Args:
    pin (machine.Pin): The digital pin to monitor.
    start_signal (Signal): The expected initial stable signal.
    end_signal (Signal): The signal we are looking for a change towards.
    threshold (int, optional): The number of consecutive checks for `end_signal` to confirm a change. Defaults to 10.
    interval_ms (int, optional): The delay in milliseconds between pin readings. Defaults to 1.

  Returns:
    bool: True if a change from `start_signal` to `end_signal` is detected
          (i.e., `end_signal` is read at least once within `threshold` checks
          after the pin is no longer `start_signal`), False otherwise.
  """
  if pin.value() != start_signal.value:
    return False
  
  while pin.value() == start_signal.value:
    await Sleep.async_ms(interval_ms)

  for _ in range(threshold):
    if pin.value() == end_signal.value:
      return True
    await Sleep.async_ms(interval_ms)
  return False

def countFiltering_sync(pin: machine.Pin, target_signal: Signal, threshold: int, interval_ms: int) -> bool:
  """Synchronously applies a count filtering (debouncing) algorithm for digital signals.  
  
  This function determines if a digital pin's value is stably at the `target_signal` by checking for `threshold` consecutive readings.  
  It includes logic to reset the counter if the signal changes, ensuring true stability.  

  Args:
    pin (machine.Pin): The digital pin to monitor.
    target_signal (Signal): The signal value (HIGH or LOW) to check for stability.
    threshold (int): The number of consecutive stable readings required to confirm stability.
    interval_ms (int): The delay in milliseconds between pin readings.

  Returns:
    bool: True if the pin is stably at `target_signal`, False otherwise.
  """
  cnt = 0
  while -threshold < cnt < threshold:
    if pin.value() == target_signal.value:
      cnt = cnt + 1 if cnt >= 0 else 1
    else:
      cnt = cnt - 1 if cnt <= 0 else -1
    Sleep.sync_ms(interval_ms)
  return cnt >= threshold

async def countFiltering_async(pin: machine.Pin, target_signal: Signal, threshold: int, interval_ms: int) -> bool:
  """Asynchronously applies a count filtering (debouncing) algorithm for digital signals.  

  This function determines if a digital pin's value is stably at the `target_signal` by checking for `threshold` consecutive readings.  
  It includes logic to reset the counter if the signal changes, ensuring true stability.  

  Args:
    pin (machine.Pin): The digital pin to monitor.
    target_signal (Signal): The signal value (HIGH or LOW) to check for stability.
    threshold (int): The number of consecutive stable readings required to confirm stability.
    interval_ms (int): The delay in milliseconds between pin readings.

  Returns:
    bool: True if the pin is stably at `target_signal`, False otherwise.
  """
  cnt = 0
  while -threshold < cnt < threshold:
    if pin.value() == target_signal.value:
      cnt = cnt + 1 if cnt >= 0 else 1
    else:
      cnt = cnt - 1 if cnt <= 0 else -1
    await Sleep.async_ms(interval_ms)
  return cnt >= threshold

def isChangedStably_sync(pin: machine.Pin, start_signal: Signal, end_signal: Signal, threshold: int, interval_ms: int) -> bool:
  """Synchronously detects a stable signal change.  

  Waits for the pin to leave `start_signal` and then checks if it stably settles at `end_signal` using the `countFiltering_sync` algorithm.  

  Args:
    pin (machine.Pin): The digital pin to monitor.
    start_signal (Signal): The signal the pin is currently expected to be at.
    end_signal (Signal): The signal the pin is expected to change to and stabilize at.
    threshold (int): The stability threshold for `countFiltering_sync`.
    interval_ms (int): The delay in milliseconds between pin readings.

  Returns:
    bool: True if a stable change from `start_signal` to `end_signal` is detected, False otherwise.
  """
  if pin.value() != start_signal.value:
    Sleep.sync_ms(interval_ms)
    return False
  
  while pin.value() == start_signal.value:
    Sleep.sync_ms(interval_ms)
  
  return countFiltering_sync(pin, end_signal, threshold, interval_ms)

async def isChangedStably_async(pin: machine.Pin, start_signal: Signal, end_signal: Signal, threshold: int, interval_ms: int) -> bool:
  """Asynchronously detects a stable signal change.  

  Waits for the pin to leave `start_signal` and then checks if it stably settles at `end_signal` using the `countFiltering_async` algorithm.  

  Args:
    pin (machine.Pin): The digital pin to monitor.
    start_signal (Signal): The signal the pin is currently expected to be at.
    end_signal (Signal): The signal the pin is expected to change to and stabilize at.
    threshold (int): The stability threshold for `countFiltering_sync`.
    interval_ms (int): The delay in milliseconds between pin readings.

  Returns:
    bool: True if a stable change from `start_signal` to `end_signal` is detected, False otherwise.
  """
  if pin.value() != start_signal.value:
    await Sleep.async_ms(interval_ms)
    return False
  
  while pin.value() == start_signal.value:
    await Sleep.async_ms(interval_ms)
  
  return await countFiltering_async(pin, end_signal, threshold, interval_ms)
