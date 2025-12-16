# System/WiFi.py
import network # type: ignore
import uasyncio # type: ignore

try: 
  from ..Utils import Logging
  from ..System.Time import Sleep
  from ..Network import IP
except ImportError:
  from micropython_esp32_lib.Utils import Logging
  from micropython_esp32_lib.System.Time import Sleep
  from micropython_esp32_lib.Network import IP

class Status:
  """WLAN connection status constants (network.STAT_*)"""
  def __init__(self, code: int, name: str):
    self.code: int = code
    self.name: str = name
  def __str__(self) -> str:
    return f"Status({self.code}, {self.name})"
  def __eq__(self, other: "Status") -> bool: # type: ignore
    return self.code == other.code and self.name == other.name
  @classmethod
  def query(cls, code: int) -> "Status":
    for status in cls.__dict__.values():
      if isinstance(status, cls):
        if status.code == code:
          return status
    raise ValueError(f"Unknown Status code: {code}")
  UNABLE_TO_ACTIVATE_CONNECTOR  : "Status"
  UNABLE_TO_CLOSE_OLD_CONNECTION : "Status"
  WIFI_INTERNAL_ERROR        : "Status"
  BEACON_TIMEOUT                    : "Status"
  NO_AP_FOUND                       : "Status"
  WRONG_PASSWORD                    : "Status"
  ASSOC_FAIL                        : "Status"
  CONNECT_FAIL                      : "Status"
  HANDSHAKE_TIMEOUT                 : "Status"
  NO_AP_FOUND_W_COMPATIBLE_SECURITY : "Status"
  NO_AP_FOUND_IN_AUTHMODE_THRESHOLD : "Status"
  NO_AP_FOUND_IN_RSSI_THRESHOLD     : "Status"
  IDLE                              : "Status"
  CONNECTING                        : "Status"
  GOT_IP                            : "Status"
Status.UNABLE_TO_ACTIVATE_CONNECTOR   = Status(-1                       , "Unable to activate connector") 
Status.UNABLE_TO_CLOSE_OLD_CONNECTION = Status(-2                       , "Unable to close old connection") 
Status.WIFI_INTERNAL_ERROR            = Status(-3                       , "OSError: WiFi Internal Error") 
try:                   Status.BEACON_TIMEOUT                    = Status(network.STAT_BEACON_TIMEOUT                    , "Beacon Timeout"                   ) # type: ignore
except AttributeError: Status.BEACON_TIMEOUT                    = Status( 200                                           , "Beacon Timeout"                   )
try:                   Status.NO_AP_FOUND                       = Status(network.STAT_NO_AP_FOUND                       , "No AP Found"                      ) # type: ignore
except AttributeError: Status.NO_AP_FOUND                       = Status( 201                                           , "No AP Found"                      )
try:                   Status.WRONG_PASSWORD                    = Status(network.STAT_WRONG_PASSWORD                    , "Wrong Password"                   ) # type: ignore
except AttributeError: Status.WRONG_PASSWORD                    = Status( 202                                           , "Wrong Password"                   )
try:                   Status.ASSOC_FAIL                        = Status(network.STAT_ASSOC_FAIL                        , "Assoc Fail"                       ) # type: ignore
except AttributeError: Status.ASSOC_FAIL                        = Status( 203                                           , "Assoc Fail"                       )
try:                   Status.CONNECT_FAIL                      = Status(network.STAT_CONNECT_FAIL                      , "Connect Fail"                     ) # type: ignore
except AttributeError: Status.CONNECT_FAIL                      = Status( 203                                           , "Connect Fail"                     )
try:                   Status.HANDSHAKE_TIMEOUT                 = Status(network.STAT_HANDSHAKE_TIMEOUT                 , "Handshake Timeout"                ) # type: ignore
except AttributeError: Status.HANDSHAKE_TIMEOUT                 = Status( 204                                           , "Handshake Timeout"                )
try:                   Status.NO_AP_FOUND_W_COMPATIBLE_SECURITY = Status(network.STAT_NO_AP_FOUND_W_COMPATIBLE_SECURITY , "No AP Found (Compatible Security)") # type: ignore
except AttributeError: Status.NO_AP_FOUND_W_COMPATIBLE_SECURITY = Status( 210                                           , "No AP Found (Compatible Security)")
try:                   Status.NO_AP_FOUND_IN_AUTHMODE_THRESHOLD = Status(network.STAT_NO_AP_FOUND_IN_AUTHMODE_THRESHOLD , "No AP Found (AuthMode Threshold)" ) # type: ignore
except AttributeError: Status.NO_AP_FOUND_IN_AUTHMODE_THRESHOLD = Status( 211                                           , "No AP Found (AuthMode Threshold)" )
try:                   Status.NO_AP_FOUND_IN_RSSI_THRESHOLD     = Status(network.STAT_NO_AP_FOUND_IN_RSSI_THRESHOLD     , "No AP Found (RSSI Threshold)"     ) # type: ignore
except AttributeError: Status.NO_AP_FOUND_IN_RSSI_THRESHOLD     = Status( 212                                           , "No AP Found (RSSI Threshold)"     )
try:                   Status.IDLE                              = Status(network.STAT_IDLE                              , "Idle"                             ) # type: ignore
except AttributeError: Status.IDLE                              = Status(1000                                           , "Idle"                             )
try:                   Status.CONNECTING                        = Status(network.STAT_CONNECTING                        , "Connecting"                       ) # type: ignore
except AttributeError: Status.CONNECTING                        = Status(1001                                           , "Connecting"                       )
try:                   Status.GOT_IP                            = Status(network.STAT_GOT_IP                            , "Got IP"                           ) # type: ignore
except AttributeError: Status.GOT_IP                            = Status(1010                                           , "Got IP"                           )

