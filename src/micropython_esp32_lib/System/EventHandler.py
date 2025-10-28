import abc
import _thread as thread
import asyncio

try: 
  from . import Logging
  from . import Sleep
except ImportError:
  from micropython_esp32_lib.System import Logging
  from micropython_esp32_lib.System import Sleep

class Handler(abc.ABC):
  def __init__(self, object, *args, **kwargs):
    """Initializes the Handler with the given object, arguments, and keyword arguments.
    
    Parameters:
      object: The object to which the Handler is associated.
      *args: The positional arguments to pass to the Handler.
      **kwargs: The keyword arguments to pass to the Handler.
    """
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
    """
    Initialize an Event object with the given object and optional arguments and keyword arguments.

    Parameters:
      object (object): The object to monitor.
      *args (tuple): Optional arguments to pass to the object's method.
      **kwargs (dict): Optional keyword arguments to pass to the object's method.
    """
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
  def __init__(self, event: Event, handler: Handler, log_name: str = "EventHandler", log_level: Logging.Level = Logging.LEVEL.INFO, *args, **kwargs):
    """
    Constructs a new EventHandler object.

    Args:
      event (Event): The Event object to monitor.
      handler (Handler): The Handler object to execute upon event occurrence.
      log_name (str, optional): The log name for this EventHandler instance. Defaults to "EventHandler".
      log_level (Logging.Level, optional): The log level for this EventHandler instance. Defaults to Logging.LEVEL.INFO.
      *args: Additional arguments to pass to the Handler object.
      **kwargs: Additional keyword arguments to pass to the Handler object.
    """
    self.event: Event = event
    self.handler: Handler = handler
    self.args = args
    self.kwargs = kwargs
    self.enabled: bool = True
    self.logger = Logging.Log(log_name, log_level)
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
    Sleep.sync_ms(1)
    thread.start_new_thread(self.monitor_sync, ())
  def start_async(self, object) -> None:
    """Start monitoring event and handling it asynchronously in the event loop"""
    self.enabled = True
    self.logger.debug("Starting async monitor task in monitor_async...")
    Sleep.sync_ms(1)
    asyncio.create_task(self.monitor_async())
  def stop(self) -> None:
    """Stop monitoring event and handling it"""
    self.logger.debug("Stopping event handler...")
    self.enabled = False