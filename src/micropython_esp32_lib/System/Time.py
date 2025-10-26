# System/Time.py
import utime
import machine

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

make_s = lambda year=2000, month=1, day=1, hour=0, minute=0, second=0, timezone=0: utime.mktime((year, month, day, hour, minute, second, 0, 0)) + timezone * SECONDS_PER_HOUR

def setRTC(time_seconds: int = 0, timezone: int | None = None) -> None:
  """
  Sets the system real-time clock (RTC) to the given time in seconds, with the given timezone offset applied.

  Args:
    time_seconds (int, optional): The time in seconds. Defaults to 0, which is interpreted as the current time.
    timezone (int, optional): The timezone offset in hours. Defaults to TIMEZONE.

  Notes:
    This function may not work correctly on all MicroPython boards, as RTC handling can vary greatly between boards.
  """
  global TIMEZONE
  if timezone is None: timezone = TIMEZONE
  time_seconds += timezone * SECONDS_PER_HOUR
  tm = utime.localtime(time_seconds)
  try:
    # Note: MicroPython RTC often handles datetime but sub-second is tricky.
    machine.RTC().datetime((tm[0], tm[1], tm[2], tm[6], tm[3], tm[4], tm[5], utime.ticks_ms()))
  except:
    pass # RTC not available or not configurable

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
  return utime.time() + timezone * SECONDS_PER_HOUR

def current_ms(timezone: int | None = None) -> int:
  """
  Returns the current time in milliseconds, with the given timezone offset applied.

  If time_ns is unavailable, this function falls back to using utime.time() for seconds and utime.ticks_ms() for sub-seconds.

  Args:
    timezone (int, optional): The timezone offset in hours. Defaults to TIMEZONE.

  Returns:
    int: The current time in milliseconds, with the given timezone offset applied.
  """
  global TIMEZONE
  if timezone is None: timezone = TIMEZONE
  try:
    # Use utime.time() for seconds and ticks_ms() for sub-seconds if time_ns is unavailable
    return (utime.time() + timezone * SECONDS_PER_HOUR) * MS_PER_S + (utime.ticks_ms() % MS_PER_S)
  except AttributeError:
    return current_s(timezone) * MS_PER_S

def current_us(timezone: int | None = None) -> int:
  """
  Returns the current time in microseconds, with the given timezone offset applied.

  If utime.time_ns() is available, it is used to provide the best possible precision.
  Otherwise, utime.time() is used for seconds and utime.ticks_us() is used for sub-seconds.

  Args:
    timezone (int, optional): The timezone offset in hours. Defaults to TIMEZONE.

  Returns:
    int: The current time in microseconds, with the given timezone offset applied.
  """
  global TIMEZONE
  if timezone is None: timezone = TIMEZONE

  try:
    # utime.time_ns() // 1000 gives total microseconds
    return utime.time_ns() // NS_PER_MS + timezone * SECONDS_PER_HOUR * US_PER_S
  except AttributeError:
    # Fallback: time() for seconds + ticks_us() for sub-seconds (best effort)
    return current_s(timezone) * US_PER_S + (utime.ticks_us() % US_PER_S)

def current_ns(timezone: int | None = None) -> int:
  """
  Returns the current time in nanoseconds, with the given timezone offset applied.

  If utime.time_ns() is available, it is used to provide the best possible precision.
  Otherwise, utime.time() is used for seconds and utime.ticks_us() is used for sub-seconds.

  Args:
    timezone (int, optional): The timezone offset in hours. Defaults to TIMEZONE.

  Returns:
    int: The current time in nanoseconds, with the given timezone offset applied.
  """
  global TIMEZONE
  if timezone is None: timezone = TIMEZONE
  try:
    # MicroPython time_ns is often us or ms precision, but we treat it as the base.
    return utime.time_ns() + timezone * SECONDS_PER_HOUR * NS_PER_S
  except AttributeError:
    # Fallback: time() for seconds + ticks_us() * 1000 for sub-seconds
    return current_s(timezone) * NS_PER_S + (utime.ticks_us() % US_PER_S) * NS_PER_US

class TimeFormater:
  # Added 'Z' format for true UTC/ISO8601 when timezone is 0
  ISO8601    = "{year:04d}-{month:02d}-{day:02d}T{hour:02d}:{minute:02d}:{second:02d}{tz_suffix}"
  ISO8601_MS = "{year:04d}-{month:02d}-{day:02d}T{hour:02d}:{minute:02d}:{second:02d}.{millisecond:03d}{tz_suffix}"
  ISO8601_US = "{year:04d}-{month:02d}-{day:02d}T{hour:02d}:{minute:02d}:{second:02d}.{millisecond:03d}{microsecond:03d}{tz_suffix}"
  ISO8601_NS = "{year:04d}-{month:02d}-{day:02d}T{hour:02d}:{minute:02d}:{second:02d}.{millisecond:03d}{microsecond:03d}{nanosecond:03d}{tz_suffix}"
  
  # Simple formats for logging
  DEFAULT    = "{year:04d}/{month:02d}/{day:02d} {hour:02d}:{minute:02d}:{second:02d}{tz_suffix}"
  DEFAULT_MS = "{year:04d}/{month:02d}/{day:02d} {hour:02d}:{minute:02d}:{second:02d}.{millisecond:03d}{tz_suffix}"
  DEFAULT_US = "{year:04d}/{month:02d}/{day:02d} {hour:02d}:{minute:02d}:{second:02d}.{millisecond:03d}{microsecond:03d}{tz_suffix}"
  DEFAULT_NS = "{year:04d}/{month:02d}/{day:02d} {hour:02d}:{minute:02d}:{second:02d}.{millisecond:03d}{microsecond:03d}{nanosecond:03d}{tz_suffix}"