class PowerManagement:
  """WLAN power management modes (network.WLAN.PM_*)"""
  def __init__(self, code: int, name: str):
    self.code: int = code
    self.name: str = name
  def __str__(self) -> str:
    return f"PowerManagement({self.code}, {self.name})"
  def __eq__(self, other: "PowerManagement") -> bool: # type: ignore
    return self.code == other.code and self.name == other.name
  @classmethod
  def query(cls, code: int) -> "PowerManagement":
    for pm in cls.__dict__.values():
      if isinstance(pm, cls):
        if pm.code == code:
          return pm
    raise ValueError(f"Unknown PowerManagement code: {code}")
  NONE       : "PowerManagement"
  PERFORMANCE: "PowerManagement"
  POWERSAVE  : "PowerManagement"
try:                   PowerManagement.NONE        = PowerManagement(network.WLAN.PM_NONE       , "NONE"          ) # type: ignore
except AttributeError: PowerManagement.NONE        = PowerManagement(0                          , "NONE"          )
try:                   PowerManagement.PERFORMANCE = PowerManagement(network.WLAN.PM_PERFORMANCE, "PERFORMANCE"   ) # type: ignore
except AttributeError: PowerManagement.PERFORMANCE = PowerManagement(1                          , "PERFORMANCE"   )
try:                   PowerManagement.POWERSAVE   = PowerManagement(network.WLAN.PM_POWERSAVE  , "POWERSAVE"     ) # type: ignore
except AttributeError: PowerManagement.POWERSAVE   = PowerManagement(2                          , "POWERSAVE"     )


class Security:
  """WLAN security modes (network.WLAN.SEC_*)"""
  def __init__(self, code: int, name: str):
    self.code: int = code
    self.name: str = name
  def __str__(self) -> str:
    return f"Security({self.code}, {self.name})"
  def __eq__(self, other: "Security") -> bool: # type: ignore
    return self.code == other.code and self.name == other.name
  @classmethod
  def query(cls, code: int) -> "Security":
    for security in cls.__dict__.values():
      if isinstance(security, cls):
        if security.code == code:
          return security
    raise ValueError(f"Unknown Security code: {code}")
  OPEN                    : "Security"
  WEP                     : "Security"
  WPA                     : "Security"
  WPA2                    : "Security"
  WPA_WPA2                : "Security"
  WPA2_ENT                : "Security"
  WPA3                    : "Security"
  WPA2_WPA3               : "Security"
  WAPI                    : "Security"
  OWE                     : "Security"
  WPA3_ENT_192            : "Security"
  WPA3_EXT_PSK            : "Security"
  WPA3_EXT_PSK_MIXED_MODE : "Security"
  DPP                     : "Security"
  WPA3_ENT                : "Security"
  WPA2_WPA3_ENT           : "Security"
