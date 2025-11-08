# Network/WiFi.py
import network

try: 
  from ..Utils import Logging
  from ..System import Sleep
  from . import Basic as NetworkBasic
except ImportError:
  from micropython_esp32_lib.Utils import Logging
  from micropython_esp32_lib.System import Sleep
  from micropython_esp32_lib.Network import Basic as NetworkBasic

class Config:
  """Configuration container for WLAN connection and settings."""
  def __init__( self, 
                ssid: str | None = None, 
                password: str | None = None, 
                hostAddress: NetworkBasic.IPV4Address | None = None, 
                subnet: NetworkBasic.IPV4Address | None = None, 
                gateway: NetworkBasic.IPV4Address | None = None, 
                dns: NetworkBasic.IPV4Address | None = None, 
                hostname: str | None = None,
                mac: bytes | None = None,
                channel: int | None = None,
                reconnects: int | None = None,
                security = None, 
                hidden: bool | None = None,
                key: str | None = None,
                txpower: int | float | None = None,
                pm = None, 
                log_name: str = "WiFi Config",
                log_level: Logging.Level = Logging.LEVEL.WARNING) -> None:
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
      security (None): The security of the WLAN network to connect to.
      hidden (bool | None): Whether the WLAN network is hidden or not.
      key (str | None): The key of the WLAN network to connect to.
      txpower (int | float | None): The transmission power of the WLAN network to connect to.
      pm (PowerManagement | None): The power management of the WLAN network to connect to.
      log_level (Logging.Level, optional): The log level for reporting status. Defaults to Logging.LEVEL.INFO.
    """
    self.ssid: str | None = ssid
    self.password: str | None = password
    self.hostAddress: NetworkBasic.IPV4Address | None = hostAddress
    self.subnet: NetworkBasic.IPV4Address | None = subnet
    self.gateway: NetworkBasic.IPV4Address | None = gateway
    self.dns: NetworkBasic.IPV4Address | None = dns
    self.hostname: str | None = hostname
    self.mac: bytes | None = mac
    self.channel: int | None = channel
    self.reconnects: int | None = reconnects
    self.security = security
    self.hidden: bool | None = hidden
    self.key: str | None = key
    self.txpower: int | float | None = txpower
    self.pm: NetworkBasic.PowerManagement | None = pm
    self.logger = Logging.Log(log_name, log_level)
  def __str__(self) -> str:
    return f"WiFi.Config({self.ssid}, {self.password})"
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
      self.logger.error(e.__str__())
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
        config['security'] = self.security
      if self.hidden is not None:
        config['hidden'] = self.hidden
      if self.key is not None:
        config['key'] = self.key
      if self.txpower is not None:
        config['txpower'] = self.txpower
      if self.pm is not None:
        config['pm'] = self.pm
    except Exception as e:
      self.logger.error(e.__str__())
      raise e
    return config
class Connector:
  """Handles activation, connection, and configuration of the Wi-Fi interface."""
  def __init__(self, interface: NetworkBasic.Mode = NetworkBasic.MODE.STA, interval_ms: int = 100, connecting_timeout_ms: int = 10000, idle_timeout_ms: int = 10000, log_name: str = "Wi-Fi Connector", log_level: Logging.Level = Logging.LEVEL.INFO) -> None:
    """Initializes the Wi-Fi Connector with the given parameters.
    Parameters:
      interface (int): The mode of the Wi-Fi interface (default: MODE.STA).
      interval_ms (int): The interval at which the Wi-Fi interface is checked for activity (default: 100).
      connecting_timeout_ms (int): The timeout for connecting to a Wi-Fi network (default: 10000).
      idle_timeout_ms (int): The timeout for idling the Wi-Fi interface (default: 10000).
      log_level (Logging.Level, optional): The log level for reporting status. Defaults to Logging.LEVEL.INFO.
    Returns:
      None
    """
    self.interval_ms: int = interval_ms
    self.connecting_timeout_ms: int = connecting_timeout_ms
    self.idle_timeout_ms: int = idle_timeout_ms
    self.logger: Logging.Log = Logging.Log(name=log_name, level=log_level)
    self.wlan = network.WLAN(interface.value)
    self.config: Config | None = None
  def activate(self, timeout_ms: int = -1, retry_count: int = 8, retry_interval_ms: int | None = None) -> bool:
    """Activates the Wi-Fi interface.
    Parameters:
      timeout_ms (int): The timeout for waiting for the Wi-Fi interface to become active (default: -1).
      retry_count (int): The number of times to retry activating the Wi-Fi interface (default: 8).
      retry_interval_ms (int | None): The interval at which to retry activating the Wi-Fi interface (default: None).
    Returns:
      bool: True if the Wi-Fi interface was successfully activated, False otherwise.
    Notes:
      If timeout_ms is -1, the function will not wait for the Wi-Fi interface to become active.
      If retry_interval_ms is None, the function will use the interval_ms attribute of the class instance.
    """
    if retry_interval_ms is None: retry_interval_ms = self.interval_ms
    if not self.wlan.active():
      self.logger.info("Activing... ")
      self.wlan.active(True)
      for i in range(retry_count):
        if Sleep.sync_wait_until(lambda: self.wlan.active(), timeout_ms=timeout_ms, interval_ms=retry_interval_ms):
          break
        self.logger.info("Activing... ")
      if self.wlan.active():
        self.logger.info("Activated.")
        return True
      else:
        self.logger.warning("Failed to activate.")
        return False
    else:
      self.logger.info("WiFi is already actived.")
      return True
    
  def deactivate(self, timeout_ms: int = -1, retry_count: int = 8, retry_interval_ms: int | None = None) -> bool:
    """Deactivates the Wi-Fi interface.
    Parameters:
      timeout_ms (int): The timeout for waiting for the Wi-Fi interface to become inactive (default: -1).
      retry_count (int): The number of times to retry deactivating the Wi-Fi interface (default: 8).
      retry_interval_ms (int | None): The interval at which to retry deactivating the Wi-Fi interface (default: None).
    Returns:
      None
    Notes:
      If timeout_ms is -1, the function will not wait for the Wi-Fi interface to become inactive.
      If retry_interval_ms is None, the function will use the interval_ms attribute of the class instance.
    """
    if retry_interval_ms is None: retry_interval_ms = self.interval_ms
    if self.wlan.active():
      self.logger.info("Deactiving... ")
      self.wlan.active(False)
      for i in range(retry_count):
        if Sleep.sync_wait_until(lambda: not self.wlan.active(), timeout_ms=timeout_ms, interval_ms=retry_interval_ms):
          break
        self.logger.info("Deactiving... ")
      if not self.wlan.active():
        self.logger.info("Deactivated.")
        return True
      else:
        self.logger.warning("Failed to deactivate.")
        return False
    else:
      self.logger.info("WiFi is already deactivated.")
      return True
  def _config_(self, config) -> None:
    """Applies wlan.config() settings and static IP settings (if applicable).
    
    Parameters:
        config (WiFi.Config): The configuration to apply.
    
    Notes:
        If 'ip' is present in config, the static IP configuration will be applied with the provided values.
        If 'ip' is not present, the static IP configuration will not be changed.
        If 'hostname', 'mac', 'channel', 'reconnects', 'security', 'hidden', 'key', 'txpower', or 'pm' are present in config, they will be applied.
        If any of the above parameters are not present in config, their values will not be changed.
    """
    _config: Config = config
    self.config = _config
    config_dict = self.config.to_dict()
    
    # Apply static IP configuration if provided
    if 'ip' in config_dict:
        ip_config_tuple = (config_dict['ip'], config_dict.get('subnet', '255.255.255.0'), config_dict.get('gateway', '0.0.0.0'), config_dict.get('dns', '8.8.8.8'))
        self.logger.info(f"Setting static IP config: {ip_config_tuple}")
        self.wlan.ifconfig(tuple(ip_config_tuple))
            
    # Apply general configuration parameters
    config_params = {
        'hostname': None, 'mac': None, 'channel': None, 'reconnects': None, 
        'security': None, 'hidden': None, 'key': None, 'txpower': None, 'pm': None
    }
    for key in config_params.keys():
        if key in config_dict:
            try:
                self.wlan.config(**{key: config_dict[key]})
            except (ValueError, TypeError) as e:
                # Log non-critical errors for unsupported config keys
                self.logger.warning(f"Warning: Could not set config param '{key}'. Error: {e}")
  def connect(self, config: Config, timeout_ms: int = -1, retry_count: int = 8, retry_interval_ms: int | None = None) -> bool:
    """Connects to a Wi-Fi network using the provided configuration.
    Parameters:
        config (Config): The configuration to use when connecting to the Wi-Fi network.
        timeout_ms (int): The timeout for waiting for the Wi-Fi interface to become active (default: -1).
        retry_count (int): The number of times to retry activating the Wi-Fi interface (default: 8).
        retry_interval_ms (int | None): The interval at which to retry activating the Wi-Fi interface (default: None).
    Returns:
        bool: True if the Wi-Fi interface was successfully connected, False otherwise.
    Notes:
        If timeout_ms is -1, the function will not wait for the Wi-Fi interface to become active.
        If retry_interval_ms is None, the function will use the interval_ms attribute of the class instance.
    """
    if retry_interval_ms is None: retry_interval_ms = self.interval_ms
    _config: Config = config
    if not self.wlan.active():
      self.logger.info("WiFi is not actived. Activating now.")
      if not self.activate(timeout_ms=timeout_ms, retry_count=retry_count, retry_interval_ms=retry_interval_ms):
        self.logger.warning("Connection aborted: WiFi failed to activate.")
        return False
    if self.wlan.isconnected():
      self.logger.info("WiFi already connected. Reconnecting now.")
      if not self.disconnect(timeout_ms=timeout_ms, retry_count=retry_count, retry_interval_ms=retry_interval_ms):
        self.logger.warning("Connection aborted: WiFi failed to disconnect.")
        return False
    # Apply configuration (like hostname, power mode, static IP)
    self._config_(_config)
    # Start the connection process
    if (_config.ssid is not None):
      self.logger.info(f"Attempting to connect to SSID: {_config.ssid}")
      self.wlan.connect(_config.ssid, _config.password if _config.password is not None else "")
    else:
      self.logger.warning("Connection aborted: SSID not provided.")
      return False
    # Wait for the connection process to complete
    if NetworkBasic.STATU.Statu(self.wlan.status()) == NetworkBasic.STATU.CONNECTING:
      for i in range(retry_count):
        self.logger.info("Wifi connecting... ({}/{})".format(i+1, retry_count))
        if Sleep.sync_wait_until(lambda: NetworkBasic.STATU.Statu(self.wlan.status()) != NetworkBasic.STATU.CONNECTING, timeout_ms=timeout_ms, interval_ms=self.interval_ms):
          self.logger.info("Wifi connected.")
          break
        else:
          self.logger.warning("Wifi connection timeout.")
          return False
    if NetworkBasic.STATU.Statu(self.wlan.status()) == NetworkBasic.STATU.IDLE:
      for i in range(retry_count):
        self.logger.info("Wifi idle... ({}/{})".format(i+1, retry_count))
        if Sleep.sync_wait_until(lambda: NetworkBasic.STATU.Statu(self.wlan.status()) != NetworkBasic.STATU.IDLE, timeout_ms=timeout_ms, interval_ms=self.interval_ms):
          self.logger.info("Wifi idle.")
          break
        else:
          self.logger.warning("Wifi idle timeout.")
          return False
    # Check the final connection status
    final_status = NetworkBasic.STATU.Statu(self.wlan.status())
    if final_status == NetworkBasic.STATU.GOT_IP:
      # ip_config: tuple[str, str, str, str] = self.wlan.ifconfig()
      self.logger.info(f"WiFi connected successfully. HostName: {self.getHostname()}, IP: {(self.getHostIP())}, MAC: {self.getMAC_Str()}")
      return True
    
    elif final_status == NetworkBasic.STATU.IDLE:
      self.logger.warning("WiFi connection failed: idle status")
    elif final_status == NetworkBasic.STATU.WRONG_PASSWORD:
      self.logger.warning("WiFi connection failed: wrong password")
    elif final_status == NetworkBasic.STATU.NO_AP_FOUND:
      self.logger.warning("WiFi connection failed: no AP found")
    elif final_status == NetworkBasic.STATU.CONNECT_FAIL:
      self.logger.warning("WiFi connection failed: connect fail")
    else:
      self.logger.warning("WiFi connection failed: unknown status")
    self.disconnect(timeout_ms=timeout_ms, retry_count=retry_count, retry_interval_ms=retry_interval_ms)
    self.deactivate(timeout_ms=timeout_ms, retry_count=retry_count, retry_interval_ms=retry_interval_ms)
    return False
  def tryConnect(self, configs: list[Config], timeout_ms: int = -1, retry_count: int = 8, retry_interval_ms: int | None = None) -> bool:
    """Connects to a Wi-Fi network using the provided list of configurations.
    Parameters:
        configs (list[Config]): The list of configurations to use when connecting to the Wi-Fi network.
        timeout_ms (int): The timeout for waiting for the Wi-Fi interface to become active (default: -1).
        retry_count (int): The number of times to retry activating the Wi-Fi interface (default: 8).
        retry_interval_ms (int | None): The interval at which to retry activating the Wi-Fi interface (default: None).
    Returns:
        bool: True if the Wi-Fi interface was successfully connected, False otherwise.
    Notes:
        If timeout_ms is -1, the function will not wait for the Wi-Fi interface to become active.
        If retry_interval_ms is None, the function will use the interval_ms attribute of the class instance.
    """
    for config in configs:
      if self.connect(config, timeout_ms=timeout_ms, retry_count=retry_count, retry_interval_ms=retry_interval_ms):
        return True
    return False
  def disconnect(self, timeout_ms: int = -1, retry_count: int = 8, retry_interval_ms: int | None = None) -> bool:
    """Disconnects from the current Wi-Fi network.
    Parameters:
        timeout_ms (int): The timeout for waiting for the Wi-Fi interface to become disconnected (default: -1).
        retry_count (int): The number of times to retry disconnecting the Wi-Fi interface (default: 8).
        retry_interval_ms (int | None): The interval at which to retry disconnecting the Wi-Fi interface (default: None).
    Returns:
        bool: True if the Wi-Fi interface was successfully disconnected, False otherwise.
    Notes:
        If timeout_ms is -1, the function will not wait for the Wi-Fi interface to become disconnected.
        If retry_interval_ms is None, the function will use the interval_ms attribute of the class instance.
    """
    if retry_interval_ms is None: retry_interval_ms = self.interval_ms
    if self.wlan.isconnected():
      self.wlan.disconnect()
      # Wait for disconnect
      for i in range(retry_count):
        self.logger.info("Wifi disconnecting... ({}/{})".format(i+1, retry_count))
        if Sleep.sync_wait_until(lambda: not self.wlan.isconnected() and NetworkBasic.Statu("", self.wlan.status()) == NetworkBasic.STATU.IDLE, timeout_ms=timeout_ms, interval_ms=self.interval_ms):
          self.logger.info("Wifi disconnected.")
          return True
        else:
          self.logger.warning("Wifi disconnect timeout.")
      if not self.wlan.isconnected():
        self.logger.info("Wifi disconnected.")
        return True
      else:
        self.logger.warning("Wifi disconnect failed.")
        return False
    else:
      self.logger.info("WiFi is not connected.")
      return True
  def __del__(self):
    self.disconnect()
    self.deactivate()
    self.logger.info("WiFi connection closed.")
  
  def getConfig(self, configName: str):
    return self.wlan.config(configName)
  def getSSID(self) -> str:
    return self.wlan.config("essid")
  def getPassword (self) -> str:
    return self.wlan.config("password")
  def getHostIP(self) -> NetworkBasic.IPV4Address:
    return NetworkBasic.IPV4Address(self.wlan.ifconfig()[0])
  def getNetmask(self) -> NetworkBasic.IPV4Address:
    return NetworkBasic.IPV4Address(self.wlan.ifconfig()[1])
  def getGateway(self) -> NetworkBasic.IPV4Address:
    return NetworkBasic.IPV4Address(self.wlan.ifconfig()[2])
  def getDNS(self) -> NetworkBasic.IPV4Address:
    return NetworkBasic.IPV4Address(self.wlan.ifconfig()[3])
  def getMAC_Bytes(self) -> bytes:
    return self.wlan.config("mac")
  def getMAC_Str(self) -> str:
    return "-".join([f"{b:02X}" for b in self.getMAC_Bytes()])
  def getHostname(self) -> str:
    try: 
      return self.wlan.config("dhcp_hostname")
    except:
      return self.wlan.config("hostname")
  def isConnected(self) -> bool:
    return self.wlan.isconnected()

if __name__ == '__main__':
  logger = Logging.Log("Test Network", Logging.LEVEL.INFO)
  logger.info("Test the WiFi connection")
  wifiConfig_list: list[Config] = [
    Config("SSID0", "PSWD0", hostname = "MicroPython"),
    Config("SSID1", "PSWD1", hostname = "MicroPython")
  ]
  logger.info("Connect WiFi...")
  wifi = Connector(log_level=Logging.LEVEL.INFO)
  for wifiConfig in wifiConfig_list:
    try: 
      if wifi.connect(wifiConfig, timeout_ms=10000, retry_count=8, retry_interval_ms=1000):
        logger.info(f"Connect WiFi Done.")
        break
      else:
        logger.warning(f"Connect WiFi Failed.")
    except Exception as e:
      logger.error(f"Connect WiFi Failed. Error: {e}")


