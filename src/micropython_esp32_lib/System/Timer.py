# src/micropython_esp32_lib/System/Timer.py
import machine

try:
  from . import Logging
  from . import Enum
except ImportError:
  from micropython_esp32_lib.System import Logging
  from micropython_esp32_lib.System import Enum

class Mode(Enum.Unit):
  """Timer operating modes."""
  pass
class MODE:
  try:
    ONE_SHOT = Mode("ONE_SHOT", machine.Timer.ONE_SHOT)
    PERIODIC = Mode("PERIODIC", machine.Timer.PERIODIC)
  except AttributeError:
    Logging.Log("System.Timer.MODE", Logging.LEVEL.WARNING).warning("machine.Timer constants (ONE_SHOT, PERIODIC) not found. Timer functionality may be limited.")

class Timer:
  """
  A wrapper class for MicroPython's machine.Timer, providing a robust
  interface for hardware timers with integrated logging.

  This class encapsulates the low-level machine.Timer functionality,
  making it easier to manage periodic or one-shot hardware-driven events
  within the MicroPython_ESP32_lib framework.
  """

  def __init__(self, id: int, log_name: str = "Timer", log_level: Logging.Level = Logging.LEVEL.INFO):
    """
    Constructs a new Timer object.

    Args:
      id (int, optional): The ID of the hardware timer. -1 typically constructs a virtual timer. Defaults to -1.
      log_name (str, optional): The name to use for the logger. Defaults to "Timer".
      log_level (Logging.Level, optional): The log level for this timer instance. Defaults to Logging.LEVEL.INFO.
    """
    self._timer_id = id
    # self._timer_obj = None
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
      self.logger.info(f"Initialized successfully.")
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
      raise RuntimeError("Timer object not initialized.")

    try:
      self._timer_obj.deinit()
      self.active = False
      self.logger.info(f"Timer {self._timer_id} deinitialized successfully.")
    except Exception as e:
      self.logger.error(f"Failed to deinitialize Timer {self._timer_id}: {e}")
      raise e
  def __del__(self):
    self.deinit()
    self._timer_obj = None
    self.logger.debug(f"Timer {self._timer_id} deleted.")
  
  def __str__(self):
    return f"Timer({self._timer_id})"
    # return f"{self._timer_id}"
  def __repr__(self):
    return self.__str__()

if __name__ == '__main__':
  try:
    from . import Sleep
  except ImportError:
    from micropython_esp32_lib.System import Sleep

  def test_callback_function(timer_obj):
    Logging.Log("Callback", Logging.LEVEL.DEBUG).debug(f"Activate Callback for {timer_obj}")
  
  logger = Logging.Log("main", Logging.LEVEL.DEBUG)
  logger.debug("Testing System.Timer Wrapper")
  logger.debug("\n\n")

  # Test 1: Periodic timer
  logger.debug("Test 1: Periodic Timer (id=0)")
  timer0 = Timer(id=1, log_level=Logging.LEVEL.DEBUG)
  timer0.init(mode=MODE.PERIODIC, period_ms=100, callback=test_callback_function)
  logger.debug(f"Is {timer0} active: {timer0.active}")
  Sleep.sync_ms(1000)
  timer0.deinit()
  logger.debug(f"Is {timer0} active after deinit: {timer0._timer_obj is not None and timer0.active}")
  logger.debug("\n\n")

  # Test 2: One-shot timer
  logger.debug("Test 2: One-Shot Timer (id=1)")
  timer1 = Timer(id=2, log_level=Logging.LEVEL.INFO)
  timer1.init(mode=MODE.ONE_SHOT, period_ms=100, callback=test_callback_function)
  logger.debug(f"Is {timer1} active: {timer1.active}")
  Sleep.sync_ms(1000)
  timer1.deinit()
  logger.debug(f"Is {timer1} active after deinit: {timer1._timer_obj is not None and timer1.active}")
  logger.debug("\n\n")
