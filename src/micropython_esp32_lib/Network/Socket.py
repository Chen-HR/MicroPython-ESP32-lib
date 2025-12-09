"""
# file: ./System/Socket.py

- https://docs.python.org/3.8/library/asyncio-stream.html#asyncio.start_server
"""
import abc
import usocket # type: ignore
import uasyncio # type: ignore

try: 
  from ..Utils import Logging
except ImportError:
  from micropython_esp32_lib.Utils import Logging

class AdderssFamily:
  def __init__(self, code: int, name: str):
    self.code: int = code
    self.name: str = name
  def __str__(self) -> str:
    return f"AdderssFamily({self.code}, {self.name})"
  def __eq__(self, other: "AdderssFamily") -> bool: # type: ignore
    return self.code == other.code and self.name == other.name
  @classmethod
  def query(cls, code: int) -> "AdderssFamily":
    for adderssFamily in cls.__dict__.values():
      if isinstance(adderssFamily, cls):
        if adderssFamily.code == code:
          return adderssFamily
    raise ValueError(f"Unknown AdderssFamily code: {code}")
  INET: "AdderssFamily"
  INET6: "AdderssFamily"
try: AdderssFamily.INET = AdderssFamily(usocket.AF_INET, "inet")
except AttributeError: pass
try: AdderssFamily.INET6 = AdderssFamily(usocket.AF_INET6, "inet6")
except AttributeError: pass

class Type: # socket types
  def __init__(self, code: int, name: str):
    self.code: int = code
    self.name: str = name
  def __str__(self) -> str:
    return f"Type({self.code}, {self.name})"
  def __eq__(self, other: "Type") -> bool: # type: ignore
    return self.code == other.code and self.name == other.name
  @classmethod
  def query(cls, code: int) -> "Type":
    for type in cls.__dict__.values():
      if isinstance(type, cls):
        if type.code == code:
          return type
    raise ValueError(f"Unknown Type code: {code}")
  STREAM: "Type"
  DATAGRAM: "Type"
try: Type.STREAM = Type(usocket.SOCK_STREAM, "stream")
except AttributeError: pass
try: Type.DATAGRAM = Type(usocket.SOCK_DGRAM, "datagram")
except AttributeError: pass


class IPProtocol:
  def __init__(self, code: int, name: str):
    self.code: int = code
    self.name: str = name
  def __str__(self) -> str:
    return f"IPProtocol({self.code}, {self.name})"
  def __eq__(self, other: "IPProtocol") -> bool: # type: ignore
    return self.code == other.code and self.name == other.name
  @classmethod
  def query(cls, code: int) -> "IPProtocol":
    for protocol in cls.__dict__.values():
      if isinstance(protocol, cls):
        if protocol.code == code:
          return protocol
    raise ValueError(f"Unknown IPProtocol code: {code}")
  TCP: "IPProtocol"
  UDP: "IPProtocol"
try: IPProtocol.TCP = IPProtocol(usocket.IPPROTO_TCP, "TCP")
except AttributeError: pass
try: IPProtocol.UDP = IPProtocol(usocket.IPPROTO_UDP, "UDP")
except AttributeError: pass

class OptionLevel: # socket option level
  def __init__(self, level: int):
    self.value = level
  def __repr__(self) -> str:
    return f"OptionLevel({self.value})"
  def __eq__(self, other) -> bool:
    if isinstance(other, OptionLevel): return self.value == other.value
    return False
  SOCKET: "OptionLevel"
OptionLevel.SOCKET = OptionLevel(usocket.SOL_SOCKET)


