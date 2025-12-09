import utime # type: ignore
import asyncio

# Import only necessary functions/constants from SystemTime for clean dependency
try: 
  from .. import Time
except ImportError:
  from micropython_esp32_lib.System import Time

# --- Synchronous Sleep (Standard Naming) ---
try: sync_s = utime.sleep 
except: pass
try: sync_ms = utime.sleep_ms # type: ignore
except: sync_ms = lambda ms: sync_s(ms/1000.0)
try: sync_us = utime.sleep_us # type: ignore
except: sync_us = lambda us: sync_ms(us//1000)
try: sync_ns = utime.sleep_ns # type: ignore
except: sync_ns = lambda ns: sync_us(ns//1000)

# --- Asynchronous Sleep (Standard Naming) ---
try: async_s = asyncio.sleep
except: pass
try: async_ms = asyncio.sleep_ms # type: ignore
except: async_ms = lambda ms: async_s(ms/1000.0)
try: async_us = asyncio.sleep_us # type: ignore
except: async_us = lambda us: async_ms(us//1000)
try: async_ns = asyncio.sleep_ns # type: ignore
except: async_ns = lambda ns: async_us(ns//1000)

_DEFULT_INTERVAL_MS: int = 16

def sync_until_sync(condition, timeout_ms: int | None = None, interval_ms: int = _DEFULT_INTERVAL_MS) -> bool:
  """Synchronously waits until the given synchronously condition is met.

  Args:
    condition (Callable[tuple, bool]): A synchronously condition to wait until satisfied.
    timeout_ms (int | None, optional): The timeout in milliseconds. Defaults to None, which means an indefinite wait.
    interval_ms (int, optional): The interval in milliseconds to check the condition. Defaults to _DEFULT_INTERVAL_MS.

  Returns:
    bool: True if the condition is met, False otherwise.
  """
  if timeout_ms is None: 
    while not condition():
      sync_ms(interval_ms)
    return True
  end_ms = Time.current_ms() + timeout_ms
  while not condition() and Time.current_ms() < end_ms:
    sync_ms(interval_ms)
  return condition()
async def sync_until_async(condition, timeout_ms: int | None = None, interval_ms: int = _DEFULT_INTERVAL_MS) -> bool:
  """Synchronously waits until the given asynchronously condition is met.

  Args:
    condition (Callable[tuple, bool]): A asynchronously condition to wait until satisfied.
    timeout_ms (int | None, optional): The timeout in milliseconds. Defaults to None, which means an indefinite wait.
    interval_ms (int, optional): The interval in milliseconds to check the condition. Defaults to _DEFULT_INTERVAL_MS.

  Returns:
    bool: True if the condition is met, False otherwise.
  """
  if timeout_ms is None: 
    while not await condition():
      sync_ms(interval_ms)
    return True
  end_ms = Time.current_ms() + timeout_ms
  while not await condition() and Time.current_ms() < end_ms:
    sync_ms(interval_ms)
  return await condition()
async def async_until_sync(condition, timeout_ms: int | None = None, interval_ms: int = _DEFULT_INTERVAL_MS) -> bool:
  """Asynchronously waits until the given synchronously condition is met.

  Args:
    condition (Callable[tuple, bool]): A synchronously condition to wait until satisfied.
    timeout_ms (int | None, optional): The timeout in milliseconds. Defaults to None, which means an indefinite wait.
    interval_ms (int, optional): The interval in milliseconds to check the condition. Defaults to _DEFULT_INTERVAL_MS.

  Returns:
    bool: True if the condition is met, False otherwise.
  """
  if timeout_ms is None: 
    while not condition():
      await async_ms(interval_ms)
    return True # Condition is met
  end_ms = Time.current_ms() + timeout_ms
  while not condition() and Time.current_ms() < end_ms:
    await async_ms(interval_ms)
  return condition()
async def async_until_async(condition, timeout_ms: int | None = None, interval_ms: int = _DEFULT_INTERVAL_MS) -> bool:
  """Asynchronously waits until the given asynchronously condition is met.

  Args:
    condition (Callable[tuple, bool]): A asynchronously condition to wait until satisfied.
    timeout_ms (int | None, optional): The timeout in milliseconds. Defaults to None, which means an indefinite wait.
    interval_ms (int, optional): The interval in milliseconds to check the condition. Defaults to _DEFULT_INTERVAL_MS.

  Returns:
    bool: True if the condition is met, False otherwise.
  """
  if timeout_ms is None: 
    while not await condition():
      await async_ms(interval_ms)
    return True # Condition is met
  end_ms = Time.current_ms() + timeout_ms
  while not await condition() and Time.current_ms() < end_ms:
    await async_ms(interval_ms)
  return await condition()
