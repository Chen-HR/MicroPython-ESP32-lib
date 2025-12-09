"""
# Digital Tools

This module provides tools for working with digital pins.

The class `Mode`, `Pull`, `Drive`, `IRQTrigger` and `Signal` are used to define the mode, pull state, drive strength, IRQ trigger type and signal state of a pin.

"""
import machine # type: ignore

try:
  from .Time import Sleep
except ImportError:
  from micropython_esp32_lib.System.Time import Sleep

# Pin Mode:
#   machine.Pin.IN
#   machine.Pin.OUT
#   machine.Pin.OPEN_DRAIN
#   machine.Pin.ALT
#   machine.Pin.ALT_OPEN_DRAIN
#   machine.Pin.ANALOG
class Mode:
  def __init__(self, code: int, name: str):
    self.code: int = code
    self.name: str = name
  def __str__(self) -> str:
    return f"Mode({self.code}, {self.name})"
  def __eq__(self, other: "Mode") -> bool: # type: ignore
    return self.code == other.code and self.name == other.name
  @classmethod
  def query(cls, code: int) -> "Mode":
    for mode in cls.__dict__.values():
      if isinstance(mode, cls):
        if mode.code == code:
          return mode
    raise ValueError(f"Unknown pin mode code: {code}")
  IN: "Mode"
  OUT: "Mode"
  OPEN_DRAIN: "Mode"
  ALT: "Mode"
  ALT_OPEN_DRAIN: "Mode"
  ANALOG: "Mode"
try: Mode.IN = Mode(machine.Pin.IN, "IN")
except AttributeError: pass
try: Mode.OUT = Mode(machine.Pin.OUT, "OUT")
except AttributeError: pass
try: Mode.OPEN_DRAIN = Mode(machine.Pin.OPEN_DRAIN, "OPEN_DRAIN")
except AttributeError: pass
try: Mode.ALT = Mode(machine.Pin.ALT, "ALT")
except AttributeError: pass
try: Mode.ALT_OPEN_DRAIN = Mode(machine.Pin.ALT_OPEN_DRAIN, "ALT_OPEN_DRAIN")
except AttributeError: pass
try: Mode.ANALOG = Mode(machine.Pin.ANALOG, "ANALOG")
except AttributeError: pass

# Pin Pull State: 
#   machine.Pin.PULL_UP
#   machine.Pin.PULL_DOWN
#   machine.Pin.PULL_HOLD
class Pull:
  def __init__(self, code: int, name: str):
    self.code: int = code
    self.name: str = name
  def __str__(self) -> str:
    return f"Pull({self.code}, {self.name})"
  def __eq__(self, other: "Pull") -> bool: # type: ignore
    return self.code == other.code and self.name == other.name
  @classmethod
  def query(cls, code: int) -> "Pull":
    for pull in cls.__dict__.values():
      if isinstance(pull, cls):
        if pull.code == code:
          return pull
    raise ValueError(f"Unknown pull mode code: {code}")
  UP: "Pull"
  DOWN: "Pull"
  HOLD: "Pull"
try: Pull.UP = Pull(machine.Pin.PULL_UP, "UP")
except AttributeError: pass
try: Pull.DOWN = Pull(machine.Pin.PULL_DOWN, "DOWN")
except AttributeError: pass
try: Pull.HOLD = Pull(machine.Pin.PULL_HOLD, "HOLD")
except AttributeError: pass

# Pin Drive Strength: 
#   machine.Pin.DRIVE_0
#   machine.Pin.DRIVE_1
#   machine.Pin.DRIVE_2
class Drive:
  def __init__(self, code: int, name: str):
    self.code: int = code
    self.name: str = name
  def __str__(self) -> str:
    return f"Drive({self.code}, {self.name})"
  def __eq__(self, other: "Drive") -> bool: # type: ignore
    return self.code == other.code and self.name == other.name
  @classmethod
  def query(cls, code: int) -> "Drive":
    for drive in cls.__dict__.values():
      if isinstance(drive, cls):
        if drive.code == code:
          return drive
    raise ValueError(f"Unknown drive strength code: {code}")
  _0: "Drive"
  _1: "Drive"
  _2: "Drive"
try: Drive._0 = Drive(machine.Pin.DRIVE_0, "_0")
except AttributeError: pass
try: Drive._1 = Drive(machine.Pin.DRIVE_1, "_1")
except AttributeError: pass
try: Drive._2 = Drive(machine.Pin.DRIVE_2, "_2")
except AttributeError: pass


