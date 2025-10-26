import network
import utime as time

warning_enable: bool = True

# WLAN.status(): 
#   `network.STAT_IDLE`: no connection and no activity,
#   `network.STAT_CONNECTING`: connecting in progress,
#   `network.STAT_WRONG_PASSWORD`: failed due to incorrect password,
#   `network.STAT_NO_AP_FOUND`: failed because no access point replied,
#   `network.STAT_CONNECT_FAIL`: failed due to other problems,
#   `network.STAT_GOT_IP`: connection successful.

try:
  NETWORK_STAT_CONNECTING: int = network.STAT_CONNECTING
  NETWORK_STAT_NO_AP_FOUND: int = network.STAT_NO_AP_FOUND
  NETWORK_STAT_WRONG_PASSWORD: int = network.STAT_WRONG_PASSWORD
  NETWORK_STAT_CONNECT_FAIL: int = network.STAT_CONNECT_FAIL
  NETWORK_STAT_IDLE: int = network.STAT_IDLE
  NETWORK_STAT_GOT_IP: int = network.STAT_GOT_IP
except AttributeError:
  if warning_enable: print("Warning: Network status constants (`network.STAT_*`) not found.")
  NETWORK_STAT_CONNECTING = 1001
  NETWORK_STAT_NO_AP_FOUND = 201
  NETWORK_STAT_WRONG_PASSWORD = 202
  NETWORK_STAT_CONNECT_FAIL = 203
  NETWORK_STAT_IDLE = 1000
  NETWORK_STAT_GOT_IP = 1010

# Allowed values for the WLAN.config(pm=...) network interface parameter:
# - `PM_PERFORMANCE`: enable WiFi power management to balance power savings and WiFi performance
# - `PM_POWERSAVE`: enable WiFi power management with additional power savings and reduced WiFi performance
# - `PM_NONE`: disable wifi power management
# --- FIX for missing network module constants ---
# Some Micropython ports or builds do not expose `network.PM_*` constants via the network module.
# We define fallbacks to the standard integer values (usually 0, 1, 2) if they are missing,
# while printing a warning to alert the user.

try:
  NETWORK_PM_NONE = network.PM_NONE
  NETWORK_PM_PERFORMANCE = network.PM_PERFORMANCE
  NETWORK_PM_POWERSAVE = network.PM_POWERSAVE
except AttributeError:
  if warning_enable: print("Warning: Network Power Management constants (`network.PM_*`) not found.")
  NETWORK_PM_NONE = 0
  NETWORK_PM_PERFORMANCE = 1 
  NETWORK_PM_POWERSAVE = 2

# `network.WLAN.IF_STA` (station aka client, connects to upstream WiFi access points) 
# `network.WLAN.IF_AP` (access point, allows other WiFi clients to connect)

try:
  NETWORK_MODE_STA = network.WLAN.STA_IF
  NETWORK_MODE_AP = network.WLAN.AP_IF
except AttributeError:
  if warning_enable: print("Warning: Network interface mode constants (`network.WLAN.STA_IF` and `network.WLAN.AP_IF`) not found.")
  try:
    NETWORK_MODE_STA = network.STA_IF
    NETWORK_MODE_AP = network.AP_IF
  except AttributeError:
    if warning_enable: print("Warning: Network interface mode constants (`network.STA_IF` and `network.AP_IF`) not found.")
    NETWORK_MODE_STA = 0
    NETWORK_MODE_AP = 1

class IPV4Address:
  """
  Represents an IPV4 address as a tuple of integers.
  NOTE: Micropython's wlan.ifconfig() returns strings, not integers.
  """
  def __init__(self, ip: tuple[int, int, int, int] | None = None) -> None:
    if ip is None:
      self.ip = (0, 0, 0, 0)
    elif len(ip) != 4:
      raise ValueError("IP address must have exactly 4 octets")
    else:
      for octet in ip:
        if not (0 <= octet <= 255):
          raise ValueError("Each octet must be between 0 and 255")
      self.ip: tuple[int, int, int, int] = ip

  def __str__(self) -> str:
    return ".".join(map(str, self.ip))
  
  def str(self) -> str:
    return self.__str__()
  
  def tuple(self) -> tuple[int, int, int, int]:
    return self.ip

