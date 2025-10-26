# Network/Basic.py
import network

try: 
  from ..System import Logging
  from ..System import Code
except ImportError:
  from MicroPython_ESP32_lib.System import Logging
  from MicroPython_ESP32_lib.System import Code

class Statu(Code.Code):
  pass
class STATU:
  """WLAN connection status constants (network.STAT_*)"""
  # Define fallback values in case MicroPython's network module lacks them
  IDLE            : Statu = Statu("IDLE"           ,1000) # network.STAT_IDLE: no connection and no activity
  CONNECTING      : Statu = Statu("CONNECTING"     ,1001) # network.STAT_CONNECTING: connecting in progress
  GOT_IP          : Statu = Statu("GOT_IP"         ,1010) # network.STAT_GOT_IP: connection successful
  NO_AP_FOUND     : Statu = Statu("NO_AP_FOUND"    ,201 ) # network.STAT_NO_AP_FOUND: failed because no access point replied
  WRONG_PASSWORD  : Statu = Statu("WRONG_PASSWORD" ,202 ) # network.STAT_WRONG_PASSWORD: failed due to incorrect password
  CONNECT_FAIL    : Statu = Statu("CONNECT_FAIL"   ,203 ) # network.STAT_CONNECT_FAIL: failed due to other problems
  try:
    IDLE            : Statu = Statu("IDLE"           ,network.STAT_IDLE          ) # network.STAT_IDLE: no connection and no activity
    CONNECTING      : Statu = Statu("CONNECTING"     ,network.STAT_CONNECTING    ) # network.STAT_CONNECTING: connecting in progress
    GOT_IP          : Statu = Statu("GOT_IP"         ,network.STAT_GOT_IP        ) # network.STAT_GOT_IP: connection successful
    NO_AP_FOUND     : Statu = Statu("NO_AP_FOUND"    ,network.STAT_NO_AP_FOUND   ) # network.STAT_NO_AP_FOUND: failed because no access point replied
    WRONG_PASSWORD  : Statu = Statu("WRONG_PASSWORD" ,network.STAT_WRONG_PASSWORD) # network.STAT_WRONG_PASSWORD: failed due to incorrect password
    CONNECT_FAIL    : Statu = Statu("CONNECT_FAIL"   ,network.STAT_CONNECT_FAIL  ) # network.STAT_CONNECT_FAIL: failed due to other problems
  except AttributeError:
    Logging.Log("Network Constants Status", Logging.LEVEL.WARNING).warning("Network status constants (`network.STAT_*`) not fully found. Using internal fallbacks.")

class PowerManagement(Code.Code):
  pass
class PM:
  """WLAN power management modes (network.PM_*)"""
  # MicroPython PM modes (often 0, 1, 2)
  ACTIVE    : PowerManagement = PowerManagement("ACTIVE"    ,0)
  POWERSAVE : PowerManagement = PowerManagement("POWERSAVE" ,1)
  
  try:
    # Attempt to map MicroPython's specific constants if available
    ACTIVE    : PowerManagement = PowerManagement("ACTIVE"    ,network.MODE_PERFORMANCE)
    POWERSAVE : PowerManagement = PowerManagement("POWERSAVE" ,network.MODE_NONE       )
  except AttributeError:
    try:
      # Common esp32/esp8266 power modes
      ACTIVE    : PowerManagement = PowerManagement("ACTIVE"    ,network.WLAN.PM_ACTIVE   )
      POWERSAVE : PowerManagement = PowerManagement("POWERSAVE" ,network.WLAN.PM_POWERSAVE)
    except AttributeError:
      Logging.Log("Network Constants Power Management", Logging.LEVEL.WARNING).warning("Network power management constants (`network.PM_*`) not fully found. Using internal fallbacks.")
class Mode(Code.Code):
  pass
class MODE:
  """WLAN operating modes (network.MODE_*)"""
  STA : Mode = Mode("STA", 1) # Station mode (client)
  AP  : Mode = Mode("AP" , 2) # Access Point mode
  try:
    STA : Mode = Mode("STA", network.STA_IF) # Station mode (client)
    AP  : Mode = Mode("AP" , network.AP_IF ) # Access Point mode
  except AttributeError:
    Logging.Log("Network Constants Mode", Logging.LEVEL.WARNING).warning("Network interface constants (`network.STA_IF`, `network.AP_IF`) not fully found. Using internal fallbacks (1, 2).")

class IPV4Address:
  """
  Represents an IPV4 address as a tuple of integers.
  NOTE: Micropython's wlan.ifconfig() returns strings, not integers.
  """
  def __init__(self, addr: tuple[int, int, int, int] | str | None = None, log_level: Logging.Level = Logging.LEVEL.WARNING) -> None:
    """
    Initializes an instance of the IPV4Address class.

    Args:
      ip (tuple[int, int, int, int] | None): The IPv4 address as a tuple of integers.
        If None, the address is set to (0, 0, 0, 0).

    Raises:
      ValueError: If the length of the input tuple is not 4,
        or if any of the octets are not between 0 and 255 (inclusive).

    """
    logger = Logging.Log("IPV4 Address", log_level)
    self.addr = (0, 0, 0, 0) if addr is None else addr
    try: # parse address as str
      logger.debug(f"Parse address as string {self.addr}...")
      self.addr = tuple(map(int, addr.split(".")))
    except ValueError: # address not str
      logger.debug(f"address as string {self.addr} failed. Parse as tuple...")
    if len(self.addr) != 4: # check addr: tuple[int, int, int, int]
      logger.error("IPV4 address must have exactly 4 octets")
      raise ValueError("IPV4 address must have exactly 4 octets")
    else: # addr: tuple[int, int, int, int]
      for octet in self.addr:
        if not (0 <= octet <= 255):
          logger.error("Each octet must be between 0 and 255")
          raise ValueError("Each octet must be between 0 and 255")
      self.addr: tuple[int, int, int, int] = addr
  def __str__(self) -> str:
    return ".".join(map(str, self.addr))
  def __tuple__(self) -> tuple[int, int, int, int]:
    return self.addr