# IRQ Trigger Type.
#   machine.Pin.IRQ_FALLING
#   machine.Pin.IRQ_RISING
#   machine.Pin.IRQ_LOW_LEVEL
#   machine.Pin.IRQ_HIGH_LEVEL
class IRQTrigger:
  def __init__(self, code: int, name: str):
    self.code: int = code
    self.name: str = name
  def __str__(self) -> str:
    return f"IRQTrigger({self.code}, {self.name})"
  def __eq__(self, other: "IRQTrigger") -> bool: # type: ignore
    return self.code == other.code and self.name == other.name
  def __or__(self, value: "IRQTrigger"):
    return IRQTrigger(self.code | value.code, f"{self.name} | {value.name}")
  @classmethod
  def query(cls, code: int) -> "IRQTrigger":
    for type in cls.__dict__.values():
      if isinstance(type, cls):
        if type.code == code:
          return type
    raise ValueError(f"Unknown IRQ trigger type code: {code}")
  FALLING    : "IRQTrigger"
  RISING     : "IRQTrigger"
  LOW_LEVEL  : "IRQTrigger"
  HIGH_LEVEL : "IRQTrigger"
try: IRQTrigger.FALLING = IRQTrigger(machine.Pin.IRQ_FALLING, "FALLING")
except AttributeError: pass
try: IRQTrigger.RISING = IRQTrigger(machine.Pin.IRQ_RISING, "RISING")
except AttributeError: pass
try: IRQTrigger.LOW_LEVEL = IRQTrigger(machine.Pin.IRQ_LOW_LEVEL, "LOW_LEVEL")
except AttributeError: pass
try: IRQTrigger.HIGH_LEVEL = IRQTrigger(machine.Pin.IRQ_HIGH_LEVEL, "HIGH_LEVEL")
except AttributeError: pass

class Signal:
  def __init__(self, value: int, name: str):
    self.value: int = value
    self.name: str = name
  def __str__(self) -> str:
    return f"Signal({self.value}, {self.name})"
  def __eq__(self, other: "Signal") -> bool: # type: ignore
    return self.value == other.value and self.name == other.name
  def __ne__(self, other: "Signal") -> bool: # type: ignore
    return not self.__eq__(other)
  def inverse(self) -> "Signal":
    if self == Signal.HIGH: return Signal.LOW
    elif self == Signal.LOW: return Signal.HIGH
    raise ValueError(f"Signal value must be 0 or 1, not {self}")
  @classmethod
  def query(cls, code: int) -> "Signal":
    for signal in cls.__dict__.values():
      if isinstance(signal, cls):
        if signal.value == code:
          return signal
    raise ValueError(f"Unknown digital signal value: {code}")
  HIGH: "Signal"
  LOW : "Signal"
try: Signal.HIGH = Signal(1, "HIGH")
except AttributeError: pass
try: Signal.LOW = Signal(0, "LOW")
except AttributeError: pass

def isChanged_sync(pin: machine.Pin, start: Signal, end: Signal, threshold: int = 10, interval_ms: int = 1) -> bool:
  """Synchronously detects if the pin's value briefly changes from `start` to `end`.  
  
  This is a transient check, not guaranteeing stability at `end`.   
  It checks if `end` is observed at least once within `threshold` checks after the pin is no longer `start`.  

  Args:
    pin (machine.Pin): The digital pin to monitor.
    start (Signal): The expected initial stable signal.
    end (Signal): The signal we are looking for a change towards.
    threshold (int, optional): The number of consecutive checks for `end` to confirm a change. Defaults to 10.
    interval_ms (int, optional): The delay in milliseconds between pin readings. Defaults to 1.

  Returns:
    bool: True if a change from `start` to `end` is detected
          (i.e., `end` is read at least once within `threshold` checks
          after the pin is no longer `start`), False otherwise.
  """
  if pin.value() != start.value:
    return False
  
  # Wait until the signal leaves start
  while pin.value() == start.value:
    Sleep.sync_ms(interval_ms)

  # After leaving start, check if end is observed within a short window
  for _ in range(threshold): 
    if pin.value() == end.value:
      return True
    Sleep.sync_ms(interval_ms)
  return False

