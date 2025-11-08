"""
# file: ./System/Timer.py
"""
import machine
import random
import asyncio
import inspect

try:
  from ..System import Sleep
  from ..Utils import Logging
  from ..Utils import Enum
  from ..Utils import Utils
except ImportError:
  from micropython_esp32_lib.System import Sleep
  from micropython_esp32_lib.Utils import Logging
  from micropython_esp32_lib.Utils import Enum
  from micropython_esp32_lib.Utils import Utils

class Mode(Enum.Unit):
  """Timer operating modes."""
  pass
class MODE:
  try:
    ONE_SHOT = Mode("ONE_SHOT", machine.Timer.ONE_SHOT)
    PERIODIC = Mode("PERIODIC", machine.Timer.PERIODIC)
  except AttributeError:
    Logging.Log("System.Timer.MODE", Logging.LEVEL.WARNING).warning("machine.Timer constants (ONE_SHOT, PERIODIC) not found. Timer functionality may be limited.")

class IdManager(Enum.Unit):
  """Timer ID manager."""
  def __init__(self, size: int = Utils.UINT16_MAX):
    self.size: int = size
    self.using: set[int] = set()
  def get(self) -> int:
    if len(self.using) >= self.size:
      raise RuntimeError("Timer ID manager is full.")
    rdm = random.randint(0, self.size-1)
    while rdm in self.using:
      rdm = random.randint(0, self.size-1)
    self.using.add(rdm)
    return rdm
  def free(self, id: int) -> None:
    if id in self.using:
        self.using.remove(id)

class MachineTimer: 
  """
  A wrapper class for MicroPython's machine.Timer, providing a robust
  interface for hardware timers with integrated logging.

  This class encapsulates the low-level machine.Timer functionality,
  making it easier to manage periodic or one-shot hardware-driven events
  within the MicroPython_ESP32_lib framework.
  """
  idManager = IdManager(4)

  def __init__(self, id: int, log_name: str = "MachineTimer", log_level: Logging.Level = Logging.LEVEL.INFO):
    """
    Constructs a new Timer object.

    Args:
      id (int, optional): The ID of the hardware timer. Assigns a random ID if id < 0.
      log_name (str, optional): The name to use for the logger. Defaults to "MachineTimer".
      log_level (Logging.Level, optional): The log level for this timer instance. Defaults to Logging.LEVEL.INFO.
    """
    self._timer_id = id if id >= 0 else MachineTimer.idManager.get()
    self.logger = Logging.Log(f"{log_name}({id})", log_level)
    self.active = False

    try:
      self._timer_obj = machine.Timer(id)
      self.logger.debug(f"Created successfully.")
    except Exception as e:
      self.logger.error(f"Failed to create: {e}. Timer functionality will be unavailable.")
      self._timer_obj = None # Ensure it's None if creation failed
      raise e

  def init(self, period_ms: int, callback, mode: Mode = MODE.PERIODIC) -> None:
    """
    Initialises the timer with the given parameters.

    Args:
      mode (Mode): The timer operating mode (ONE_SHOT or PERIODIC).
      period_ms (int): The timer period in milliseconds.
      callback (callable, optional): The function to call upon timer expiration. Must take one argument (the Timer object itself). Defaults to None, which will cause a TypeError upon timer expiration if not changed.

    Raises:
      RuntimeError: If the underlying machine.Timer object was not created successfully.
      ValueError: if neither freq nor period is specified, or if callback is None.
      Exception: Catches and re-raises any exception from machine.Timer.init().
    """
    if self._timer_obj is None:
      self.logger.error("Attempted to init a Timer that failed to be created.")
      raise RuntimeError("Timer object not initialized.")

    try:
      self._timer_obj.init(mode=mode.value, period=period_ms, callback=callback)
      self.active = True
      self.logger.info(f"Initialized successfully. Mode: {mode.name}, Period: {period_ms}ms.")
    except Exception as e:
      self.logger.error(f"Failed to initialize Timer: {e}")
      raise e

  def deinit(self) -> None:
    """
    Deinitialises the timer. Stops the timer and disables the timer peripheral.

    Raises:
      RuntimeError: If the underlying machine.Timer object was not created successfully.
      Exception: Catches and re-raises any exception from machine.Timer.deinit().
    """
    if self._timer_obj is None:
      self.logger.warning("Attempted to deinit a Timer that failed to be created or is already deinitialized.")
      # Do not raise an error here, just log and return to allow cleanup to proceed.
      return

    try:
      self._timer_obj.deinit()
      self.active = False
      self.logger.info(f"Timer {self._timer_id} deinitialized successfully.")
    except Exception as e:
      self.logger.error(f"Failed to deinitialize Timer {self._timer_id}: {e}")
      raise e
  def __del__(self):
    self.deinit()
    # self._timer_obj = None # Timer object is managed by machine module.
    MachineTimer.idManager.free(self._timer_id) # Free the ID
    self.logger.debug(f"Timer {self._timer_id} deleted.")
  
  def __str__(self):
    return f"Timer({self._timer_id})"
    # return f"{self._timer_id}"
  def __repr__(self):
    return self.__str__()