try:                   Security.OPEN                    = Security(network.WLAN.SEC_OPEN                    , "OPEN"                    ) # type: ignore
except AttributeError: Security.OPEN                    = Security(0                          , "OPEN"                    )
try:                   Security.WEP                     = Security(network.WLAN.SEC_WEP                     , "WEP"                     ) # type: ignore
except AttributeError: Security.WEP                     = Security(1                          , "WEP"                     )
try:                   Security.WPA                     = Security(network.WLAN.SEC_WPA                     , "WPA"                     ) # type: ignore
except AttributeError: Security.WPA                     = Security(2                          , "WPA"                     )
try:                   Security.WPA2                    = Security(network.WLAN.SEC_WPA2                    , "WPA2"                    ) # type: ignore
except AttributeError: Security.WPA2                    = Security(3                          , "WPA2"                    )
try:                   Security.WPA_WPA2                = Security(network.WLAN.SEC_WPA_WPA2                , "WPA_WPA2"                ) # type: ignore
except AttributeError: Security.WPA_WPA2                = Security(4                          , "WPA_WPA2"                )
try:                   Security.WPA2_ENT                = Security(network.WLAN.SEC_WPA2_ENT                , "WPA2_ENT"                ) # type: ignore
except AttributeError: Security.WPA2_ENT                = Security(5                          , "WPA2_ENT"                )
try:                   Security.WPA3                    = Security(network.WLAN.SEC_WPA3                    , "WPA3"                    ) # type: ignore
except AttributeError: Security.WPA3                    = Security(6                          , "WPA3"                    )
try:                   Security.WPA2_WPA3               = Security(network.WLAN.SEC_WPA2_WPA3               , "WPA2_WPA3"               ) # type: ignore
except AttributeError: Security.WPA2_WPA3               = Security(7                          , "WPA2_WPA3"               )
try:                   Security.WAPI                    = Security(network.WLAN.SEC_WAPI                    , "WAPI"                    ) # type: ignore
except AttributeError: Security.WAPI                    = Security(8                          , "WAPI"                    )
try:                   Security.OWE                     = Security(network.WLAN.SEC_OWE                     , "OWE"                     ) # type: ignore
except AttributeError: Security.OWE                     = Security(9                          , "OWE"                     )
try:                   Security.WPA3_ENT_192            = Security(network.WLAN.SEC_WPA3_ENT_192            , "WPA3_ENT_192"            ) # type: ignore
except AttributeError: Security.WPA3_ENT_192            = Security(10                         , "WPA3_ENT_192"            )
try:                   Security.WPA3_EXT_PSK            = Security(network.WLAN.SEC_WPA3_EXT_PSK            , "WPA3_EXT_PSK"            ) # type: ignore
except AttributeError: Security.WPA3_EXT_PSK            = Security(11                         , "WPA3_EXT_PSK"            )
try:                   Security.WPA3_EXT_PSK_MIXED_MODE = Security(network.WLAN.SEC_WPA3_EXT_PSK_MIXED_MODE , "WPA3_EXT_PSK_MIXED_MODE" ) # type: ignore
except AttributeError: Security.WPA3_EXT_PSK_MIXED_MODE = Security(12                         , "WPA3_EXT_PSK_MIXED_MODE" )
try:                   Security.DPP                     = Security(network.WLAN.SEC_DPP                     , "DPP"                     ) # type: ignore
except AttributeError: Security.DPP                     = Security(13                         , "DPP"                     )
try:                   Security.WPA3_ENT                = Security(network.WLAN.SEC_WPA3_ENT                , "WPA3_ENT"                ) # type: ignore
except AttributeError: Security.WPA3_ENT                = Security(14                         , "WPA3_ENT"                )
try:                   Security.WPA2_WPA3_ENT           = Security(network.WLAN.SEC_WPA2_WPA3_ENT           , "WPA2_WPA3_ENT"           ) # type: ignore
except AttributeError: Security.WPA2_WPA3_ENT           = Security(15                         , "WPA2_WPA3_ENT"           )

class Mode:
  """WLAN operating modes (network.*_IF)"""
  def __init__(self, code: int, name: str):
    self.code: int = code
    self.name: str = name
  def __str__(self) -> str:
    return f"Mode({self.code}, {self.name})"
  def __eq__(self, other: "Mode") -> bool: # type: ignore
    return self.code == other.code and self.name == other.name
  @classmethod
  def query(cls, code: int) -> "Mode":
    for mode in cls.__dict__.values():
      if isinstance(mode, cls):
        if mode.code == code:
          return mode
    raise ValueError(f"Unknown Mode code: {code}")
  STA : "Mode"
  AP  : "Mode"
