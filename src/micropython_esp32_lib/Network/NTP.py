# Network/NTP.py
import ntptime

try: 
  from ..Utils import Logging
  from ..System import Sleep
except ImportError:
  from micropython_esp32_lib.Utils import Logging
  from micropython_esp32_lib.System import Sleep

def syncTimeWithNTP(ntp_host: str = "time.google.com", log_level: Logging.Level = Logging.LEVEL.INFO) -> bool:
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

def syncTimeWithNTPs(ntp_hosts: list[str] = ["time.cloudflare.com", "time.google.com", "pool.ntp.org"], log_level: Logging.Level = Logging.LEVEL.INFO) -> bool:
  """Tries to synchronize the system time using multiple NTP servers.

  Args:
    ntp_hosts (list[str], optional): A list of NTP server addresses. Defaults to ["time.cloudflare.com", "time.google.com", "pool.ntp.org"].
    log_level (Logging.Level, optional): The log level for reporting status. Defaults to Logging.LEVEL.INFO.

  Returns:
    bool: True if synchronization was successful with any server, False otherwise.
  """
  for ntp_host in ntp_hosts:
    if syncTimeWithNTP(ntp_host=ntp_host, log_level=log_level):
      return True
  return False

if __name__ == '__main__':
  logger = Logging.Log("Test NTP", Logging.LEVEL.INFO)
  logger.info("Test the NTP connection")

  logger.info("Sync NTP...")
  if syncTimeWithNTPs(log_level=Logging.LEVEL.INFO):
    logger.info("Sync NTP Done.")
  else: 
    logger.warning("Sync NTP Failed.")