class Time:
  """
  Represents a point in time with nanosecond precision.
  The Time object is immutable once created.
  """
  
  def __init__(self, time_ns: int = 0, timezone: int | None = None, format: str = TimeFormater.DEFAULT_NS):
    """
    Initializes a Time object from a given time in nanoseconds and timezone offset in hours.

    Args:
      time_ns (int, optional): The time in nanoseconds. Defaults to 0, which is interpreted as the current time.
      timezone (int, optional): The timezone offset in hours. Defaults to TIMEZONE.
      format (str, optional): The format string for the Time object's __str__() method. Defaults to TimeFormater.DEFAULT_NS.

    The Time object is immutable once created.
    """
    global TIMEZONE
    if timezone is None: timezone = TIMEZONE
    self.nanosecond_total: int = current_ns(timezone) if time_ns == 0 else time_ns
    
    # 1. Second component from epoch
    self.second_from_epoch: int = self.nanosecond_total // NS_PER_S

    # 2. Time tuple (localtime expects seconds from epoch)
    # utime.localtime includes the local time offset (timezone * SECONDS_PER_HOUR) already applied in current_ns
    self.tm: tuple[int, int, int, int, int, int, int, int] = utime.localtime(self.second_from_epoch)
    
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
    self.formater: str = format
    
  def __str__(self) -> str:
    """Default string representation using the initialized format."""
    return self.format(self.formater)

  def _get_tz_suffix(self, fmt: str) -> str:
    """
    Returns the timezone suffix string for the given format string.
    If the timezone offset is 0 and the format string is ISO8601 or ends with 'Z', 'Z' is returned.
    Otherwise, the timezone offset string is formatted as '+HH:MM'.
    """
    if self.timezone == 0 and ('ISO8601' in fmt or fmt.endswith('Z')):
      return 'Z'
    # Format the timezone offset string (+HH:MM, MicroPython only handles +HH)
    sign = '+' if self.timezone >= 0 else '-'
    # MicroPython string formatting often struggles with advanced format specifiers like :+02d
    # We rely on simpler string concatenation for robustness in MicroPython
    return "{}{:02d}".format(sign, abs(self.timezone))
      
  def format(self, fmt: str) -> str:
    """
    Formats a Time object according to the given format string.

    The format string supports the following format specifiers:
      - year: 4-digit year (e.g. {year:04d})
      - month: 2-digit month (e.g. {month:02d})
      - day: 2-digit day (e.g. {day:02d})
      - hour: 2-digit hour (e.g. {hour:02d})
      - minute: 2-digit minute (e.g. {minute:02d})
      - second: 2-digit second (e.g. {second:02d})
      - weekday: 1-digit weekday (0-6, e.g. {weekday})
      - yearday: 3-digit day of the year (1-366, e.g. {yearday:03d})
      - millisecond: 3-digit millisecond (0-999, e.g. {millisecond:03d})
      - microsecond: 3-digit microsecond (0-999, e.g. {microsecond:03d})
      - nanosecond: 3-digit nanosecond (0-999, e.g. {nanosecond:03d})
      - timezone: timezone offset in hours (e.g. {timezone:+03d})

    The format string is expected to be a valid Python format string.
    The {tz_suffix} placeholder is replaced with the timezone suffix string generated by _get_tz_suffix.

    Returns a str object representing the formatted Time object.
    """
    # Handle timezone suffix logic
    tz_suffix = self._get_tz_suffix(fmt)
    fmt = fmt.replace('{tz_suffix}', tz_suffix) # Replace placeholder

    return fmt.format(
      year        = self.year,
      month       = self.month,
      day         = self.day,
      hour        = self.hour,
      minute      = self.minute,
      second      = self.second,
      weekday     = self.weekday,
      yearday     = self.yearday,
      millisecond = self.millisecond,
      microsecond = self.microsecond, # Sub-millisecond part (0-999)
      nanosecond  = self.nanosecond,  # Sub-microsecond part (0-999)
      timezone    = self.timezone,
      # Note: Removed micropart/nanopart from format method as they were removed from __init__
    )

if __name__ == '__main__':
  print('Test SystemTime...')
  print(f"Current time: {Time()}")
  print(f"setting RTC...")
  setRTC(0)
  print(f"Current time: {Time()}")
  print(f"setting timezone...")
  setTimezone(8)
  print(f"Current time: {Time()}")