# SO_ACCEPTCONN: Final[int]
# SO_BROADCAST: Final[int]
# SO_DEBUG: Final[int]
# SO_DONTROUTE: Final[int]
# SO_ERROR: Final[int]
# SO_KEEPALIVE: Final[int]
# SO_LINGER: Final[int]
# SO_OOBINLINE: Final[int]
# SO_RCVBUF: Final[int]
# SO_RCVLOWAT: Final[int]
# SO_RCVTIMEO: Final[int]
# SO_REUSEADDR: Final[int]
# SO_SNDBUF: Final[int]
# SO_SNDLOWAT: Final[int]
# SO_SNDTIMEO: Final[int]
# SO_TYPE: Final[int]
class Option:
  def __init__(self, code: int, name: str):
    self.code: int = code
    self.name: str = name
  def __str__(self) -> str:
    return f"Option({self.code}, {self.name})"
  def __eq__(self, other: "Option") -> bool: # type: ignore
    return self.code == other.code and self.name == other.name
  @classmethod
  def query(cls, code: int) -> "Option":
    for option in cls.__dict__.values():
      if isinstance(option, cls):
        if option.code == code:
          return option
    raise ValueError(f"Unknown Option code: {code}")
  ACCEPTCONN: "Option"
  BROADCAST: "Option"
  DEBUG: "Option"
  DONTROUTE: "Option"
  ERROR: "Option"
  KEEPALIVE: "Option"
  LINGER: "Option"
  OOBINLINE: "Option"
  RCVBUF: "Option"
  RCVLOWAT: "Option"
  RCVTIMEO: "Option"
  REUSEADDR: "Option"
  SNDBUF: "Option"
  SNDLOWAT: "Option"
  SNDTIMEO: "Option"
  TYPE: "Option"
try: Option.ACCEPTCONN = Option(usocket.SO_ACCEPTCONN, "ACCEPTCONN")
except AttributeError: pass
try: Option.BROADCAST = Option(usocket.SO_BROADCAST, "BROADCAST")
except AttributeError: pass
try: Option.DEBUG = Option(usocket.SO_DEBUG, "DEBUG")
except AttributeError: pass
try: Option.DONTROUTE = Option(usocket.SO_DONTROUTE, "DONTROUTE")
except AttributeError: pass
try: Option.ERROR = Option(usocket.SO_ERROR, "ERROR")
except AttributeError: pass
try: Option.KEEPALIVE = Option(usocket.SO_KEEPALIVE, "KEEPALIVE")
except AttributeError: pass
try: Option.LINGER = Option(usocket.SO_LINGER, "LINGER")
except AttributeError: pass
try: Option.OOBINLINE = Option(usocket.SO_OOBINLINE, "OOBINLINE")
except AttributeError: pass
try: Option.RCVBUF = Option(usocket.SO_RCVBUF, "RCVBUF")
except AttributeError: pass
try: Option.RCVLOWAT = Option(usocket.SO_RCVLOWAT, "RCVLOWAT")
except AttributeError: pass
try: Option.RCVTIMEO = Option(usocket.SO_RCVTIMEO, "RCVTIMEO")
except AttributeError: pass
try: Option.REUSEADDR = Option(usocket.SO_REUSEADDR, "REUSEADDR")
except AttributeError: pass
try: Option.SNDBUF = Option(usocket.SO_SNDBUF, "SNDBUF")
except AttributeError: pass
try: Option.SNDLOWAT = Option(usocket.SO_SNDLOWAT, "SNDLOWAT")
except AttributeError: pass
try: Option.SNDTIMEO = Option(usocket.SO_SNDTIMEO, "SNDTIMEO")
except AttributeError: pass
try: Option.TYPE = Option(usocket.SO_TYPE, "TYPE")
except AttributeError: pass

class Address:
  def __init__(self, host: str, port: int):
    self.host = host
    self.port = port
  def __str__(self) -> str:
    return f"{self.host}:{self.port}"
  def __repr__(self) -> str:
    return f"SocketAddress('{self.host}', {self.port})"

class Socket(usocket.socket): # TODO: unfinished
  """
  A synchronous socket wrapper that inherits from usocket.socket, providing
  a consistent interface within the library's framework.
  """
  def __init__(self, family: AdderssFamily = AdderssFamily.INET, type: Type = Type.STREAM, proto: IPProtocol = IPProtocol.TCP, fileno: int = -1):
    super().__init__(family.code, type.code, proto.code, fileno)
  
  def accept(self) -> tuple[usocket.socket, Address]:
    """Accept a connection. Returns (conn_socket, address_tuple)."""
    conn_socket, address_tuple = super().accept()
    return conn_socket, Address(address_tuple[0], address_tuple[1])

  def setsockopt_(self, level: OptionLevel = OptionLevel.SOCKET, option: Option = Option.REUSEADDR, value: int = 1) -> None:
    """Set a socket option using the library's Enum wrappers."""
    super().setsockopt(level.value, option.code, value)
