"""
# file: ./System/Time/__init__.py
"""
import utime # type: ignore
import machine # type: ignore

try:
  from . import Sleep
except ImportError:
  from micropython_esp32_lib.System.Time import Sleep

TIMEZONE: int = 0 # UTC+0
SECONDS_PER_HOUR: int = 3_600

NS_PER_US: int = 1_000
US_PER_MS: int = 1_000
MS_PER_S:  int = 1_000

NS_PER_MS: int = 1_000_000
US_PER_S:  int = 1_000_000
NS_PER_S:  int = 1_000_000_000

def setTimezone(timezone: int | None = None) -> int:
  """
  Sets the global timezone offset in hours.

  Args:
    timezone (int, optional): The timezone offset in hours.

  Returns:
    int: The global timezone offset in hours.
  """
  global TIMEZONE
  if timezone is None: timezone = 0
  TIMEZONE = timezone
  return TIMEZONE

def make_s(year: int = 2000, month: int = 1, day: int = 1, hour: int = 0, minute: int = 0, second: int = 0, timezone: int = 0) -> float: 
  return utime.mktime((year, month, day, hour, minute, second, 0, 0)) + timezone * SECONDS_PER_HOUR # type: ignore

def setRTC(time_s: int = 0, timezone: int | None = None) -> None:
  """
  Sets the system real-time clock (RTC) to the given time in seconds, with the given timezone offset applied.

  Args:
    time_s (int, optional): The time in seconds. Defaults to 0, which is interpreted as the current time.
    timezone (int, optional): The timezone offset in hours. Defaults to TIMEZONE.

  Notes:
    This function may not work correctly on all MicroPython boards, as RTC handling can vary greatly between boards.
  """
  global TIMEZONE
  if timezone is None: timezone = TIMEZONE
  time_s += timezone * SECONDS_PER_HOUR
  tm = utime.localtime(time_s)
  machine.RTC().datetime((tm[0], tm[1], tm[2], tm[6], tm[3], tm[4], tm[5], utime.ticks_ms())) # type: ignore

def current_s(timezone: int | None = None) -> int:
  """
  Returns the current time in seconds, with the given timezone offset applied.

  Args:
    timezone (int, optional): The timezone offset in hours. Defaults to TIMEZONE.

  Returns:
    int: The current time in seconds, with the given timezone offset applied.
  """
  global TIMEZONE
  if timezone is None: timezone = TIMEZONE
  return int(utime.time()) + timezone * SECONDS_PER_HOUR

def current_ms(timezone: int | None = None) -> int:
  """
  Returns the current time in milliseconds, with the given timezone offset applied.

  Args:
    timezone (int, optional): The timezone offset in hours. Defaults to TIMEZONE.

  Returns:
    int: The current time in milliseconds, with the given timezone offset applied.
  """
  global TIMEZONE
  if timezone is None: timezone = TIMEZONE
  try: return utime.time_ns() // NS_PER_MS + timezone * SECONDS_PER_HOUR * MS_PER_S
  except AttributeError: return current_s(timezone) * MS_PER_S

def current_us(timezone: int | None = None) -> int:
  """
  Returns the current time in microseconds, with the given timezone offset applied.

  Args:
    timezone (int, optional): The timezone offset in hours. Defaults to TIMEZONE.

  Returns:
    int: The current time in microseconds, with the given timezone offset applied.
  """
  global TIMEZONE
  if timezone is None: timezone = TIMEZONE
  try: return utime.time_ns() // NS_PER_US + timezone * SECONDS_PER_HOUR * US_PER_S
  except AttributeError: return current_s(timezone) * US_PER_S

def current_ns(timezone: int | None = None) -> int:
  """
  Returns the current time in nanoseconds, with the given timezone offset applied.

  Args:
    timezone (int, optional): The timezone offset in hours. Defaults to TIMEZONE.

  Returns:
    int: The current time in nanoseconds, with the given timezone offset applied.
  """
  global TIMEZONE
  if timezone is None: timezone = TIMEZONE
  try: return utime.time_ns() + timezone * SECONDS_PER_HOUR * NS_PER_S
  except AttributeError: return current_s(timezone) * NS_PER_S

