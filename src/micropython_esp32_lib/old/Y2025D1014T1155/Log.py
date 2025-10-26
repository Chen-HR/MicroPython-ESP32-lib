try: 
  from . import SystemTime
except ImportError:
  from HRChen import SystemTime

class Log:
  """Logging Utility Class"""
  LEVEL_DEBUG = 0
  LEVEL_INFO = 1
  LEVEL_WARNING = 2
  LEVEL_ERROR = 3
  LEVEL_NONE = 4

  level_names = {
    LEVEL_DEBUG: "DEBUG",
    LEVEL_INFO: "INFO",
    LEVEL_WARNING: "WARNING",
    LEVEL_ERROR: "ERROR",
    LEVEL_NONE: "NONE"
  }

  def __init__(self, name: str, level: int = LEVEL_INFO):
    self.name = name
    self.level = level    

  def debug(self, message: str) -> None:
    """Log a debug message"""
    if self.level <= self.LEVEL_DEBUG:
      print(f"[{SystemTime.Time()}] [{self.name}] [DEBUG] {message}")

  def info(self, message: str) -> None:
    """Log an info message"""
    if self.level <= self.LEVEL_INFO:
      print(f"[{SystemTime.Time()}] [{self.name}] [INFO] {message}")

  def warning(self, message: str) -> None:
    """Log a warning message"""
    if self.level <= self.LEVEL_WARNING:
      print(f"[{SystemTime.Time()}] [{self.name}] [WARNING] {message}")

  def error(self, message: str) -> None:
    """Log an error message"""
    if self.level <= self.LEVEL_ERROR:
      print(f"[{SystemTime.Time()}] [{self.name}] [ERROR] {message}")