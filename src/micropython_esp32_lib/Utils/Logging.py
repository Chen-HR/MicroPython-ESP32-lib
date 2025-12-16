"""
# file: ./Utils/Logging.py
"""
# TODO: add async support

import abc
import sys
# import logging # Type hints will not be available if this code inherits from logging.
# from typing import IO, TextIO, Never

try: 
  from ..System import Time
except ImportError:
  from micropython_esp32_lib.System import Time

_log_linefmt: str = "[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s"
_log_timefmt: str = Time.Formater.String.DEFAULT_MS.formater
_log_stream: sys.TextIO = sys.stderr # type: ignore

try:
  from ..System.Lock import allocate_lock, Lock
except ImportError:
  from micropython_esp32_lib.System.Lock import allocate_lock, Lock
_log_locker: Lock = allocate_lock() # type: ignore

class Level:
  def __init__(self, code: int, name: str):
    self.code: int = code
    self.name: str = name
  def __str__(self) -> str:
    return f"Level({self.code}, {self.name})"
  def __eq__(self, other: "Level") -> bool: # type: ignore
    return self.code == other.code and self.name == other.name
  @classmethod
  def query(cls, code: int) -> "Level":
    for pull in cls.__dict__.values():
      if isinstance(pull, cls):
        if pull.code == code:
          return pull
    raise ValueError(f"Unknown level code: {code}")
  CRITICAL : "Level"
  ERROR    : "Level"
  WARNING  : "Level"
  INFO     : "Level"
  DEBUG    : "Level"
  NOTSET   : "Level"
Level.CRITICAL = Level(50, "CRITICAL")
Level.ERROR    = Level(40, "ERROR")
Level.WARNING  = Level(30, "WARNING")
Level.INFO     = Level(20, "INFO")
Level.DEBUG    = Level(10, "DEBUG")
Level.NOTSET   = Level(0, "NOTSET")
_log_level: Level = Level.WARNING

class Record:
  def set(self, name: str, level: Level, message: str):
    self.name: str = name
    self.levelno: int = level.code
    self.levelname: str = level.name
    self.message: str = message
    self.currentTime_ns: Time.Time = Time.Time(Time.current_ns())
    self.asctime: str = ""

class Formatter:
  # def __init__(self, linefmt: str = _log_linefmt, timefmt: str = _log_timefmt):
  #   self.linefmt = linefmt
  #   self.timefmt = timefmt
  # def usesTime(self):
  #   return "asctime" in self.linefmt
  @staticmethod
  def formatTime(timefmt: str, record: Record) -> str:
    return Time.Formater.format(record.currentTime_ns, Time.Formater.String(timefmt))
  @staticmethod
  def format(record: Record, linefmt: str = _log_linefmt, timefmt: str = _log_timefmt) -> str:
    if "asctime" in linefmt:
      record.asctime = Formatter.formatTime(timefmt, record)
    return linefmt % {
      "name": record.name,
      "levelname": record.levelname,
      "levelno": record.levelno,
      "message": record.message,
      "asctime": record.asctime
    }

class Handler(abc.ABC):
  def __init__(self, level: Level = Level.NOTSET, formatter = Formatter):
    self.level = level
    self.formatter = formatter
  @abc.abstractmethod
  def close(self):
    pass
  def setLevel(self, level: Level):
    self.level = level
  def setFormatter(self, formatter):
    self.formatter = formatter
  def format(self, record: Record):
    return self.formatter().format(record) # type: ignore
  @abc.abstractmethod
  def emit(self, record: Record):
    pass
class StreamHandler(Handler): # redo from logging.StreamHandler
  def __init__(self, stream = _log_stream, terminator: str = "\n"):
    """
    Args:
        stream (IO, optional): The stream to write the log messages to. Defaults. Defaults to _log_stream.
        terminator (str, optional): The string to append at the end of each log. Defaults to "\\n".
    """
    super().__init__()
    self.stream = stream
    self.terminator = terminator
  def close(self):
    if hasattr(self.stream, "flush"):
      self.stream.flush() # type: ignore
  def emit(self, record: Record):
    if record.levelno >= self.level.code:
      global _log_locker
      try:
        _log_locker.acquire()
        self.stream.write(self.format(record) + self.terminator) # type: ignore
      except Exception as e:
        raise e
      finally:
        _log_locker.release()
class FileHandler(StreamHandler):
  def __init__(self, filename: str, mode: str="a", encoding: str="UTF-8"):
    super().__init__(stream=open(filename, mode=mode, encoding=encoding))
  def close(self):
    super().close()
    self.stream.close()