class Time:
  """
  Represents a point in time with nanosecond precision.
  The Time object is immutable once created.
  """
  
  def __init__(self, time_ns: int | None = None, timezone: int | None = None):
    """
    Initializes a Time object from a given time in nanoseconds and timezone offset in hours.

    Args:
      time_ns (int, optional): The time in nanoseconds. Defaults to 0, which is interpreted as the current time.
      timezone (int, optional): The timezone offset in hours. Defaults to TIMEZONE.
      format (str, optional): The format string for the Time object's __str__() method. Defaults to Formater.DEFAULT_NS.

    The Time object is immutable once created.
    """
    global TIMEZONE
    if timezone is None: timezone = TIMEZONE
    self.nanosecond_total: int = current_ns(timezone) if time_ns is None else time_ns
    
    # 1. Second component from epoch
    self.second_from_epoch: int = self.nanosecond_total // NS_PER_S

    # 2. Time tuple (localtime expects seconds from epoch)
    # utime.localtime includes the local time offset (timezone * SECONDS_PER_HOUR) already applied in current_ns
    self.tm: tuple[int, int, int, int, int, int, int, int] = utime.localtime(self.second_from_epoch) # type: ignore # (year, month, day, hour, minute, second, weekday, yearday) ref https://docs.micropython.org/en/v1.15/library/utime.html
    
    # Date/Time Components (Derived from tm)
    self.year: int = self.tm[0]
    self.month: int = self.tm[1]
    self.day: int = self.tm[2]
    self.hour: int = self.tm[3]
    self.minute: int = self.tm[4]
    self.second: int = self.tm[5] # Second component (0-59)
    self.weekday: int = self.tm[6] # 0~6
    self.yearday: int = self.tm[7] # 1~366
    
    # 3. Sub-second components (Cleaned and simplified calculation)
    total_ns_of_second: int = self.nanosecond_total % NS_PER_S # 0 to 999,999,999
    
    self.millisecond: int = total_ns_of_second // NS_PER_MS    # 0-999 ms
    
    # The remaining nanoseconds after ms calculation
    remaining_ns: int = total_ns_of_second % NS_PER_MS         # 0-999,999 ns
    
    # The microsecond part (0-999) and nanosecond part (0-999) of the remainder
    self.microsecond: int = remaining_ns // NS_PER_US         # 0-999 us (sub-millisecond)
    self.nanosecond: int = remaining_ns % NS_PER_US           # 0-999 ns (sub-microsecond)

    self.timezone: int = timezone
    # self.formater: str = format

  def format(self, formater: "Formater.String") -> str: # type: ignore
    """Formats the Time object according to the specified format string."""
    return Formater.format(self, formater)

  def __str__(self) -> str:
    """Default string representation using the initialized format."""
    # return self.format(self.formater)
    return self.format(Formater.String.DEFAULT_NS)

  # def _get_tz_suffix(self, fmt: str) -> str:
  #   """
  #   Returns the timezone suffix string for the given format string.
  #   If the timezone offset is 0 and the format string is ISO8601 or ends with 'Z', 'Z' is returned.
  #   Otherwise, the timezone offset string is formatted as '+HH:MM'.
  #   """
  #   if self.timezone == 0 and ('ISO8601' in fmt or fmt.endswith('Z')):
  #     return 'Z'
  #   # Format the timezone offset string (+HH:MM, MicroPython only handles +HH)
  #   sign = '+' if self.timezone >= 0 else '-'
  #   # MicroPython string formatting often struggles with advanced format specifiers like :+02d
  #   # We rely on simpler string concatenation for robustness in MicroPython
  #   return "{}{:02d}".format(sign, abs(self.timezone))
      
  # def format(self, fmt: str) -> str:
  #   """
  #   Formats a Time object according to the given format string.

  #   The format string supports the following format specifiers:
  #     - year: 4-digit year (e.g. {year:04d})
  #     - month: 2-digit month (e.g. {month:02d})
  #     - day: 2-digit day (e.g. {day:02d})
  #     - hour: 2-digit hour (e.g. {hour:02d})
  #     - minute: 2-digit minute (e.g. {minute:02d})
  #     - second: 2-digit second (e.g. {second:02d})
  #     - weekday: 1-digit weekday (0-6, e.g. {weekday})
  #     - yearday: 3-digit day of the year (1-366, e.g. {yearday:03d})
  #     - millisecond: 3-digit millisecond (0-999, e.g. {millisecond:03d})
  #     - microsecond: 3-digit microsecond (0-999, e.g. {microsecond:03d})
  #     - nanosecond: 3-digit nanosecond (0-999, e.g. {nanosecond:03d})
  #     - timezone: timezone offset in hours (e.g. {timezone:+03d})

  #   The format string is expected to be a valid Python format string.
  #   The {tz_suffix} placeholder is replaced with the timezone suffix string generated by _get_tz_suffix.

  #   Returns a str object representing the formatted Time object.
  #   """
  #   # Handle timezone suffix logic
  #   tz_suffix = self._get_tz_suffix(fmt)
  #   fmt = fmt.replace('{tz_suffix}', tz_suffix) # Replace placeholder

  #   return fmt.format(
  #     year        = self.year,
  #     month       = self.month,
  #     day         = self.day,
  #     hour        = self.hour,
  #     minute      = self.minute,
  #     second      = self.second,
  #     weekday     = self.weekday,
  #     yearday     = self.yearday,
  #     millisecond = self.millisecond,
  #     microsecond = self.microsecond, # Sub-millisecond part (0-999)
  #     nanosecond  = self.nanosecond,  # Sub-microsecond part (0-999)
  #     timezone    = self.timezone,
  #     # Note: Removed micropart/nanopart from format method as they were removed from __init__
  #   )

