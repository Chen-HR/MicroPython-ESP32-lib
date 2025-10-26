from typing import SupportsIndex
import machine

try:
  from . import Wait
except ImportError:
  from HRChen import Wait

class Signal:
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
  def __setattr__(self, name: str, value: machine.Any) -> None:
    pass
  def __ne__(self, other) -> bool:
    return self.__bool__() != other.__bool__()

HIGH = Signal(1)
LOW = Signal(0)


def countFiltering_digital_sync(pin: machine.Pin, target_signal: Signal, threshold: int, interval_ms: int) -> bool: # TODO: move to utils
  """Count Filtering Algorithmfor Digital Signal
  Args:
    target_signal (Signal): target signal
    threshold (int): stability threshold
    interval_ms (int): sampling interval in milliseconds
  Returns:
    bool: button signal is stable at target signal
  """
  if pin.value() == target_signal:
    # init counters
    cnt = 0
    uncnt = 0
    while True:
      # check signal and update counters
      if pin.value() == target_signal:
        cnt += 1
        uncnt = 0
      else:
        cnt = 0
        uncnt += 1
      # check counters
      if cnt > threshold:
        return True
      elif uncnt > threshold:
        return False
      Wait.sync_ms(interval_ms)
  return False

async def countFiltering_digital_async(pin: machine.Pin, target_signal: Signal, threshold: int, interval_ms: int) -> bool: # TODO: move to utils
  """Asynchronous Count Filtering Algorithm for Digital Signal
  Args:
    target_signal (Signal): target signal
    threshold (int): stability threshold
    interval_ms (int): sampling interval in milliseconds
  Returns:
    bool: button signal is stable at target signal
  """
  if pin.value() == target_signal:
    # init counters
    cnt = 0
    uncnt = 0
    while True:
      # check signal and update counters
      if pin.value() == target_signal:
        cnt += 1
        uncnt = 0
      else:
        cnt = 0
        uncnt += 1
      # check counters
      if cnt > threshold:
        return True
      elif uncnt > threshold:
        return False
      await Wait.async_ms(interval_ms)
  return False

def isChanged_digital_sync(pin: machine.Pin, start_signal: Signal, end_signal: Signal, threshold: int, interval_ms: int) -> bool: # TODO: move to utils
  """Detect signal change with Count Filtering Algorithm

  Args:
      start_signal (Signal): start signal
      end_signal (Signal): end signal
      threshold (int): stability threshold
      interval_ms (int): sampling interval in milliseconds

  Returns:
      bool: button signal changed from start signal to end signal and is stable at end signal
  """
  while pin.value() == start_signal:
    Wait.sync_ms(interval_ms)
  return countFiltering_digital_sync(pin, end_signal, threshold, interval_ms)

async def isChanged_digital_async(pin: machine.Pin, start_signal: Signal, end_signal: Signal, threshold: int, interval_ms: int) -> bool: # TODO: move to utils
  """Asynchronous Detect signal change with Count Filtering Algorithm

  Args:
      start_signal (Signal): start signal
      end_signal (Signal): end signal
      threshold (int): stability threshold
      interval_ms (int): sampling interval in milliseconds

  Returns:
      bool: button signal changed from start signal to end signal and is stable at end signal
  """
  while pin.value() == start_signal:
    await Wait.async_ms(interval_ms)
  return await countFiltering_digital_async(pin, end_signal, threshold, interval_ms)
