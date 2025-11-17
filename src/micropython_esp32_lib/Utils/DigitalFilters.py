"""
# file: ./Utils/DigitalFilters.py
"""
import machine

try:
  from ..System import Sleep
  from ..System import Digital
  from ..Utils import Enum
  from ..Utils import Logging
except ImportError:
  from micropython_esp32_lib.System import Sleep
  from micropython_esp32_lib.System import Digital
  from micropython_esp32_lib.Utils import Enum
  from micropython_esp32_lib.Utils import Logging

def isChanged_sync(pin: machine.Pin, start_signal: Digital.Signal, end_signal: Digital.Signal, threshold: int = 10, interval_ms: int = 1) -> bool:
  """Synchronously detects if the pin's value briefly changes from `start_signal` to `end_signal`.  
  
  This is a transient check, not guaranteeing stability at `end_signal`.   
  It checks if `end_signal` is observed at least once within `threshold` checks after the pin is no longer `start_signal`.  

  Args:
    pin (machine.Pin): The digital pin to monitor.
    start_signal (Digital.Signal): The expected initial stable signal.
    end_signal (Digital.Signal): The signal we are looking for a change towards.
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

async def isChanged_async(pin: machine.Pin, start_signal: Digital.Signal, end_signal: Digital.Signal, threshold: int = 10, interval_ms: int = 1) -> bool:
  """Asynchronously detects if the pin's value briefly changes from `start_signal` to `end_signal`.  
  
  This is a transient check, not guaranteeing stability at `end_signal`.  
  It checks if `end_signal` is observed at least once within `threshold` checks after the pin is no longer `start_signal`.  

  Args:
    pin (machine.Pin): The digital pin to monitor.
    start_signal (Digital.Signal): The expected initial stable signal.
    end_signal (Digital.Signal): The signal we are looking for a change towards.
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

def countFiltering_sync(pin: machine.Pin, target_signal: Digital.Signal, threshold: int, interval_ms: int) -> bool:
  """Synchronously applies a count filtering (debouncing) algorithm for digital signals.  
  
  This function determines if a digital pin's value is stably at the `target_signal` by checking for `threshold` consecutive readings.  
  It includes logic to reset the counter if the signal changes, ensuring true stability.  

  Args:
    pin (machine.Pin): The digital pin to monitor.
    target_signal (Digital.Signal): The signal value (HIGH or LOW) to check for stability.
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

async def countFiltering_async(pin: machine.Pin, target_signal: Digital.Signal, threshold: int, interval_ms: int) -> bool:
  """Asynchronously applies a count filtering (debouncing) algorithm for digital signals.  

  This function determines if a digital pin's value is stably at the `target_signal` by checking for `threshold` consecutive readings.  
  It includes logic to reset the counter if the signal changes, ensuring true stability.  

  Args:
    pin (machine.Pin): The digital pin to monitor.
    target_signal (Digital.Signal): The signal value (HIGH or LOW) to check for stability.
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

def isChangedStably_sync(pin: machine.Pin, start_signal: Digital.Signal, end_signal: Digital.Signal, threshold: int, interval_ms: int) -> bool:
  """Synchronously detects a stable signal change.  

  Waits for the pin to leave `start_signal` and then checks if it stably settles at `end_signal` using the `countFiltering_sync` algorithm.  

  Args:
    pin (machine.Pin): The digital pin to monitor.
    start_signal (Digital.Signal): The signal the pin is currently expected to be at.
    end_signal (Digital.Signal): The signal the pin is expected to change to and stabilize at.
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

async def isChangedStably_async(pin: machine.Pin, start_signal: Digital.Signal, end_signal: Digital.Signal, threshold: int, interval_ms: int) -> bool:
  """Asynchronously detects a stable signal change.  

  Waits for the pin to leave `start_signal` and then checks if it stably settles at `end_signal` using the `countFiltering_async` algorithm.  

  Args:
    pin (machine.Pin): The digital pin to monitor.
    start_signal (Digital.Signal): The signal the pin is currently expected to be at.
    end_signal (Digital.Signal): The signal the pin is expected to change to and stabilize at.
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