class WLANConfig:
  """Configuration container for WLAN connection and settings."""
  def __init__( self, 
                ssid: str | None = None, 
                password: str | None = None, 
                localhost: IPV4Address | None = None, 
                subnet: IPV4Address | None = None, 
                gateway: IPV4Address | None = None, 
                dns: IPV4Address | None = None, 
                hostname: str | None = None,
                mac: bytes | None = None,
                channel: int | None = None,
                reconnects: int | None = None,
                security = None, 
                hidden: bool | None = None,
                key: str | None = None,
                txpower: int | float | None = None,
                pm = None) -> None:
    self.ssid: str | None = ssid
    self.password: str | None = password
    self.localhost: IPV4Address | None = localhost
    self.subnet: IPV4Address | None = subnet
    self.gateway: IPV4Address | None = gateway
    self.dns: IPV4Address | None = dns
    self.hostname: str | None = hostname
    self.mac: bytes | None = mac
    self.channel: int | None = channel
    self.reconnects: int | None = reconnects
    self.security = security
    self.hidden: bool | None = hidden
    self.key: str | None = key
    self.txpower: int | float | None = txpower
    self.pm = pm
  
  def to_dict(self) -> dict:
    """Converts configuration attributes to a dictionary for wlan.config() calls."""
    config = {}

    # ifconfig parameters (used for static IP configuration)
    if self.localhost is not None:
      config['ip'] = self.localhost.str()
    if self.subnet is not None:
      config['subnet'] = self.subnet.str()
    if self.gateway is not None:
      config['gateway'] = self.gateway.str()
    if self.dns is not None:
      config['dns'] = self.dns.str()
      
    # wlan.config() parameters
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
    return config

