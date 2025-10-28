# src/micropython_esp32_lib/System/Timer.py
import machine
import random
import _thread as thread
import asyncio
import inspect

try:
  from . import Logging
  from . import Enum
  from . import Utils
except ImportError:
  from micropython_esp32_lib.System import Logging
  from micropython_esp32_lib.System import Enum
  from micropython_esp32_lib.System import Utils

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


class AsyncTimer: 
  """
  A timer implementation based on asyncio.sleep for non-blocking,
  event-loop driven periodic or one-shot events.
  """
  idManager = IdManager(Utils.UINT16_MAX)
  def __init__(self, id: int, log_name: str = "AsyncTimer", log_level: Logging.Level = Logging.LEVEL.INFO):
    self._timer_id = id if id >= 0 else AsyncTimer.idManager.get()
    self.logger = Logging.Log(f"{log_name}({self._timer_id})", log_level)
    self.active = False
    self._timer_task: asyncio.Task | None = None
    self.logger.debug(f"Created successfully.")
  
  async def _timer_loop(self, period_ms: int, callback, repeat: bool):
    """The coroutine that manages the timing and callback execution."""
    period_s = period_ms / 1000.0
    while True:
      try:
        await asyncio.sleep(period_s)
        # Execute the callback, handling both async and sync functions
        if inspect.iscoroutinefunction(callback): 
          await callback(self) # Pass self (the Timer object) as argument
        else: 
          callback(self) # Pass self (the Timer object) as argument
        if not repeat:
          break # Exit loop for ONE_SHOT mode
      except asyncio.CancelledError:
        self.logger.debug(f"Timer {self._timer_id} task cancelled.")
        break
      except Exception as e:
        self.logger.error(f"Error in AsyncTimer loop: {e}")
        if not repeat: 
          break # Break on error for ONE_SHOT mode
        await asyncio.sleep(1) # Add a small delay before continuing on error in PERIODIC mode
    self.active = False
    self._timer_task = None
    self.logger.info(f"Timer {self._timer_id} loop finished.")

  def init(self, period_ms: int, callback, mode: Mode = MODE.PERIODIC) -> None:
    """
    Initialises the timer with the given parameters and starts the asyncio task.
    This method is idempotent: if a timer is already active, it will be deinitialized
    before a new one is started.

    Args:
      mode (Mode): The timer operating mode (ONE_SHOT or PERIODIC).
      period_ms (int): The timer period in milliseconds.
      callback (callable): The function to call upon timer expiration. Must take one argument (the Timer object itself).

    Raises:
      ValueError: If period_ms is not positive or callback is None.
    """
    # If an existing task is running or done, clean it up before starting a new one.
    if self._timer_task is not None:
        if not self._timer_task.done(): # Task is still pending/running
            self.deinit() # Cancel and clean up the old task
        else: # Task is done, just clear the reference
            self._timer_task = None
            self.active = False # Ensure active flag is consistent

    if period_ms <= 0:
      raise ValueError("Timer period_ms must be a positive integer.")
    if callback is None:
      raise ValueError("Callback function must be provided.")
    
    repeat = (mode == MODE.PERIODIC)
    try:
      self._timer_task = asyncio.create_task(
        self._timer_loop(period_ms, callback, repeat)
      )
      self.active = True
      self.logger.info(f"Initialized successfully. Mode: {mode.name}, Period: {period_ms}ms.")
    except Exception as e:
      self.logger.error(f"Failed to initialize AsyncTimer: {e}")
      self._timer_task = None
      self.active = False
      raise e

  def deinit(self) -> None:
    """
    Deinitialises the timer. Stops the associated asyncio task.
    """
    if self._timer_task is None:
        self.logger.debug("Attempted to deinit an AsyncTimer with no task.")
        self.active = False
        return
    
    if self._timer_task.done():
        self.logger.debug("Attempted to deinit an AsyncTimer whose task is already done.")
        self._timer_task = None
        self.active = False
        return
    
    try:
      self._timer_task.cancel()
      # Give a very short time for cancellation to propagate, but don't await.
      # This is crucial for synchronous deinit calls.
      # However, for ISR context, even this might be too much.
      # The _timer_loop itself will eventually set active=False.
      self.active = False # Set active to False immediately, but final cleanup is async.
      self.logger.info(f"Timer {self._timer_id} deinitialized (task cancellation requested).")
    except Exception as e:
      self.logger.error(f"Failed to deinitialize Timer {self._timer_id}: {e}")
  
  def __del__(self):
    if self._timer_task is not None and not self._timer_task.done():
      try:
        self.deinit() # Request cancellation if still active
      except Exception as e:
        self.logger.error(f"Error during AsyncTimer {self._timer_id} deletion cleanup: {e}")
    AsyncTimer.idManager.free(self._timer_id)
    self._timer_task = None
    self.active = False
    self.logger.debug(f"Timer {self._timer_id} deleted.")
  
  def __str__(self):
    return f"AsyncTimer({self._timer_id}, active={self.active})"
  def __repr__(self):
    return self.__str__()