if __name__ == '__main__':
  try:
    from . import Time
  except ImportError:
    from micropython_esp32_lib.System import Time

  def test_callback_function(timer_obj):
    Logging.Log("Callback", Logging.LEVEL.DEBUG).debug(f"Activate Callback for {timer_obj} at {Time.Time()}")
  
  logger = Logging.Log("main_timer_test", Logging.LEVEL.INFO)
  logger.info("Starting System.Timer Wrapper Tests.")
  logger.info("\n\n")

  # Test 1: MachineTimer Periodic timer
  logger.info("Test 1: MachineTimer Periodic Timer (id=1)")
  try:
    timer0 = MachineTimer(id=1, log_level=Logging.LEVEL.DEBUG)
    timer0.init(mode=MODE.PERIODIC, period_ms=100, callback=test_callback_function)
    logger.info(f"Is {timer0} active: {timer0.active}")
    Sleep.sync_ms(1000)
    timer0.deinit()
    logger.info(f"Is {timer0} active after deinit: {timer0.active}")
  except Exception as e:
    logger.error(f"MachineTimer Periodic Test failed: {e}")
  logger.info("\n\n")

  # Test 2: MachineTimer One-shot timer
  logger.info("Test 2: MachineTimer One-Shot Timer (id=2)")
  try:
    timer1 = MachineTimer(id=2, log_level=Logging.LEVEL.INFO)
    timer1.init(mode=MODE.ONE_SHOT, period_ms=100, callback=test_callback_function)
    logger.info(f"Is {timer1} active: {timer1.active}")
    Sleep.sync_ms(1000) # Wait long enough for it to fire and self-deinit
    logger.info(f"Is {timer1} active after wait: {timer1.active}")
    # Cleanup only if it hasn't finished (shouldn't happen in this test)
    if timer1.active:
      logger.warning("One-Shot MachineTimer did not self-terminate! Calling deinit.")
      timer1.deinit()
  except Exception as e:
    logger.error(f"MachineTimer One-Shot Test failed: {e}")
  logger.info("\n\n")

  logger.info("All Timer Wrapper Tests completed.")


async def asyncTimer(interval_ms: int, callback, callback_args: tuple = (), callback_kwargs: dict = {}, repeat: bool = False, log_name: str = "AsyncTimer", log_level: Logging.Level = Logging.LEVEL.INFO) -> asyncio.Task:
  logger = Logging.Log(f"{log_name}", log_level)
  logger.debug(f"Creating async timer with interval {interval_ms}ms.")
  async def timer_task():
    # logger.debug(f"Async timer started with interval {interval_ms}ms.")
    # await Sleep.async_ms(interval_ms)
    # logger.debug(f"Async timer executing callback after {interval_ms}ms.")
    # if inspect.iscoroutinefunction(callback):
    #   await callback(*callback_args, **callback_kwargs)
    # else:
    #   callback(*callback_args, **callback_kwargs)
    # logger.debug(f"Async timer callback execution completed.")
    while True:
      await Sleep.async_ms(interval_ms)
      logger.debug(f"Async timer executing callback after {interval_ms}ms.")
      if inspect.iscoroutinefunction(callback):
        await callback(*callback_args, **callback_kwargs)
      else:
        callback(*callback_args, **callback_kwargs)
      logger.debug(f"Async timer callback execution completed.")
      if not repeat:
        break
  logger.debug(f"Async timer task created.")
  task = asyncio.create_task(timer_task())
  return task


if __name__ == '__main__':
  async def callback1():
    Logging.Log("callback_function", Logging.LEVEL.INFO).info("Async Timer Callback Executed.")
  async def callback2(arg1, arg2, arg3):
    Logging.Log("callback_function", Logging.LEVEL.INFO).info(f"Async Timer Callback Executed. callback2({arg1}, {arg2}, {arg3})")
  logger = Logging.Log("main", Logging.LEVEL.INFO)
  logger.info("Starting Async Timer Test.")
  async def main():
    logger = Logging.Log("async_main", Logging.LEVEL.INFO)
    logger.info("Scheduling Async Timer for 2000ms.")
    await asyncTimer(1000, callback1, repeat=True, log_name="asyncTimer1", log_level=Logging.LEVEL.DEBUG)
    await asyncTimer(1500, lambda: Logging.Log("callback_lambda", Logging.LEVEL.INFO).info("Async Timer Callback Executed."), repeat=True, log_name="asyncTimer2", log_level=Logging.LEVEL.DEBUG)
    await asyncTimer(2000, callback2, (1, 2, 3), repeat=False, log_name="asyncTimer3", log_level=Logging.LEVEL.DEBUG)
    await asyncTimer(2500, lambda arg1, arg2, arg3: Logging.Log("callback_lambda", Logging.LEVEL.INFO).info(f"Async Timer Callback Executed. callback2({arg1}, {arg2}, {arg3})"), (4, 5, 6), repeat=False, log_name="asyncTimer4", log_level=Logging.LEVEL.DEBUG)
    logger.info("Async Timer Scheduled for 2000ms.")
    await Sleep.async_ms(3000)
    logger.info("Async Timer Test Scheduled.")
  asyncio.run(main())
  logger.info("Async Timer Test Completed.")