try:                   Mode.STA = Mode(network.STA_IF, "STA") # type: ignore
except AttributeError: Mode.STA = Mode(0, "STA")
try:                   Mode.AP  = Mode(network.AP_IF , "AP" ) # type: ignore
except AttributeError: Mode.AP  = Mode(1, "AP" )

class WLANScanData:
  def __init__(self, ssid: bytes, bssid: bytes, channel: int, rssi: int, authmode: int, hidden: bool, encode: str = "utf-8"):
    self.ssid: bytes = ssid
    self.bssid: bytes = bssid
    self.channel: int = channel
    self.rssi: int = rssi
    self.authmode: int = authmode
    self.hidden: bool = hidden
    self.encode: str = encode
  def __str__(self) -> str:
    ssid = self.ssid.decode(self.encode)
    bssid = ':'.join(['{:02x}'.format(b) for b in self.bssid])
    return f"WLANScanData(ssid={ssid:32s}, bssid={bssid}, channel={self.channel:2d}, rssi={self.rssi:4d}, authmode={self.authmode:1d}, hidden={self.hidden:1d})"
  def __repr__(self) -> str:
    return self.__str__()

class Config:
  """Configuration container for WLAN connection and settings."""
  def __init__( self, 
                ssid: str | None = None, 
                password: str | None = None, 
                hostAddress: IP.IPV4Address | None = None, 
                subnet: IP.IPV4Address | None = None, 
                gateway: IP.IPV4Address | None = None, 
                dns: IP.IPV4Address | None = None, 
                hostname: str | None = None,
                mac: bytes | None = None,
                channel: int | None = None,
                reconnects: int | None = None,
                security: Security | None = None, 
                hidden: bool | None = None,
                key: str | None = None,
                txpower: int | float | None = None,
                pm: PowerManagement | None = None
  ) -> None:
    """Initializes a WiFi configuration container.
    Args:
      ssid (str | None): The SSID of the WLAN network to connect to.
      password (str | None): The password of the WLAN network to connect to.
      hostAddress (IPV4Address | None): The IP address of the host.
      subnet (IPV4Address | None): The subnet of the WLAN network to connect to.
      gateway (IPV4Address | None): The gateway of the WLAN network to connect to.
      dns (IPV4Address | None): The DNS address of the WLAN network to connect to.
      hostname (str | None): The hostname of the host.
      mac (bytes | None): The MAC address of the host.
      channel (int | None): The channel of the WLAN network to connect to.
      reconnects (int | None): The number of reconnects to attempt.
      security (Security | None): The security of the WLAN network to connect to.
      hidden (bool | None): Whether the WLAN network is hidden or not.
      key (str | None): The key of the WLAN network to connect to.
      txpower (int | float | None): The transmission power of the WLAN network to connect to.
      pm (PowerManagement | None): The power management of the WLAN network to connect to.
    """
    self.ssid: str | None = ssid
    self.password: str | None = password
    self.hostAddress: IP.IPV4Address | None = hostAddress
    self.subnet: IP.IPV4Address | None = subnet
    self.gateway: IP.IPV4Address | None = gateway
    self.dns: IP.IPV4Address | None = dns
    self.hostname: str | None = hostname
    self.mac: bytes | None = mac
    self.channel: int | None = channel
    self.reconnects: int | None = reconnects
    self.security: Security | None = security
    self.hidden: bool | None = hidden
    self.key: str | None = key
    self.txpower: int | float | None = txpower
    self.pm: PowerManagement | None = pm
  def __str__(self) -> str:
    return f"Config({self.ssid}, {self.password})"
  def to_dict(self) -> dict:
    """Converts configuration attributes to a dictionary for wlan.config() calls.
    This function first tries to convert the ifconfig parameters (hostAddress, subnet, gateway, dns) to a dictionary, and then tries to convert the wlan.config() parameters (hostname, mac, channel, reconnects, security, hidden, key, txpower, pm) to the same dictionary.
    If any Exception occurs during the conversion, it is caught, logged as an error, and then re-raised.
    Returns:
      dict: A dictionary containing the configuration attributes.
    """
    config = {}
    try: # ifconfig parameters (used for static IP configuration)
      if self.hostAddress is not None:
        config['ip'] = self.hostAddress.__str__()
      if self.subnet is not None:
        config['subnet'] = self.subnet.__str__()
      if self.gateway is not None:
        config['gateway'] = self.gateway.__str__()
      if self.dns is not None:
        config['dns'] = self.dns.__str__()
    except Exception as e:
      raise e
    try: # wlan.config() parameters
      if self.hostname is not None:
        config['hostname'] = self.hostname
      if self.mac is not None:
        config['mac'] = self.mac
      if self.channel is not None:
        config['channel'] = self.channel
      if self.reconnects is not None:
        config['reconnects'] = self.reconnects
      if self.security is not None:
        config['security'] = self.security.code
      if self.hidden is not None:
        config['hidden'] = self.hidden
      if self.key is not None:
        config['key'] = self.key
      if self.txpower is not None:
        config['txpower'] = self.txpower
      if self.pm is not None:
        config['pm'] = self.pm.code
    except Exception as e:
      raise e
    return config
