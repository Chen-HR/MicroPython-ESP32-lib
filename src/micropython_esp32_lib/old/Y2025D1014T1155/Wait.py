import utime
import asyncio
import machine


try: sync_s = utime.sleep 
except: pass
try: sync_ms = utime.sleep_ms 
except: pass
try: sync_us = utime.sleep_us 
except: pass

try: async_s = asyncio.sleep
except: pass
try: async_ms = asyncio.sleep_ms
except: pass
try: async_us = asyncio.sleep_us
except: pass

try: secend = utime.sleep 
except: pass
try: millisecond = utime.sleep_ms 
except: pass
try: microsecond = utime.sleep_us 
except: pass

def sync_time(target_s: int, timezone: int = 0) -> bool:
  now_s = utime.time() + timezone * 3600
  if target_s > now_s:
    try:
      sync_s(target_s - now_s)
    except Exception as e:
      print("sync_time error:", e)
      return False
  return True
async def async_time(target_s: int, timezone: int = 0) -> bool:
  now_s = utime.time() + timezone * 3600
  if target_s > now_s:
    try:
      await async_s(target_s - now_s)
    except Exception as e:
      print("async_time error:", e)
      return False
  return True

if __name__ == "__main__":
  try:
    from HRChen import SystemTime
  except ImportError:
    from . import SystemTime

  print("[__main__] Current local time:", SystemTime.TimeStruct())
  print("[__main__] Test sync_time() to wait 5 seconds...")
  sync_time(SystemTime.current() + 5)
  print("[__main__] sync_time() done.")
  print("[__main__] Current local time:", SystemTime.TimeStruct())
  print("[__main__] Test async_time() to wait 5 seconds...")
  asyncio.run(async_time(SystemTime.current() + 5))
  print("[__main__] async_time() done.")
  print("[__main__] Current local time:", SystemTime.TimeStruct())