class AsyncTimer:
  def __init__(self, interval_ms: int, callback, callback_args: tuple = (), callback_kwargs: dict = {}, repeat: bool = False, start: bool = True, log_name: str = "AsyncTimer", log_level: Logging.Level = Logging.LEVEL.INFO):
    self.logger = Logging.Log(f"{log_name}", log_level)
    self.active = False
    self._timer_task: asyncio.Task | None = None
    self.interval_ms = interval_ms
    self.callback = callback
    self.callback_args = callback_args
    self.callback_kwargs = callback_kwargs
    self.repeat = repeat
    self.logger.debug(f"Created successfully.")
    if start: self.start()
  async def _run_timer(self):
    self.active = True
    self.logger.debug(f"Async timer started with interval {self.interval_ms}ms. Repeat: {self.repeat}")
    while self.active:
      await Sleep.async_ms(self.interval_ms)
      self.logger.debug(f"Async timer executing callback after {self.interval_ms}ms.")
      if inspect.iscoroutinefunction(self.callback):
        await self.callback(*self.callback_args, **self.callback_kwargs)
      else:
        self.callback(*self.callback_args, **self.callback_kwargs)
      self.logger.debug(f"Async timer callback execution completed.")
      if not self.repeat:
        break
    self.active = False
    self.logger.debug(f"Async timer stopped.")
  def start(self):
    if not self.active:
      self._timer_task = asyncio.create_task(self._run_timer())
      self.logger.debug(f"Async timer task started.")
  def stop(self):
    if self.active:
      self.active = False
      if self._timer_task: self._timer_task.cancel()
      self.logger.debug(f"Async timer task stopped.")
    else:
      self.logger.debug(f"Async timer task already stopped.")
    self._timer_task = None
    self.logger.debug(f"Async timer task reference cleared.")
    self.logger.debug(f"Async timer stopped.")
  def restart(self):
    self.stop()
    self.start()
  def __del__(self):
    self.stop()
    self.logger.debug(f"Async timer deleted.")

if __name__ == '__main__':
  async def callback1():
    Logging.Log("callback_function", Logging.LEVEL.INFO).info("AsyncTimer Class Callback Executed.")
  async def callback2(arg1, arg2, arg3):
    Logging.Log("callback_function", Logging.LEVEL.INFO).info(f"AsyncTimer Class Callback Executed. callback2({arg1}, {arg2}, {arg3})")
  logger = Logging.Log("main", Logging.LEVEL.INFO)
  logger.info("Starting AsyncTimer Class Test.")
  async def main():
    logger = Logging.Log("async_main", Logging.LEVEL.INFO)
    logger.info("Creating AsyncTimer instances.")
    timer1 = AsyncTimer(1000, callback1, log_name="AsyncTimerClass1", log_level=Logging.LEVEL.DEBUG, repeat=True)
    timer2 = AsyncTimer(1500, lambda: Logging.Log("callback_lambda", Logging.LEVEL.INFO).info("AsyncTimer Class Callback Executed."), log_name="AsyncTimerClass2", log_level=Logging.LEVEL.DEBUG, repeat=True)
    timer3 = AsyncTimer(2000, callback2, (1, 2, 3), log_name="AsyncTimerClass3", log_level=Logging.LEVEL.DEBUG, repeat=False)
    timer4 = AsyncTimer(2500, lambda arg1, arg2, arg3: Logging.Log("callback_lambda", Logging.LEVEL.INFO).info(f"AsyncTimer Class Callback Executed. callback2({arg1}, {arg2}, {arg3})"), (4, 5, 6), log_name="AsyncTimerClass4", log_level=Logging.LEVEL.DEBUG, repeat=False)
    logger.info("AsyncTimer instances created and started.")
    await Sleep.async_ms(7000)
    logger.info("Stopping AsyncTimer instances.")
    timer1.stop()
    timer2.stop()
    logger.info("AsyncTimer Class Test Completed.")
  asyncio.run(main())
  logger.info("AsyncTimer Class Test Finished.")