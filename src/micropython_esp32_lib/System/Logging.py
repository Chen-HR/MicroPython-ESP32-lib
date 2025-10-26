# System/Logging.py
try: 
  from . import Time
  from . import Sleep
  from . import Code
except ImportError:
  from MicroPython_ESP32_lib.System import Time
  from MicroPython_ESP32_lib.System import Sleep
  from MicroPython_ESP32_lib.System import Code

# --- Log Handler Interface (DIP) ---
class LogHandler:
  """Abstract base class for log output handlers (OCP)."""
  def emit(self, record: str) -> None:
    """Outputs the formatted log record."""
    raise NotImplementedError

class ConsoleHandler(LogHandler):
  """Default handler that prints to the console."""
  def emit(self, record: str) -> None:
    print(record)

_log_lock = None
try:
  from _thread import allocate_lock
  class Lock: # Placeholder for type consistency
    def acquire(self, waitflag: int = 1, timeout: float = -1): 
      pass
    def release(self): 
      pass
    def locked(self): 
      pass
  _log_lock: Lock = allocate_lock()
except Exception:
  class Lock_Implementation:
    """A simple mock lock for demonstration purposes.

    Reference: <https://docs.micropython.org/en/latest/library/_thread.html> -> <https://docs.python.org/3.5/library/_thread.html#module-_thread>

    Lock objects have the following methods:

    ## `lock.acquire(waitflag=1, timeout=-1)`
    Without any optional argument, this method acquires the lock unconditionally, if necessary waiting until it is released by another thread (only one thread at a time can acquire a lock — that’s their reason for existence).

    If the integer waitflag argument is present, the action depends on its value: if it is zero, the lock is only acquired if it can be acquired immediately without waiting, while if it is nonzero, the lock is acquired unconditionally as above.

    If the floating-point timeout argument is present and positive, it specifies the maximum wait time in seconds before returning. A negative timeout argument specifies an unbounded wait. You cannot specify a timeout if waitflag is zero.

    The return value is True if the lock is acquired successfully, False if not.

    Changed in version 3.2: The timeout parameter is new.

    Changed in version 3.2: Lock acquires can now be interrupted by signals on POSIX.

    ## `lock.release()`
    Releases the lock. The lock must have been acquired earlier, but not necessarily by the same thread.

    ## `lock.locked()`
    Return the status of the lock: True if it has been acquired by some thread, False if not.
    """
    def __init__(self, start_locked=False):
      """
      Initialize the lock object.

      Args:
        start_locked (bool): Whether the lock should be initially locked (default: False).
      """
      self._locked = start_locked
    def acquire(self, waitflag: int = 1, timeout: float = -1) -> bool:
      """
      Acquires the lock object.

      Args:
        waitflag (int, optional): The wait flag. If 0, the lock is only acquired if it can be acquired immediately without waiting. If nonzero, the lock is acquired unconditionally as above. Defaults to 1.
        timeout (float, optional): The maximum wait time in seconds before returning. A negative timeout argument specifies an unbounded wait. Defaults to -1.

      Returns:
        bool: True if the lock is acquired successfully, False if not.

      Notes:
        If waitflag is zero, the lock is only acquired if it can be acquired immediately without waiting, while if it is nonzero, the lock is acquired unconditionally as above.
        If the floating-point timeout argument is present and positive, it specifies the maximum wait time in seconds before returning. A negative timeout argument specifies an unbounded wait.
      """
      if waitflag != 0:
        if timeout > 0:
          timeout_ms = int(timeout * 1000)
          while self._locked:
            Sleep.sync_ms(1)
            if timeout_ms > 0:
              timeout_ms -= 1
        elif timeout < 0:
          while self._locked:
            Sleep.sync_ms(1)
      if self._locked:
        return False
      self._locked = True
      return True
    def release(self) -> bool:
      """Releases the lock object.

      Returns:
        bool: True if the lock is released successfully, False if not.
      """
      if not self._locked:
        return False
      self._locked = False
      return True
    def locked(self) -> bool:
      """Returns the status of the lock: True if it has been acquired by some thread, False if not.

      Notes:
        This method does not modify the state of the lock.
      """
      return self._locked
  Lock = Lock_Implementation
  def allocate_lock():
    return Lock()
  _log_lock: Lock = allocate_lock()

class Level(Code.Code):
  def __repr__(self) -> str:
    return f"Level({self.name}, {self.code})"
  def lower(self, level) -> bool:
    _level: Level = level
    return self.code < _level.code
class LEVEL:
  DEBUG   = Level.define("DEBUG", 0)
  INFO    = Level.define("INFO", 1)
  WARNING = Level.define("WARNING", 2)
  ERROR   = Level.define("ERROR", 3)
  NONE    = Level.define("NONE", 4)

class Log: 
  time_formatter = Time.Time
  # Set default handler
  handler: LogHandler = ConsoleHandler() 

  @classmethod
  def set_time_formatter(cls, formatter_func):
    cls.time_formatter = formatter_func

  @classmethod
  def set_handler(cls, handler_object: LogHandler):
    """Set a custom log output handler (e.g., FileHandler, SocketHandler)."""
    cls.handler = handler_object

  def __init__(self, name: str, level: Level | None = None):
    if level is None: level = LEVEL.INFO
    self.name = name
    self.level = level    

  def _log(self, level: Level, message: str) -> None:
    if level.lower(self.level):
      return

    try:
      _log_lock.acquire()
      timestamp = self.time_formatter() 
      output = f"[{timestamp}] [{level.name}] [{self.name}] {message}"
      self.handler.emit(output) 
    finally:
      _log_lock.release()

  def debug(self, message: str) -> None:
    self._log(LEVEL.DEBUG, message)

  def info(self, message: str) -> None:
    self._log(LEVEL.INFO, message)

  def warning(self, message: str) -> None:
    self._log(LEVEL.WARNING, message)

  def error(self, message: str) -> None:
    self._log(LEVEL.ERROR, message)

if __name__ == "__main__":
  log = Log("Test Log", LEVEL.INFO)
  log.debug("This is a debug message")
  log.info("This is an info message")
  log.warning("This is a warning message")
  log.error("This is an error message")