async def isChanged_async(pin: machine.Pin, start: Signal, end: Signal, threshold: int = 10, interval_ms: int = 1) -> bool:
  """Asynchronously detects if the pin's value briefly changes from `start` to `end`.  
  
  This is a transient check, not guaranteeing stability at `end`.  
  It checks if `end` is observed at least once within `threshold` checks after the pin is no longer `start`.  

  Args:
    pin (machine.Pin): The digital pin to monitor.
    start (Signal): The expected initial stable signal.
    end (Signal): The signal we are looking for a change towards.
    threshold (int, optional): The number of consecutive checks for `end` to confirm a change. Defaults to 10.
    interval_ms (int, optional): The delay in milliseconds between pin readings. Defaults to 1.

  Returns:
    bool: True if a change from `start` to `end` is detected
          (i.e., `end` is read at least once within `threshold` checks
          after the pin is no longer `start`), False otherwise.
  """
  if pin.value() != start.value:
    return False
  
  while pin.value() == start.value:
    await Sleep.async_ms(interval_ms)

  for _ in range(threshold):
    if pin.value() == end.value:
      return True
    await Sleep.async_ms(interval_ms)
  return False

def countFiltering_sync(pin: machine.Pin, target: Signal, threshold: int, interval_ms: int) -> bool:
  """Synchronously applies a count filtering (debouncing) algorithm for digital signals.  
  
  This function determines if a digital pin's value is stably at the `target` by checking for `threshold` consecutive readings.  
  It includes logic to reset the counter if the signal changes, ensuring true stability.  

  Args:
    pin (machine.Pin): The digital pin to monitor.
    target (Signal): The signal value (HIGH or LOW) to check for stability.
    threshold (int): The number of consecutive stable readings required to confirm stability.
    interval_ms (int): The delay in milliseconds between pin readings.

  Returns:
    bool: True if the pin is stably at `target`, False otherwise.
  """
  cnt = 0
  while -threshold < cnt < threshold:
    if pin.value() == target.value:
      cnt = cnt + 1 if cnt >= 0 else 1
    else:
      cnt = cnt - 1 if cnt <= 0 else -1
    Sleep.sync_ms(interval_ms)
  return cnt >= threshold

async def countFiltering_async(pin: machine.Pin, target: Signal, threshold: int, interval_ms: int) -> bool:
  """Asynchronously applies a count filtering (debouncing) algorithm for digital signals.  

  This function determines if a digital pin's value is stably at the `target` by checking for `threshold` consecutive readings.  
  It includes logic to reset the counter if the signal changes, ensuring true stability.  

  Args:
    pin (machine.Pin): The digital pin to monitor.
    target (Signal): The signal value (HIGH or LOW) to check for stability.
    threshold (int): The number of consecutive stable readings required to confirm stability.
    interval_ms (int): The delay in milliseconds between pin readings.

  Returns:
    bool: True if the pin is stably at `target`, False otherwise.
  """
  cnt = 0
  while -threshold < cnt < threshold:
    if pin.value() == target.value:
      cnt = cnt + 1 if cnt >= 0 else 1
    else:
      cnt = cnt - 1 if cnt <= 0 else -1
    await Sleep.async_ms(interval_ms)
  return cnt >= threshold

def isChangedStably_sync(pin: machine.Pin, start: Signal, end: Signal, threshold: int, interval_ms: int) -> bool:
  """Synchronously detects a stable signal change.  

  Waits for the pin to leave `start` and then checks if it stably settles at `end` using the `countFiltering_sync` algorithm.  

  Args:
    pin (machine.Pin): The digital pin to monitor.
    start (Signal): The signal the pin is currently expected to be at.
    end (Signal): The signal the pin is expected to change to and stabilize at.
    threshold (int): The stability threshold for `countFiltering_sync`.
    interval_ms (int): The delay in milliseconds between pin readings.

  Returns:
    bool: True if a stable change from `start` to `end` is detected, False otherwise.
  """
  if pin.value() != start.value:
    Sleep.sync_ms(interval_ms)
    return False
  
  while pin.value() == start.value:
    Sleep.sync_ms(interval_ms)
  
  return countFiltering_sync(pin, end, threshold, interval_ms)

async def isChangedStably_async(pin: machine.Pin, start: Signal, end: Signal, threshold: int, interval_ms: int) -> bool:
  """Asynchronously detects a stable signal change.  

  Waits for the pin to leave `start` and then checks if it stably settles at `end` using the `countFiltering_async` algorithm.  

  Args:
    pin (machine.Pin): The digital pin to monitor.
    start (Signal): The signal the pin is currently expected to be at.
    end (Signal): The signal the pin is expected to change to and stabilize at.
    threshold (int): The stability threshold for `countFiltering_sync`.
    interval_ms (int): The delay in milliseconds between pin readings.

  Returns:
    bool: True if a stable change from `start` to `end` is detected, False otherwise.
  """
  if pin.value() != start.value:
    await Sleep.async_ms(interval_ms)
    return False
  
  while pin.value() == start.value:
    await Sleep.async_ms(interval_ms)
  
  return await countFiltering_async(pin, end, threshold, interval_ms)
