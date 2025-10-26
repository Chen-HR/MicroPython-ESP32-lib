# Sysyem/Sleep.py
import utime
import asyncio

# Import only necessary functions/constants from SystemTime for clean dependency
try: 
  from . import Time
except ImportError:
  from MicroPython_ESP32_lib.System import Time

# --- Synchronous Sleep (Standard Naming) ---
try: sync_s = utime.sleep 
except: pass
try: sync_ms = utime.sleep_ms 
except: pass
try: sync_us = utime.sleep_us 
except: pass
try: sync_ns = utime.sleep_ns 
except: pass

# --- Asynchronous Sleep (Standard Naming) ---
try: async_s = asyncio.sleep
except: pass
try: async_ms = asyncio.sleep_ms
except: pass
try: async_us = asyncio.sleep_us
except: pass
try: async_ns = asyncio.sleep_ns
except: pass

def sync_wait_until(condition, timeout_ms: float = -1, interval_ms: int = 1) -> bool:
  """Synchronously waits until the given condition is met.

  Args:
    condition (callable): A condition to wait until satisfied.
    timeout_ms (float, optional): The timeout in milliseconds. Defaults to -1, which means an indefinite wait.
    interval_ms (int, optional): The interval in milliseconds to check the condition. Defaults to 1.

  Returns:
    bool: True if the condition is met, False otherwise.
  """
  if timeout_ms < 0:
    while not bool(condition()):
      sync_ms(interval_ms)
    return True # Condition is met
  else:
    end_ms = Time.current_ms() + timeout_ms
    while not bool(condition()) and Time.current_ms() < end_ms:
      sync_ms(interval_ms)
  return bool(condition())
async def async_wait_until(condition, timeout_ms: float = -1, interval_ms: int = 1) -> bool:
  """Asynchronously waits until the given condition is met.

  Args:
    condition (callable): A condition to wait until satisfied.
    timeout_ms (float, optional): The timeout in milliseconds. Defaults to -1, which means an indefinite wait.
    interval_ms (int, optional): The interval in milliseconds to check the condition. Defaults to 1.

  Returns:
    bool: True if the condition is met, False otherwise.
  """
  if timeout_ms < 0:
    while not bool(condition()):
      await async_ms(interval_ms)
    return True # Condition is met
  else:
    end_ms = Time.current_ms() + timeout_ms
    while not bool(condition()) and Time.current_ms() < end_ms:
      await async_ms(interval_ms)
  return bool(condition())


if __name__ == "__main__":
  print(f"[{Time.Time()}] [__main__] Test sync_wait_until() to wait 5 seconds...")
  try: 
    end_time_s = Time.current_s() + 5
    sync_wait_until(lambda: Time.current_s() >= end_time_s, timeout_ms=10000, interval_ms=100)
    print(f"[{Time.Time()}] [__main__] sync_wait_until() done.")
  except Exception as e:
    print(f"[{Time.Time()}] [__main__] sync_wait_until() error:", e)