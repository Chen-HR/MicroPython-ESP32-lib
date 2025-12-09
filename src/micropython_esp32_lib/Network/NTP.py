# System/NTP.py
import ntptime # type: ignore

# try: 
#   from ..Utils import Logging
# except ImportError:
#   from micropython_esp32_lib.Utils import Logging

def syncTimeWithNTP(ntp_host: str = "time.google.com") -> bool:
  """  Synchronizes the system time using NTP.

  Args:
    ntp_host (str, optional): The NTP server address. Defaults to "time.google.com".

  Returns:
    bool: True if synchronization was successful, False otherwise.
  """
  ntptime.host = ntp_host
  ntptime.settime() 
  return True

def syncTimeWithNTPs(ntp_hosts: list[str] = ["time.cloudflare.com", "time.google.com", "pool.ntp.org"]) -> bool:
  """Tries to synchronize the system time using multiple NTP servers.

  Args:
    ntp_hosts (list[str], optional): A list of NTP server addresses. Defaults to ["time.cloudflare.com", "time.google.com", "pool.ntp.org"].

  Returns:
    bool: True if synchronization was successful with any server, False otherwise.
  """
  for ntp_host in ntp_hosts:
    if syncTimeWithNTP(ntp_host=ntp_host):
      return True
  return False

if __name__ == '__main__':
  
  try: 
    from ..System import Logging
  except ImportError:
    from micropython_esp32_lib.System import Logging
  Logging.info("Test the NTP connection")
  Logging.info("Sync NTP...")
  if syncTimeWithNTPs():
    Logging.info("Sync NTP Done.")
  else: 
    Logging.warning("Sync NTP Failed.")