class Connector:
  def __init__(self, interface: Mode = Mode.STA, hostname: str | None = None, 
               retry: int = 8, interval_ms: int = 256, timeout_ms: int = 8192, logger: Logging.Logger | None = None) -> None:
    """Initializes the Wi-Fi Connector with the given parameters.
    Arg:
      interface (Mode): The interface to use for Wi-Fi connection. Defaults to Mode.STA.
      hostname (str | None): The hostname of the host. Defaults to None.
      retry (int): The number of times to retry connecting to the network. Defaults to 8.
      interval_ms (int): The interval at which the Wi-Fi interface is checked for activity. Defaults to 200.
      timeout_ms (int): The timeout for the Wi-Fi interface. Defaults to 10000.
      logger (Logging.Logger | None): The logger to use for logging. Defaults to None.
    Returns:
      None
    """
    self.retry: int = retry
    self.interval_ms: int = interval_ms
    self.timeout_ms: int = timeout_ms
    self.wlan = network.WLAN(interface.code)
    self.hostname: str | None = hostname
    self.config: Config | None = None
    self.logger: Logging.Logger | None = logger

  def _config_(self, config) -> None:
    """Applies wlan.config() settings and static IP settings (if applicable).
    
    Arg:
      config (WiFi.Config): The configuration to apply.
    
    Notes:
      If 'ip' is present in config, the static IP configuration will be applied with the provided values.
      If 'ip' is not present, the static IP configuration will not be changed.
      If 'hostname', 'mac', 'channel', 'reconnects', 'security', 'hidden', 'key', 'txpower', or 'pm' are present in config, they will be applied.
      If any of the above parameters are not present in config, their values will not be changed.
    """
    _config: Config = config
    if _config.hostname is None and self.hostname is not None: _config.hostname = self.hostname
    self.config = _config
    config_dict = self.config.to_dict()
    
    # Apply static IP configuration if provided
    if 'ip' in config_dict:
      ip_config_tuple = (config_dict['ip'], 
                         config_dict.get('subnet', '255.255.255.0'), 
                         config_dict.get('gateway', '0.0.0.0'), 
                         config_dict.get('dns', '8.8.8.8'))
      self.wlan.ifconfig(tuple(ip_config_tuple))
      if self.logger is not None: self.logger.debug(f"Static IP configuration applied: {ip_config_tuple}")

    # Apply general configuration parameters
    config_params = {
      'hostname': None, 'mac': None, 'channel': None, 'reconnects': None, 
      'security': None, 'hidden': None, 'key': None, 'txpower': None, 'pm': None
    }
    for key in config_params.keys():
      if key in config_dict:
        try:
          self.wlan.config(**{key: config_dict[key]})
          if self.logger is not None: self.logger.debug(f"Config param '{key}' set to '{config_dict[key]}'")
        except (ValueError, TypeError) as e:
          # Log non-critical errors for unsupported config keys
          raise Exception(f"Warning: Could not set config param '{key}'. Error: {e}")
  def isConnecting(self) -> bool:
    status = Status.query(self.wlan.status())
    if self.logger is not None: self.logger.debug(f"Checking is connecting, current Status is {status}.")
    return status in (Status.CONNECTING, Status.IDLE)
  def getAvailableNetworks(self) -> list[WLANScanData]:
    if not self.wlan.active():
      self.wlan.active(True)
    return [WLANScanData(*scanData) for scanData in self.wlan.scan()]
  def getConfig(self, configName: str):
    return self.wlan.config(configName)
  def getSSID(self) -> str:
    return self.wlan.config("essid")
  def getPassword (self) -> str:
    return self.wlan.config("password")
  def getHostIP(self) -> IP.IPV4Address:
    return IP.IPV4Address(self.wlan.ifconfig()[0])
  def getNetmask(self) -> IP.IPV4Address:
    return IP.IPV4Address(self.wlan.ifconfig()[1])
  def getGateway(self) -> IP.IPV4Address:
    return IP.IPV4Address(self.wlan.ifconfig()[2])
  def getDNS(self) -> IP.IPV4Address:
    return IP.IPV4Address(self.wlan.ifconfig()[3])
  def getMAC_Bytes(self) -> bytes:
    return self.wlan.config("mac")
  def getMAC_Str(self) -> str:
    return ":".join([f"{b:02X}" for b in self.getMAC_Bytes()])
  def getHostname(self) -> str:
    try: 
      return self.wlan.config("dhcp_hostname")
    except:
      return self.wlan.config("hostname")
  def isConnected(self) -> bool:
    return self.wlan.isconnected()