class WLANConnector:
  """Handles activation, connection, and configuration of the Wi-Fi interface."""
  def __init__(self, interface_mode: int = NETWORK_MODE_STA, interval_ms: int = 100, connecting_timeout_ms: int = 10000, idle_timeout_ms: int = 10000, loger_perfix: str | None = None) -> None:
    self.interval_ms: int = interval_ms
    self.connecting_timeout_ms: int = connecting_timeout_ms
    self.idle_timeout_ms: int = idle_timeout_ms
    self.loger_perfix: str | None = loger_perfix
    self.wlan = network.WLAN(interface_mode)

  def activate(self) -> None:
    """Activates the WLAN interface."""
    if not self.wlan.active():
      if self.loger_perfix is not None: print(self.loger_perfix, "WLAN activing... ", end="")
      self.wlan.active(True)
      # Wait for interface to become active (optional, but good practice)
      max_wait_time = 5000 # 5 seconds
      start_time = time.ticks_ms()
      while not self.wlan.active() and time.ticks_diff(time.ticks_ms(), start_time) < max_wait_time:
        time.sleep_ms(self.interval_ms)
      
      if self.wlan.active():
        if self.loger_perfix is not None: print(self.loger_perfix, "done.")
      else:
        if self.loger_perfix is not None: print(self.loger_perfix, "failed to activate.")
    else:
      if self.loger_perfix is not None: print(self.loger_perfix, "WLAN is already actived.")

  def deactivate(self) -> None:
    """Deactivates the WLAN interface."""
    if self.wlan.active():
      if self.loger_perfix is not None: print(self.loger_perfix, "WLAN deactivate... ", end="")
      self.wlan.active(False)
      # Wait for interface to become inactive
      while self.wlan.active(): # Check if it's still active
        time.sleep_ms(self.interval_ms)
      if self.loger_perfix is not None: print(self.loger_perfix, "done.")
    else:
      if self.loger_perfix is not None: print(self.loger_perfix, "WLAN is already deactivated.")

  def _config_(self, config: WLANConfig) -> None:
    """
    Applies wlan.config() settings and static IP settings (if applicable).
    Using try-except blocks as not all parameters are supported on all ports/interfaces.
    
    ## WLAN.ifconfig: `nic.ifconfig(('192.168.0.4', '255.255.255.0', '192.168.0.1', '8.8.8.8'))`

    ## WLAN.config: `WLAN.config('param')` or `WLAN.config(param=value, ...)`

    Set WiFi access point name (formally known as SSID) and WiFi channel: `ap.config(ssid='My AP', channel=11)`

    Query params one by one: `print(ap.config('ssid'))` or `print(ap.config('channel'))`

    | Parameter | Description |
    | mac | MAC address (bytes) |
    | ssid | WiFi access point name (string) |
    | channel | WiFi channel (integer). Depending on the port this may only be supported on the AP interface. |
    | hidden | Whether SSID is hidden (boolean) |
    | security | Security protocol supported (enumeration, see module constants) |
    | key | Access key (string) |
    | hostname | The hostname that will be sent to DHCP (STA interfaces) and mDNS (if supported, both STA and AP). (Deprecated, use network.hostname() instead) |
    | reconnects | Number of reconnect attempts to make (integer, 0=none, -1=unlimited) |
    | txpower | Maximum transmit power in dBm (integer or float) |
    | pm | WiFi Power Management setting (see below for allowed values) |
    """
    config_dict = config.to_dict()
    
    # Apply static IP configuration if provided
    ip_config_tuple = []
    if 'ip' in config_dict:
        ip_config_tuple.append(config_dict['ip'])
        ip_config_tuple.append(config_dict.get('subnet', '255.255.255.0'))
        ip_config_tuple.append(config_dict.get('gateway', '0.0.0.0'))
        ip_config_tuple.append(config_dict.get('dns', '8.8.8.8'))
        
        if len(ip_config_tuple) == 4:
             if self.loger_perfix is not None: print(self.loger_perfix, f"Setting static IP config: {ip_config_tuple}")
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
                if self.loger_perfix is not None: print(self.loger_perfix, f"Warning: Could not set config param '{key}'. Error: {e}")


  def connect(self, config: WLANConfig) -> bool:
    """Connects to the Wi-Fi network using the provided configuration."""
    if not self.wlan.active():
      if self.loger_perfix is not None: print(self.loger_perfix, "WLAN is not actived. Activating now.")
      self.activate()
      if not self.wlan.active():
          if self.loger_perfix is not None: print(self.loger_perfix, "Connection aborted: WLAN failed to activate.")
          return False

    if self.wlan.isconnected():
      if self.loger_perfix is not None: print(self.loger_perfix, "WLAN already connected. Disconnecting before new attempt.")
      self.disconnect()

    # Apply configuration (like hostname, power mode, static IP)
    self._config_(config)

    # Start the connection process
    if (config.ssid is not None):
      if self.loger_perfix is not None: print(self.loger_perfix, f"Attempting to connect to SSID: {config.ssid}")
      self.wlan.connect(config.ssid, config.password or '')
    else:
      if self.loger_perfix is not None: print(self.loger_perfix, "Connection aborted: SSID not provided.")
      return False

    # Wait for the connection process to complete
    start_time = time.ticks_ms()
    if self.wlan.status() == NETWORK_STAT_CONNECTING:
      if self.loger_perfix is not None: print(self.loger_perfix, "WLAN connecting... ", end="")
      while self.wlan.status() == NETWORK_STAT_CONNECTING and time.ticks_diff(time.ticks_ms(), start_time) < self.connecting_timeout_ms:
        time.sleep_ms(self.interval_ms)
      if self.loger_perfix is not None: print(self.loger_perfix, "done.")
    
    start_time = time.ticks_ms()
    if self.wlan.status() == NETWORK_STAT_IDLE:
      if self.loger_perfix is not None: print(self.loger_perfix, "WLAN idle... ", end="")
      while self.wlan.status() == NETWORK_STAT_IDLE and time.ticks_diff(time.ticks_ms(), start_time) < self.idle_timeout_ms:
        time.sleep_ms(self.interval_ms)
      if self.loger_perfix is not None: print(self.loger_perfix, "done.")

    # Check final status
    final_status = self.wlan.status()

    if final_status == NETWORK_STAT_GOT_IP:
      ip_config: tuple[str, str, str, str] = self.wlan.ifconfig()
      if self.loger_perfix is not None: print(self.loger_perfix, "WLAN connected successfully.")
      if self.loger_perfix is not None: print(self.loger_perfix, f"IP: {(ip_config[0])}, Netmask: {ip_config[1]}, Gateway: {ip_config[2]}, DNS: {ip_config[3]}")
      return True

    if final_status == NETWORK_STAT_IDLE:
      if self.loger_perfix is not None: print(self.loger_perfix, "WLAN connection failed: idle status")
      return False

    if final_status == NETWORK_STAT_WRONG_PASSWORD:
      if self.loger_perfix is not None: print(self.loger_perfix, "WLAN connection failed: wrong password")
      return False
    
    if final_status == NETWORK_STAT_NO_AP_FOUND:
      if self.loger_perfix is not None: print(self.loger_perfix, "WLAN connection failed: no access point found")
      return False
    
    if final_status == NETWORK_STAT_CONNECT_FAIL:
      if self.loger_perfix is not None: print(self.loger_perfix, "WLAN connection failed (general error)")
      return False

    if self.loger_perfix is not None: print(self.loger_perfix, f"WLAN connection failed. Final status code: {final_status}")
    return False


  def disconnect(self) -> None:
    """Disconnects the WLAN interface."""
    if self.wlan.isconnected():
      if self.loger_perfix is not None: print(self.loger_perfix, "WLAN disconnecting... ", end="")
      self.wlan.disconnect()
      # Wait for disconnect
      while self.wlan.isconnected():
        time.sleep_ms(self.interval_ms)
      if self.loger_perfix is not None: print(self.loger_perfix, "done.")
    else:
      if self.loger_perfix is not None: print(self.loger_perfix, "WLAN is not connected.")

if __name__ == "__main__":
  print("[__main__] Testing Button class with Count Filtering Algorithm with thread mode, Press Ctrl+C to stop the program.")

  wlanConnector = WLANConnector(loger_perfix="[WLAN] ")
  try:
    wlanConnector.activate()
    if wlanConnector.connect(WLANConfig(
        ssid="ssid", 
        password="password", 
        hostname="hostname", 
        pm=NETWORK_PM_POWERSAVE
      )):
      print("[__main__] Device successfully connected to the network.")
    else:
      print("[__main__] Device failed to connect to the network.")
    while True:
      time.sleep(1)
  except KeyboardInterrupt:
    print("[__main__] Program interrupted")
  except Exception as e:
    print(f"[__main__] An unexpected error occurred: {e}")
  finally:
    wlanConnector.disconnect()
    wlanConnector.deactivate()
    print("[__main__] WLAN interface is now clean.")
    print("[__main__] Program ended")