class Formater:
  class String:
    def __init__(self, formater: str) -> None:
      """
      Args:
        formater (str): accept name: `year`, `month`, `day`, `hour`, `minute`, `second`, `millisecond`, `microsecond`, `nanosecond`, `timezoneSuffix`(ISO8601)
      """
      # TODO: check `formater` content
      self.formater = formater
    ISO8601    : "Formater.String"
    ISO8601_MS : "Formater.String"
    ISO8601_US : "Formater.String"
    ISO8601_NS : "Formater.String"
    DEFAULT    : "Formater.String"
    DEFAULT_MS : "Formater.String"
    DEFAULT_US : "Formater.String"
    DEFAULT_NS : "Formater.String"
  # Added 'Z' format for true UTC/ISO8601 when timezone is 0
  String.ISO8601    = String("{year:04d}-{month:02d}-{day:02d}T{hour:02d}:{minute:02d}:{second:02d}{timezoneSuffix}")
  String.ISO8601_MS = String("{year:04d}-{month:02d}-{day:02d}T{hour:02d}:{minute:02d}:{second:02d}.{millisecond:03d}{timezoneSuffix}")
  String.ISO8601_US = String("{year:04d}-{month:02d}-{day:02d}T{hour:02d}:{minute:02d}:{second:02d}.{millisecond:03d}{microsecond:03d}{timezoneSuffix}")
  String.ISO8601_NS = String("{year:04d}-{month:02d}-{day:02d}T{hour:02d}:{minute:02d}:{second:02d}.{millisecond:03d}{microsecond:03d}{nanosecond:03d}{timezoneSuffix}")
  String.DEFAULT    = String("{year:04d}/{month:02d}/{day:02d} {hour:02d}:{minute:02d}:{second:02d}{timezoneSuffix}")
  String.DEFAULT_MS = String("{year:04d}/{month:02d}/{day:02d} {hour:02d}:{minute:02d}:{second:02d}.{millisecond:03d}{timezoneSuffix}")
  String.DEFAULT_US = String("{year:04d}/{month:02d}/{day:02d} {hour:02d}:{minute:02d}:{second:02d}.{millisecond:03d}{microsecond:03d}{timezoneSuffix}")
  String.DEFAULT_NS = String("{year:04d}/{month:02d}/{day:02d} {hour:02d}:{minute:02d}:{second:02d}.{millisecond:03d}{microsecond:03d}{nanosecond:03d}{timezoneSuffix}")
  @classmethod
  def timezoneSuffix_ISO8601(cls, timezone: int) -> str:
    return f"Z" if timezone == 0 else f"{'+' if timezone > 0 else '-'}{abs(timezone):02d}:00"
  @classmethod
  def format(cls, time: Time | None = Time(), formater: String = String.DEFAULT_MS) -> str:
    if time is None: time = Time()
    result = formater.formater.format(
      year        = time.year,
      month       = time.month,
      day         = time.day,
      hour        = time.hour,
      minute      = time.minute,
      second      = time.second,
      millisecond = time.millisecond,  # Sub-millisecond part (0-999)
      microsecond = time.microsecond,  # Sub-microsecond part (0-999)
      nanosecond  = time.nanosecond,   # Sub-nanosecond part (0-999)
      timezoneSuffix = cls.timezoneSuffix_ISO8601(time.timezone),
    )
    return result

Time().format