class Logger:
  def __init__(self, name: str, level: Level = _log_level, handlers: list[Handler] = []):
    self.name: str = name
    self.level: Level = level
    self.handlers: list[Handler] = handlers
    self.record = Record()
  def setLevel(self, level: Level):
    self.level = level
  def getEffectiveLevel(self):
    return self.level or getLogger().level or _log_level
  def isEnabledFor(self, level: Level) -> bool:
    return level.code >= self.getEffectiveLevel().code
  def addHandler(self, handler):
    self.handlers.append(handler)
  def hasHandlers(self) -> bool:
    return len(self.handlers) > 0
  def log(self, level: Level, msg: str, *args):
    if self.isEnabledFor(level):
      if args:
        if isinstance(args[0], dict):
          args = args[0]
        msg = msg % args
      self.record.set(self.name, level, msg)
      handlers = self.handlers
      if not handlers:
        handlers = getLogger().handlers
      for h in handlers:
        h.emit(self.record)
  def notset(self, msg: str, *args):
    self.log(Level.NOTSET, msg, *args)
  def debug(self, msg: str, *args):
    self.log(Level.DEBUG, msg, *args)
  def info(self, msg: str, *args):
    self.log(Level.INFO, msg, *args)
  def warning(self, msg: str, *args):
    self.log(Level.WARNING, msg, *args)
  def error(self, msg: str, *args):
    self.log(Level.ERROR, msg, *args)
  def critical(self, msg: str, *args):
    self.log(Level.CRITICAL, msg, *args)
  def exception(self, msg: str, *args, exc_info=True):
    self.log(Level.ERROR, msg, *args)
    # tb: typing.Never | BaseException | None
    tb = None
    if isinstance(exc_info, BaseException):
      tb = exc_info
    elif hasattr(sys, "exc_info"):
      tb = sys.exc_info()[1]
    if tb:
      buf = io.StringIO() # type: ignore
      sys.print_exception(tb, buf) # type: ignore
      self.log(Level.ERROR, buf.getvalue()) # type: ignore
_loggers: dict[str, Logger] = {}

def config_stream(name: str | None = None, stream = _log_stream, level: Level = _log_level):
  """_summary_

  Args:
    name (str | None, optional): The name of the logger. Defaults to None.
    stream (typing.IO, optional): The stream to write the log messages to. Defaults to _log_stream.
    level (Level, optional): The level of the logger. Defaults to _log_level.
  """
  global _loggers
  if name is None: name = "root"
  if name not in _loggers: 
    _loggers[name] = Logger(name, level, [StreamHandler(stream)])
  else:
    _loggers[name].setLevel(level)
    _loggers[name].addHandler(StreamHandler(stream))
def config_file(name: str | None = None, filename: str | None = None, filemode: str = "a", encoding: str = "UTF-8", level: Level = _log_level):
  global _loggers
  if name is None: name = "root"
  if filename is None: filename = f"{name}.log"
  if name not in _loggers: 
    _loggers[name] = Logger(name, level, [FileHandler(filename, filemode, encoding)])
  else:
    _loggers[name].setLevel(level)
    _loggers[name].addHandler(FileHandler(filename, filemode, encoding))

def getLogger(name: str | None = None):
  global _loggers
  if name is None: name = "root"
  if name not in _loggers:
    _loggers[name] = Logger(name)
    if name == "root": config_stream()
  return _loggers[name]

def shutdown():
  keys = list(_loggers.keys())
  for k in keys:
    logger = _loggers.get(k)
    if not logger:
      continue
    for h in logger.handlers:
      h.close()
    _loggers.pop(k, None)

if hasattr(sys, "atexit"):
  sys.atexit(shutdown) # type: ignore

def log(level: Level, message: str, *args):
  getLogger().log(level, message, *args)
def notset(message: str, *args):
  getLogger().notset(message, *args)
def debug(message: str, *args):
  getLogger().debug(message, *args)
def info(message: str, *args):
  getLogger().info(message, *args)
def warning(message: str, *args):
  getLogger().warning(message, *args)
def error(message: str, *args):
  getLogger().error(message, *args)
def critical(message: str, *args):
  getLogger().critical(message, *args)

if __name__ == "__main__": # pragma: no cover
  logger = getLogger()
  logger.notset("Notset message.")
  logger.debug("Debug message.")
  logger.info("Info message.")
  logger.warning("Warning message.")
  logger.error("Error message.")
  logger.critical("Critical message.")