if __name__ == '__main__':
  try:
    from . import Sleep
    from . import Time
  except ImportError:
    from micropython_esp32_lib.System import Sleep
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
  
  # Asynchronous Test Wrapper
  async def async_test_suite():
    logger = Logging.Log("async_test_main", Logging.LEVEL.INFO)
    logger.info("\n\n")

    # --- Test 3: AsyncTimer Periodic timer ---
    logger.info("Test 3: AsyncTimer Periodic Timer (id=1)")
    try:
      timer0_async = AsyncTimer(id=1, log_level=Logging.LEVEL.DEBUG) 
      timer0_async.init(mode=MODE.PERIODIC, period_ms=100, callback=test_callback_function)
      logger.info(f"Is {timer0_async} active: {timer0_async.active}")
      await asyncio.sleep(1.0) # Non-blocking wait, allows the timer task to run
      timer0_async.deinit()
      logger.info(f"Is {timer0_async} active after deinit: {timer0_async.active}")
    except Exception as e:
      logger.error(f"AsyncTimer Periodic Test failed: {e}")
    logger.info("\n\n")

    # --- Test 4: AsyncTimer One-shot timer (Corrected for self-termination) ---
    logger.info("Test 4: AsyncTimer One-Shot Timer (id=2) - Self-Termination Check")
    try:
      timer1_async = AsyncTimer(id=2, log_level=Logging.LEVEL.DEBUG)
      timer1_async.init(mode=MODE.ONE_SHOT, period_ms=100, callback=test_callback_function)
      logger.info(f"Is {timer1_async} active: {timer1_async.active}")
      await asyncio.sleep(0.15) # Wait 150ms > 100ms
      logger.info(f"Is {timer1_async} active after 150ms: {timer1_async.active}")
      if timer1_async.active:
        logger.warning("One-Shot AsyncTimer did not self-terminate! Calling deinit.")
        timer1_async.deinit()
    except Exception as e:
      logger.error(f"AsyncTimer One-Shot Test failed: {e}")
    logger.info("\n\n")

    # --- Test 5: AsyncTimer Re-init idempotency ---
    logger.info("Test 5: AsyncTimer Re-init Idempotency Test (id=3)")
    try:
        reinit_timer = AsyncTimer(id=3, log_level=Logging.LEVEL.DEBUG)
        
        logger.info("  First init (periodic 200ms)...")
        reinit_timer.init(mode=MODE.PERIODIC, period_ms=200, callback=lambda t: Logging.Log("ReinitCallback", Logging.LEVEL.DEBUG).debug("Callback 200ms"))
        await asyncio.sleep(0.3) # Let it run for a bit
        logger.info(f"  Timer active: {reinit_timer.active}. Task: {reinit_timer._timer_task}")

        logger.info("  Second init (periodic 50ms) - should cancel first and start new.")
        reinit_timer.init(mode=MODE.PERIODIC, period_ms=50, callback=lambda t: Logging.Log("ReinitCallback", Logging.LEVEL.DEBUG).debug("Callback 50ms"))
        await asyncio.sleep(0.2) # Let new timer run
        logger.info(f"  Timer active: {reinit_timer.active}. Task: {reinit_timer._timer_task}")
        reinit_timer.deinit()
        logger.info(f"  Timer active after deinit: {reinit_timer.active}")
    except Exception as e:
        logger.error(f"AsyncTimer Re-init Idempotency Test failed: {e}")
    logger.info("\n\n")


  # --- Run AsyncTimer Tests ---
  logger.info("Running AsyncTimer Tests...")
  try:
    asyncio.run(async_test_suite()) 
  except KeyboardInterrupt:
    logger.info("Asyncio test suite interrupted.")
  finally:
    logger.info("AsyncTimer Tests finished.")
  
  logger.info("All Timer Wrapper Tests completed.")