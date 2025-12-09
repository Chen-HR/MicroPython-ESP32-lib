import abc
import umqtt.robust # type: ignore

class Packet:
  def __init__(self, topic: str, message: str):
    self.topic = topic
    self.message = message

class SubscribeHandler(abc.ABC):
  @abc.abstractmethod
  def handle(self, packet: Packet):
    pass

class SubscribeRouter(SubscribeHandler):
  def __init__(self):
    # { "topic": handler }
    self.routes: dict[str, SubscribeHandler] = {}
  def add_route(self, topic: str, handler: SubscribeHandler):
    self.routes[topic] = handler
  def handle(self, packet: Packet):
    if packet.topic in self.routes:
      self.routes[packet.topic].handle(packet)

class Client(umqtt.robust.MQTTClient):
  def __init__(self, client_id: bytes, server: str, port: int, user: str, password: str, keepalive: int, handler: SubscribeHandler, ssl=None, ssl_params={}):
    super().__init__(client_id, server, port, user, password, keepalive, ssl, ssl_params)
    self.handler: SubscribeHandler = handler
    self.set_callback(self._callback)
  def _callback(self, topic: str, msg: bytes):
    packet = Packet(topic, msg.decode("utf-8"))
    if hasattr(self.handler, "handle"):
      self.handler.handle(packet) # type: ignore
