import ntptime
import utime
import machine

def sync_ntp(ntp_host: str = "time.google.com", logger_perfix: str | None = None) -> bool:
  try:
    if logger_perfix is not None: print(logger_perfix, f"System time synchronization in progress (use NTP server: `{ntp_host}`)... ", end="")
    ntptime.host = ntp_host
    current_time = ntptime.time()
    ntptime.settime()
    if logger_perfix is not None: print("Done.")
    return True
  except Exception as e:
    if logger_perfix is not None: print("Failed.")
    return False

TIMEZONE = 0 # UTC+0
UNIT_TIME_NS = (10**(len(str(utime.time_ns()))-len(str(utime.time()))-6))

def setTimezone(timezone: int = TIMEZONE) -> int:
  global TIMEZONE
  TIMEZONE: int = timezone
  return TIMEZONE

def offset(timezone: int = TIMEZONE):
  global TIMEZONE
  utc_offset_s: int = timezone * 3600 
  tm = utime.localtime(utime.time() + utc_offset_s) # utime.struct_time
  machine.RTC().datetime((tm[0], tm[1], tm[2], tm[6], tm[3], tm[4], tm[5], utime.ticks_ms()))
  TIMEZONE = 0

def current_s(timezone: int = TIMEZONE) -> int:
  return utime.time() + timezone * 3_600

def current_ms(timezone: int = TIMEZONE) -> int:
  return utime.time_ns() // (1_000*UNIT_TIME_NS)

def current_ns(timezone: int = TIMEZONE) -> int:
  return utime.time_ns() // (UNIT_TIME_NS)

class TimeStruct:
  def __init__(self, time_ns: int = 0, timezone: int = TIMEZONE):
    if time_ns == 0:
      self.time_ns = current_ns(timezone)
    else:
      self.time_ns = time_ns
    print(f"[TimeStruct.__init__] time_ns: {self.time_ns}")
    self.time_s: int = self.time_ns // 1_000_000
    print(f"[TimeStruct.__init__] time_s : {self.time_ns // 1_000_000}, {self.time_s}")
    self.tm: tuple[int, int, int, int, int, int, int, int] = utime.localtime(self.time_s)
    self.year: int = self.tm[0]
    self.month: int = self.tm[1]
    self.day: int = self.tm[2]
    self.hour: int = self.tm[3]
    self.minute: int = self.tm[4]
    self.second: int = self.tm[5]
    self.millisecond: int = (self.time_ns % 1_000_000) // 1_000
    self.microsecond: int = self.time_ns % 1_000
    self.weekday: int = self.tm[6] # 0~6
    self.yearday: int = self.tm[7] # 1~366

  def __str__(self):
    return self.format()

  def format(self, fmt: str = "{year:04d}/{month:02d}/{day:02d} {hour:02d}:{minute:02d}:{second:02d}.{millisecond:03d}.{microsecond:03d}") -> str:
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
      microsecond = self.microsecond
    )

make_s = lambda year, month, day, hour=0, minute=0, second=0, timezone=TIMEZONE: utime.mktime((year, month, day, hour, minute, second, 0, 0)) - timezone * 3600

if __name__ == "__main__":
  try:
    from . import WLAN
  except ImportError: 
    from HRChen import WLAN

  s_s = current_s()
  s_ms = current_ms()
  s_ns = current_ns()
  utime.sleep_ms(100)
  e_s = current_s()
  e_ms = current_ms()
  e_ns = current_ns()
  print("[__main__]  s:", s_s)
  print("[__main__]  e:", e_s)
  print()
  print("[__main__] ms:", s_ms)
  print("[__main__] me:", e_ms)
  print()
  print("[__main__] ns:", s_ns)
  print("[__main__] ne:", e_ns)
  print()

  wlanConnector = WLAN.WLANConnector(loger_perfix="[WLAN] ")
  print("[__main__] init local time:", TimeStruct())
  try:
    wlanConnector.activate()
    while not wlanConnector.connect(WLAN.WLANConfig(
        ssid="CSIE406_DEV", 
        password="406406406", 
        hostname="ESP32S3-IoT-Device", 
        pm=WLAN.NETWORK_PM_POWERSAVE
      )):
      print("[__main__] Retrying to connect...")
    else:
      print("[__main__] Device successfully connected to the network.")

    print("[__main__] init local time:", TimeStruct()) 
    sync_ntp("time.google.com", "[syncTime_ntp]")
    print("[__main__] sync_ntp local time (UTC+0):", TimeStruct()) 
    print("[__main__] sync_ntp local time (UTC+8):", TimeStruct(timezone=8)) 
    offset(8)

    while True:
      utime.sleep_ms(500)
      print("[__main__] Current local time:", TimeStruct())

  except KeyboardInterrupt:
    print("[__main__] Program interrupted")
  except Exception as e:
    print(f"[__main__] An unexpected error occurred: {e}")
  finally:
    wlanConnector.disconnect()
    wlanConnector.deactivate()
    print("[__main__] WLAN interface is now clean.")
    print("[__main__] Program ended")