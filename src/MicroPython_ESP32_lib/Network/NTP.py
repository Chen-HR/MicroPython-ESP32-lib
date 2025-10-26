# Network/NTP.py
import ntptime

try: 
  from ..System import Logging
  from ..System import Sleep
except ImportError:
  from MicroPython_ESP32_lib.System import Logging
  from MicroPython_ESP32_lib.System import Sleep

def sync(ntp_host: str = "time.google.com", log_level: Logging.Level = Logging.LEVEL.INFO) -> bool:
  """  Synchronizes the system time using NTP.

  Args:
    ntp_host (str, optional): The NTP server address. Defaults to "time.google.com".
    log_level (Logging.Level, optional): The log level for reporting status. Defaults to Logging.LEVEL.INFO.

  Returns:
    bool: True if synchronization was successful, False otherwise.
  """
  logger = Logging.Log("Sync NTP", log_level)

  try:
    logger.info(f"System time synchronization in progress (use NTP server: `{ntp_host}`)...")
    ntptime.host = ntp_host
    ntptime.settime() 
    logger.info("Synchronization Done.")
    return True
  except Exception as e:
    logger.error(f"Synchronization Failed. Error: {e}")
    return False

def sync_with_retry(ntp_host: str = "time.google.com", retries: int = 4, delay_ms: int = 4, log_level: Logging.Level = Logging.LEVEL.INFO) -> bool:
  """Synchronizes the system time using NTP with retry mechanism.

  Args:
    ntp_host (str, optional): The NTP server address. Defaults to "time.google.com".
    retries (int, optional): The number of retries. Defaults to 4.
    delay_ms (int, optional): The delay in milliseconds between retries. Defaults to 4.
    log_level (Logging.Level, optional): The log level for reporting status. Defaults to Logging.LEVEL.INFO.

  Returns:
    bool: True if synchronization was successful, False otherwise.
  """
  logger = Logging.Log("Sync NTP", log_level)
  
  for i in range(retries):
    if sync(ntp_host=ntp_host, log_level=log_level):
      return True
    
    if i < retries - 1:

      Sleep.sync_ms(delay_ms)
    
  logger.error("NTP synchronization failed after all retries.")
  return False


if __name__ == '__main__':
  logger = Logging.Log("Test NTP", Logging.LEVEL.INFO)
  logger.info("Test the NTP connection")

  logger.info("Sync NTP...")
  if sync(ntp_host="time.google.com", log_level=Logging.LEVEL.INFO):
    logger.info("Sync NTP Done.")
  else: 
    logger.warning("Sync NTP Failed.")