class SyncConnector(Connector):
  """Handles Synchronous activation, connection, and configuration of the Wi-Fi interface."""
  def activate(self) -> bool:
    """Activates the Wi-Fi interface.

    Returns:
      bool: True if the Wi-Fi interface was successfully activated, False otherwise.
    """
    if self.wlan.active(): return True
    for _ in range(self.retry):
      self.wlan.active(True)
      if Sleep.sync_until_sync(lambda: self.wlan.active(), self.timeout_ms, self.interval_ms):
        break
    return self.wlan.active()
  def deactivate(self) -> bool:
    """Deactivates the Wi-Fi interface.

    Returns:
      bool: True if the Wi-Fi interface was successfully deactivated, False otherwise.
    """
    if not self.wlan.active(): return True
    for _ in range(self.retry):
      self.wlan.active(False)
      if Sleep.sync_until_sync(lambda: not self.wlan.active(), self.timeout_ms, self.interval_ms):
        break
    return not self.wlan.active()

  def connect(self, config: Config) -> Status:
    """Connects to a Wi-Fi network.

    Returns:
      bool: True if the connection was successfully established, False otherwise.
    """
    # Ensure the interface is active
    if not self.wlan.active() and not self.activate():
      return Status.UNABLE_TO_ACTIVATE_CONNECTOR

    # Ensure the interface is disconnected
    if self.wlan.isconnected() and not self.disconnect():
      return Status.UNABLE_TO_CLOSE_OLD_CONNECTION

    # Apply configuration
    self._config_(config)

    # Wait for the connection process to complete
    for i in range(self.retry):
      if self.logger is not None: self.logger.info(f"Wifi connecting... ({i+1}/{self.retry})")
      try:
        self.wlan.connect(config.ssid, config.password)
        if Sleep.sync_until_sync(lambda: not self.isConnecting(), self.timeout_ms, self.interval_ms):
          return Status.query(self.wlan.status())
      except OSError as error: # WiFi Internal Error
        if self.logger is not None: self.logger.warning("WiFi Internal Error")
        # return Status.WIFI_INTERNAL_ERROR
    return Status.query(self.wlan.status())
  def tryConnect(self, configs: list[Config], encoding: str = "utf-8") -> bool:
    """Connects to a Wi-Fi network using the provided list of configurations.

    Args:
      configs (list[Config]): The list of configurations to use when connecting to the Wi-Fi network.
      encoding (str, optional): The encoding to use for the SSID. Defaults to "utf-8".

    Returns:
      bool: True if the connection was successfully established, False otherwise.
    """
    # Ensure the interface is active
    if not self.wlan.active() and not self.activate():
      return False

    # Try to connect to the available networks
    connectable: list[WLANScanData] = self.getAvailableNetworks()
    for config in configs:
      config_hidden: bool = config.hidden if config.hidden is not None else False
      for scanData in connectable:
        if config_hidden or scanData.ssid.decode(encoding) == (config.ssid if encoding is not None else ""):
          connectStatus = self.connect(config)
          if connectStatus == Status.GOT_IP:
            if self.logger is not None: self.logger.info(f"Sussessfully Connected to \"{config.ssid}\"")
            return True
          else:
            if self.logger is not None: self.logger.warning(f"Failed to connect to \"{config.ssid}\", status: {connectStatus}")
            Sleep.sync_ms(self.interval_ms)
    return False
  def disconnect(self) -> bool:
    """Disconnects from the Wi-Fi network.

    Returns:
      bool: True if the disconnection was successful, False otherwise.
    """
    if not self.wlan.isconnected():
      return True
    for _ in range(self.retry):
      self.wlan.disconnect()
      if Sleep.sync_until_sync(lambda: not self.wlan.isconnected(), self.timeout_ms, self.interval_ms):
        break
    return not self.wlan.isconnected()
  def delete(self):
    self.disconnect()
    self.deactivate()
  def __del__(self):
    self.delete()

