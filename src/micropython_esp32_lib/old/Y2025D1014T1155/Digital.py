import machine

try:
  from . import Wait
  from . import SystemTime
except ImportError:
  from HRChen import Wait
  from HRChen import SystemTime

class Signal:
  """Digital Signal Wrapper Class"""
  HIGH = 1
  LOW = 0
  def __init__(self, signal: int):
    self.signal: int = signal
  def __bool__(self) -> bool:
    return self.signal != 0
  def __int__(self) -> int:
    return 1 if self.__bool__() else 0
  def __str__(self) -> str:
    return "HIGH" if self.__bool__() else "LOW"
  def __repr__(self) -> str:
    return f"DigitalSignal({self.signal})"
  def __eq__(self, other) -> bool:
    return self.__bool__() == other.__bool__()
  def __ne__(self, other) -> bool:
    return self.__bool__() != other.__bool__()

HIGH = Signal(1)
LOW = Signal(0)

def isChanged_sync(pin: machine.Pin, start_signal: Signal, end_signal: Signal, threshold: int = 10, interval_ms: int = 1) -> bool:
  """Detect signal change

  Args:
      start_signal (Signal): start signal
      end_signal (Signal): end signal

  Returns:
      bool: button signal changed from start signal to end signal
  """
  if pin.value() != start_signal.__int__():
    return False
  for _ in range(threshold):
    if pin.value() == end_signal.__int__(): return True
    Wait.sync_ms(interval_ms)
  return False
async def isChanged_async(pin: machine.Pin, start_signal: Signal, end_signal: Signal, threshold: int = 10, interval_ms: int = 1) -> bool:
  """Asynchronous Detect signal change

  Args:
      start_signal (Signal): start signal
      end_signal (Signal): end signal

  Returns:
      bool: button signal changed from start signal to end signal
  """
  if pin.value() != start_signal.__int__():
    return False
  for _ in range(threshold):
    if pin.value() == end_signal.__int__(): return True
    await Wait.async_ms(interval_ms)
  return False


def countFiltering_sync(pin: machine.Pin, target_signal: Signal, threshold: int, interval_ms: int) -> bool:
  """Count Filtering Algorithmfor Digital Signal
  Args:
    target_signal (Signal): target signal
    threshold (int): stability threshold
    interval_ms (int): sampling interval in milliseconds
  Returns:
    bool: button signal is stable at target signal
  """
  # if pin.value() != target_signal.__int__():
  #   return False
  cnt = 0
  while -threshold < cnt < threshold:
    if pin.value() == target_signal.__int__():
      cnt = cnt + 1 if cnt >= 0 else 1
    else:
      cnt = cnt - 1 if cnt <= 0 else -1
    Wait.sync_ms(interval_ms)
  return cnt >= threshold

async def countFiltering_async(pin: machine.Pin, target_signal: Signal, threshold: int, interval_ms: int) -> bool:
  """Asynchronous Count Filtering Algorithm for Digital Signal
  Args:
    target_signal (Signal): target signal
    threshold (int): stability threshold
    interval_ms (int): sampling interval in milliseconds
  Returns:
    bool: button signal is stable at target signal
  """
  # if pin.value() != target_signal.__int__():
  #   return False
  cnt = 0
  while -threshold < cnt < threshold:
    if pin.value() == target_signal.__int__():
      cnt = cnt + 1 if cnt >= 0 else 1
    else:
      cnt = cnt - 1 if cnt <= 0 else -1
    await Wait.async_ms(interval_ms)
  return cnt >= threshold

def isChangedStably_sync(pin: machine.Pin, start_signal: Signal, end_signal: Signal, threshold: int, interval_ms: int) -> bool:
  """Detect signal change with Count Filtering Algorithm

  Args:
      start_signal (Signal): start signal
      end_signal (Signal): end signal
      threshold (int): stability threshold
      interval_ms (int): sampling interval in milliseconds

  Returns:
      bool: button signal changed from start signal to end signal and is stable at end signal
  """
  if pin.value() != start_signal.__int__():
    Wait.sync_ms(interval_ms)
    return False
  while pin.value() == start_signal.__int__():
    Wait.sync_ms(interval_ms)
  return countFiltering_sync(pin, end_signal, threshold, interval_ms)

async def isChangedStably_async(pin: machine.Pin, start_signal: Signal, end_signal: Signal, threshold: int, interval_ms: int) -> bool:
  """Asynchronous Detect signal change with Count Filtering Algorithm

  Args:
      start_signal (Signal): start signal
      end_signal (Signal): end signal
      threshold (int): stability threshold
      interval_ms (int): sampling interval in milliseconds

  Returns:
      bool: button signal changed from start signal to end signal and is stable at end signal
  """
  if pin.value() != start_signal.__int__():
    await Wait.async_ms(interval_ms)
    return False
  while pin.value() == start_signal.__int__():
    await Wait.async_ms(interval_ms)
  return await countFiltering_async(pin, end_signal, threshold, interval_ms)
