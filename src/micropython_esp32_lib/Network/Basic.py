# Network/Basic.py
import network

try: 
  from ..Utils import Logging
  from ..Utils import Enum
except ImportError:
  from micropython_esp32_lib.Utils import Logging
  from micropython_esp32_lib.Utils import Enum

class Statu(Enum.Unit):
  """WLAN connection status constants (network.STAT_*)"""
  def __init__(self, name: str, code: int) -> None:
    super().__init__(name, code)
  def __repr__(self) -> str:
    return f"Statu({self.name}, {self.value})"
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
    IDLE            : Statu = Statu("IDLE"           ,network.STAT_IDLE          ) # type: ignore # network.STAT_IDLE: no connection and no activity
    CONNECTING      : Statu = Statu("CONNECTING"     ,network.STAT_CONNECTING    ) # type: ignore # network.STAT_CONNECTING: connecting in progress
    GOT_IP          : Statu = Statu("GOT_IP"         ,network.STAT_GOT_IP        ) # type: ignore # network.STAT_GOT_IP: connection successful
    NO_AP_FOUND     : Statu = Statu("NO_AP_FOUND"    ,network.STAT_NO_AP_FOUND   ) # type: ignore # network.STAT_NO_AP_FOUND: failed because no access point replied
    WRONG_PASSWORD  : Statu = Statu("WRONG_PASSWORD" ,network.STAT_WRONG_PASSWORD) # type: ignore # network.STAT_WRONG_PASSWORD: failed due to incorrect password
    CONNECT_FAIL    : Statu = Statu("CONNECT_FAIL"   ,network.STAT_CONNECT_FAIL  ) # type: ignore # network.STAT_CONNECT_FAIL: failed due to other problems
  except AttributeError:
    tmp=Logging.Log("Network Constants Status", Logging.LEVEL.WARNING)
    tmp.warning("Network status constants (`network.STAT_*`) not fully found. Using internal fallbacks.")
    del tmp

  @classmethod
  def Statu(cls, code: int) -> Statu:
    if code == cls.IDLE           .value : return cls.IDLE           
    if code == cls.CONNECTING     .value : return cls.CONNECTING     
    if code == cls.GOT_IP         .value : return cls.GOT_IP         
    if code == cls.NO_AP_FOUND    .value : return cls.NO_AP_FOUND    
    if code == cls.WRONG_PASSWORD .value : return cls.WRONG_PASSWORD 
    if code == cls.CONNECT_FAIL   .value : return cls.CONNECT_FAIL   
    return Statu("UNKNOWN", code)

class PowerManagement(Enum.Unit):
  """WLAN power management modes (network.PM_*)"""
  def __init__(self, name: str, id: int):
    super().__init__(name, id)
  def __repr__(self) -> str:
    return f"PowerManagement({self.name}, {self.value})"
class PM:
  """WLAN power management modes (network.PM_*)"""
  # MicroPython PM modes (often 0, 1, 2)
  ACTIVE    : PowerManagement = PowerManagement("ACTIVE"    ,0)
  POWERSAVE : PowerManagement = PowerManagement("POWERSAVE" ,1)
  
  try:
    # Attempt to map MicroPython's specific constants if available
    ACTIVE    : PowerManagement = PowerManagement("ACTIVE"    ,network.MODE_PERFORMANCE) # type: ignore
    POWERSAVE : PowerManagement = PowerManagement("POWERSAVE" ,network.MODE_NONE       ) # type: ignore
  except AttributeError:
    try:
      # Common esp32/esp8266 power modes
      ACTIVE    : PowerManagement = PowerManagement("ACTIVE"    ,network.WLAN.PM_ACTIVE   ) # type: ignore
      POWERSAVE : PowerManagement = PowerManagement("POWERSAVE" ,network.WLAN.PM_POWERSAVE) # type: ignore
    except AttributeError:
      tmp=Logging.Log("Network Constants Power Management", Logging.LEVEL.WARNING)
      tmp.warning("Network power management constants (`network.PM_*`) not fully found. Using internal fallbacks.")
      del tmp

class Mode(Enum.Unit):
  """WLAN operating modes (network.MODE_*)"""
  def __init__(self, name: str, id: int):
    super().__init__(name, id)
  def __repr__(self) -> str:
    return f"Mode({self.name}, {self.value})"
class MODE:
  """WLAN operating modes (network.MODE_*)"""
  STA : Mode = Mode("STA", 1) # Station mode (client)
  AP  : Mode = Mode("AP" , 2) # Access Point mode
  try:
    STA : Mode = Mode("STA", network.STA_IF) # type: ignore # Station mode (client)
    AP  : Mode = Mode("AP" , network.AP_IF ) # type: ignore # Access Point mode
  except AttributeError:
    tmp=Logging.Log("Network Constants Mode", Logging.LEVEL.WARNING)
    tmp.warning("Network interface constants (`network.STA_IF`, `network.AP_IF`) not fully found. Using internal fallbacks (1, 2).")
    del tmp

class IPV4Address:
  NONE = (-1, -1, -1, -1)
  def __init__(self, addr: tuple[int, int, int, int] | str | None = None, log_level: Logging.Level = Logging.LEVEL.WARNING) -> None:
    """
    Initializes an instance of the IPV4Address class.

    Args:
      ip (tuple[int, int, int, int] | None): The IPv4 address as a tuple of integers.
        If None, the address is set to (0, 0, 0, 0).

    Raises:
      ValueError: If the length of the input tuple is not 4,
        or if any of 

    """
    logger = Logging.Log("IPV4 Address Constructor", log_level)
    # Parse addr into a tuple and store it in _addr
    _addr = tuple()
    if addr is None: # if addr is None
      _addr = IPV4Address.NONE
      logger.debug("No address provided. Set to default {IPV4Address.NONE}.")
    elif isinstance(addr, str): # if addr is str
      try:
        logger.debug(f"Parse address as string {addr}...")
        _addr = tuple(map(int, addr.split("."))) # type: ignore
      except ValueError:
        logger.error(f"Failed to parse address string: {addr}")
        raise ValueError(f"Invalid IP address string: {addr}")
    elif isinstance(addr, tuple): # if addr is tuple
      logger.debug(f"Clone addr to self")
      _addr = addr
    # Validate the _addr format
    if isinstance(_addr, tuple): # if addr is tuple
      logger.debug(f"Parse address as tuple {_addr}...")
      if len(_addr) != 4: # check length
        logger.error("IPV4 address must have exactly 4 octets")
        raise ValueError("IPV4 address must have exactly 4 octets")
      if all(0 <= a <= 255 for a in _addr): # check range
        logger.debug(f"Address set to {_addr}")
        self.addr: tuple[int, int, int, int] = _addr
        return
      else:
        logger.error("Each number must be between 0 and 255")
        raise ValueError("Each number must be between 0 and 255")
    raise TypeError("Address must be a tuple of 4 integers, a string, or None")
  def __str__(self) -> str:
    if all(0 <= a <= 255 for a in self.addr): # check range
      return ".".join(map(str, self.addr))
    else:
      return "None"    
  def __repr__(self) -> str:
    return f"IPV4Address({self.addr})"
  def str(self) -> str:
    return self.__str__()