class AsyncConnector(Connector):
  """Handles Asynchronous activation, connection, and configuration of the Wi-Fi interface."""
  async def activate(self) -> bool:
    """Activates the Wi-Fi interface.

    Returns:
      bool: True if the Wi-Fi interface was successfully activated, False otherwise.
    """
    if self.wlan.active(): return True
    for _ in range(self.retry):
      self.wlan.active(True)
      if await Sleep.async_until_sync(lambda: self.wlan.active(), self.timeout_ms, self.interval_ms):
        break
    return self.wlan.active()
  async def deactivate(self) -> bool:
    """Deactivates the Wi-Fi interface.

    Returns:
      bool: True if the Wi-Fi interface was successfully deactivated, False otherwise.
    """
    if not self.wlan.active(): return True
    for _ in range(self.retry):
      self.wlan.active(False)
      if await Sleep.async_until_sync(lambda: not self.wlan.active(), self.timeout_ms, self.interval_ms):
        break
    return not self.wlan.active()

  async def connect(self, config: Config) -> Status:
    """Connects to a Wi-Fi network.

    Returns:
      bool: True if the connection was successfully established, False otherwise.
    """
    # Ensure the interface is active
    if not self.wlan.active() and not await self.activate():
      return Status.UNABLE_TO_ACTIVATE_CONNECTOR

    # Ensure the interface is disconnected
    if self.wlan.isconnected() and not await self.disconnect():
      return Status.UNABLE_TO_CLOSE_OLD_CONNECTION

    # Apply configuration
    self._config_(config)

    # Wait for the connection process to complete
    for i in range(self.retry):
      if self.logger is not None: self.logger.info(f"Wifi connecting... ({i+1}/{self.retry})")
      try:
        self.wlan.connect(config.ssid, config.password)
        if await Sleep.async_until_sync(lambda: not self.isConnecting(), self.timeout_ms, self.interval_ms):
          return Status.query(self.wlan.status())
      except OSError as error: # WiFi Internal Error
        if self.logger is not None: self.logger.warning("WiFi Internal Error")
        # return Status.WIFI_INTERNAL_ERROR
    return Status.query(self.wlan.status())
  async def tryConnect(self, configs: list[Config], encoding: str = "utf-8") -> bool:
    """Connects to a Wi-Fi network using the provided list of configurations.

    Args:
      configs (list[Config]): The list of configurations to use when connecting to the Wi-Fi network.
      encoding (str, optional): The encoding to use for the SSID. Defaults to "utf-8".

    Returns:
      bool: True if the connection was successfully established, False otherwise.
    """
    # Ensure the interface is active
    if not self.wlan.active() and not await self.activate():
      return False

    # Try to connect to the available networks
    connectable: list[WLANScanData] = self.getAvailableNetworks()
    for config in configs:
      config_hidden: bool = config.hidden if config.hidden is not None else False
      for scanData in connectable:
        if config_hidden or scanData.ssid.decode(encoding) == (config.ssid if encoding is not None else ""):
          connectStatus = await self.connect(config)
          if connectStatus == Status.GOT_IP:
            if self.logger is not None: self.logger.info(f"Sussessfully Connected to \"{config.ssid}\"")
            return True
          else:
            if self.logger is not None: self.logger.warning(f"Failed to connect to \"{config.ssid}\", status: {connectStatus}")
            await Sleep.async_ms(self.interval_ms)
    return False
  async def disconnect(self) -> bool:
    """Disconnects from the Wi-Fi network.

    Returns:
      bool: True if the disconnection was successful, False otherwise.
    """
    if not self.wlan.isconnected():
      return True
    for _ in range(self.retry):
      self.wlan.disconnect()
      if await Sleep.async_until_sync(lambda: not self.wlan.isconnected(), self.timeout_ms, self.interval_ms):
        break
    return not self.wlan.isconnected()
  async def delete(self):
    await self.disconnect()
    await self.deactivate()
  def __del__(self):
    uasyncio.get_event_loop().create_task(self.delete())
