import abc
import _thread as thread
import asyncio

try: 
  from . import Log
  from . import Wait
except ImportError:
  from HRChen import Log
  from HRChen import Wait

class Handler(abc.ABC):
  def __init__(self, object, *args, **kwargs):
    self.object = object
    self.args = args
    self.kwargs = kwargs
  @abc.abstractmethod
  def handle_sync(self) -> None: # TODO: support raise exception
    pass
  @abc.abstractmethod
  async def handle_async(self) -> None: # TODO: support raise exception
    pass
class Event(abc.ABC):
  def __init__(self, object, *args, **kwargs):
    self.object = object
    self.args = args
    self.kwargs = kwargs
  @abc.abstractmethod
  def monitor_sync(self) -> bool: # TODO: support raise exception
    pass
  @abc.abstractmethod
  async def monitor_async(self) -> bool: # TODO: support raise exception
    pass

class EventHandler:
  """Event Handler Class"""
  def __init__(self, event: Event, handler: Handler, log_name: str = "EventHandler", log_level: int = Log.Log.LEVEL_INFO, *args, **kwargs):
    self.event: Event = event
    self.handler: Handler = handler
    self.args = args
    self.kwargs = kwargs
    self.enabled: bool = True
    self.logger = Log.Log(log_name, log_level)
  def monitor_sync(self) -> None:
    """Monitor event and handle it synchronously"""
    self.logger.debug("Starting sync monitor thread in loop...")
    while self.enabled:
      self.logger.debug(f"Waiting for event...")
      if self.event.monitor_sync():
        self.handler.handle_sync()
  async def monitor_async(self) -> None:
    """Monitor event and handle it asynchronously"""
    self.logger.debug("Starting async monitor task in loop...")
    while self.enabled:
      self.logger.debug(f"Waiting for event...")
      if await self.event.monitor_async():
        await self.handler.handle_async()
  def start_sync(self, object) -> None:
    """Start monitoring event and handling it synchronously in a new thread"""
    self.enabled = True
    self.logger.debug("Starting sync monitor thread in monitor_sync...")
    Wait.sync_ms(1)
    thread.start_new_thread(self.monitor_sync, ())
  def start_async(self, object) -> None:
    """Start monitoring event and handling it asynchronously in the event loop"""
    self.enabled = True
    self.logger.debug("Starting async monitor task in monitor_async...")
    Wait.sync_ms(1)
    asyncio.create_task(self.monitor_async())
  def stop(self) -> None:
    """Stop monitoring event and handling it"""
    self.logger.debug("Stopping event handler...")
    self.enabled = False