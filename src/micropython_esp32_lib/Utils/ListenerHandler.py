"""
# file: ./Utils/ListenerHandler.py
"""

import abc
import _thread as thread
import asyncio

try: 
  from . import Logging
  from ..System import Sleep
except ImportError:
  from micropython_esp32_lib.Utils import Logging
  from micropython_esp32_lib.System import Sleep

class BaseHandler(abc.ABC):
  def __init__(self, *args, **kwargs):
    """Initializes the Handler with the given object, arguments, and keyword arguments.
    
    Parameters:
      *args: The positional arguments to pass to the Handler.
      **kwargs: The keyword arguments to pass to the Handler.
    """
    self.args = args
    self.kwargs = kwargs
class SyncHandler(BaseHandler):
  @abc.abstractmethod
  def handle(self) -> None: # TODO: support raise exception
    pass
class AsyncHandler(BaseHandler):
  @abc.abstractmethod
  async def handle(self) -> None: # TODO: support raise exception
    pass


class BaseListener(abc.ABC):
  def __init__(self, *args, **kwargs):
    """
    Initialize an Listener object with the given object and optional arguments and keyword arguments.

    Parameters:
      *args (tuple): Optional arguments to pass to the object's method.
      **kwargs (dict): Optional keyword arguments to pass to the object's method.
    """
    self.args = args
    self.kwargs = kwargs
class SyncListener(BaseListener):
  @abc.abstractmethod
  def listen(self) -> bool: # TODO: support raise exception
    pass
class AsyncListener(BaseListener):
  @abc.abstractmethod
  async def listen(self) -> bool: # TODO: support raise exception
    pass

class ListenerHandler(abc.ABC):
  """Listener Handler Class"""
  def __init__(self, period_ms: int = 100, log_name: str = "ListenerHandler", log_level: Logging.Level = Logging.LEVEL.INFO, *args, **kwargs):
    """
    Constructs a new ListenerHandler object.

    Args:
      period_ms (int, optional): The period in milliseconds to check for events. Defaults to 100 ms.
      log_name (str, optional): The log name for this ListenerHandler instance. Defaults to "ListenerHandler".
      log_level (Logging.Level, optional): The log level for this ListenerHandler instance. Defaults to Logging.LEVEL.INFO.
      *args: Additional arguments to pass to the Handler object.
      **kwargs: Additional keyword arguments to pass to the Handler object.
    """
    # self.listener: Listener = listener
    # self.handler: Handler = handler
    self.period_ms: int = period_ms
    self.logger = Logging.Log(log_name, log_level)
    self.args = args
    self.kwargs = kwargs
    self.active = False
  @abc.abstractmethod
  async def listen(self) -> None: # TODO: support raise exception
    pass
  async def activate(self) -> None: # TODO: support raise exception
    """"""
    self.active = True
    asyncio.create_task(self.listen())
  def deactivate(self) -> None:
    self.active = False
  def __del__(self) -> None:
    self.deactivate()
class SyncListenerHandler(ListenerHandler):
  def __init__(self, listener: SyncListener, period_ms: int = 100, log_name: str = "SyncListenerHandler", log_level: Logging.Level = Logging.LEVEL.INFO, *args, **kwargs):
    """
    Constructs a new ListenerHandler object.

    Args:
      listener (SyncListener): The Listener object to listen.
      handler (BaseHandler): The Handler object to execute upon event occurrence.
      period_ms (int, optional): The period in milliseconds to check for events. Defaults to 100 ms.
      log_name (str, optional): The log name for this ListenerHandler instance. Defaults to "SyncListenerHandler".
      log_level (Logging.Level, optional): The log level for this ListenerHandler instance. Defaults to Logging.LEVEL.INFO.
      *args: Additional arguments to pass to the Handler object.
      **kwargs: Additional keyword arguments to pass to the Handler object.
    """
    super().__init__(period_ms, log_name, log_level, *args, **kwargs)
    self.listener: SyncListener = listener
class AsyncListenerHandler(ListenerHandler):
  def __init__(self, listener: AsyncListener, period_ms: int = 100, log_name: str = "AsyncListenerHandler", log_level: Logging.Level = Logging.LEVEL.INFO, *args, **kwargs):
    """
    Constructs a new ListenerHandler object.

    Args:
      listener (AsyncListener): The Listener object to listen.
      handler (BaseHandler): The Handler object to execute upon event occurrence.
      period_ms (int, optional): The period in milliseconds to check for events. Defaults to 100 ms.
      log_name (str, optional): The log name for this ListenerHandler instance. Defaults to "AsyncListenerHandler".
      log_level (Logging.Level, optional): The log level for this ListenerHandler instance. Defaults to Logging.LEVEL.INFO.
      *args: Additional arguments to pass to the Handler object.
      **kwargs: Additional keyword arguments to pass to the Handler object.
    """
    super().__init__(period_ms, log_name, log_level, *args, **kwargs)
    self.listener: AsyncListener = listener
class SyncListenerSyncHandler(SyncListenerHandler):
  """Listener Handler Class"""
  def __init__(self, listener: SyncListener, handler: SyncHandler, period_ms: int = 100, log_name: str = "SyncListenerSyncHandler", log_level: Logging.Level = Logging.LEVEL.INFO, *args, **kwargs):
    """
    Constructs a new ListenerHandler object.

    Args:
      listener (SyncListener): The Listener object to listen.
      handler (SyncHandler): The Handler object to execute upon event occurrence.
      period_ms (int, optional): The period in milliseconds to check for events. Defaults to 100 ms.
      log_name (str, optional): The log name for this ListenerHandler instance. Defaults to "SyncListenerSyncHandler".
      log_level (Logging.Level, optional): The log level for this ListenerHandler instance. Defaults to Logging.LEVEL.INFO.
      *args: Additional arguments to pass to the Handler object.
      **kwargs: Additional keyword arguments to pass to the Handler object.
    """
    super().__init__(listener, period_ms, log_name, log_level, *args, **kwargs)
    self.handler: SyncHandler = handler
  async def listen(self):
    while self.active:
      if self.listener.listen():
        thread.start_new_thread(self.handler.handle, ())
      await Sleep.async_ms(self.period_ms)
class SyncListenerAsyncHandler(SyncListenerHandler):
  """Listener Handler Class"""
  def __init__(self, listener: SyncListener, handler: AsyncHandler, period_ms: int = 100, log_name: str = "SyncListenerAsyncHandler", log_level: Logging.Level = Logging.LEVEL.INFO, *args, **kwargs):
    """
    Constructs a new ListenerHandler object.

    Args:
      listener (SyncListener): The Listener object to listen.
      handler (AsyncHandler): The Handler object to execute upon event occurrence.
      period_ms (int, optional): The period in milliseconds to check for events. Defaults to 100 ms.
      log_name (str, optional): The log name for this ListenerHandler instance. Defaults to "SyncListenerAsyncHandler".
      log_level (Logging.Level, optional): The log level for this ListenerHandler instance. Defaults to Logging.LEVEL.INFO.
      *args: Additional arguments to pass to the Handler object.
      **kwargs: Additional keyword arguments to pass to the Handler object.
    """
    super().__init__(listener, period_ms, log_name, log_level, *args, **kwargs)
    self.handler: AsyncHandler = handler
  async def listen(self):
    while self.active:
      if self.listener.listen():
        asyncio.create_task(self.handler.handle())
      await Sleep.async_ms(self.period_ms)
class AsyncListenerSyncHandler(AsyncListenerHandler):
  """Listener Handler Class"""
  def __init__(self, listener: AsyncListener, handler: SyncHandler, period_ms: int = 100, log_name: str = "AsyncListenerSyncHandler", log_level: Logging.Level = Logging.LEVEL.INFO, *args, **kwargs):
    """
    Constructs a new ListenerHandler object.

    Args:
      listener (AsyncListener): The Listener object to listen.
      handler (SyncHandler): The Handler object to execute upon event occurrence.
      period_ms (int, optional): The period in milliseconds to check for events. Defaults to 100 ms.
      log_name (str, optional): The log name for this ListenerHandler instance. Defaults to "AsyncListenerSyncHandler".
      log_level (Logging.Level, optional): The log level for this ListenerHandler instance. Defaults to Logging.LEVEL.INFO.
      *args: Additional arguments to pass to the Handler object.
      **kwargs: Additional keyword arguments to pass to the Handler object.
    """
    super().__init__(listener, period_ms, log_name, log_level, *args, **kwargs)
    self.handler: SyncHandler = handler
  async def listen(self):
    while self.active:
      if await self.listener.listen():
        self.handler.handle()
      await Sleep.async_ms(self.period_ms)
class AsyncListenerAsyncHandler(AsyncListenerHandler):
  """Listener Handler Class"""
  def __init__(self, listener: AsyncListener, handler: AsyncHandler, period_ms: int = 100, log_name: str = "AsyncListenerAsyncHandler", log_level: Logging.Level = Logging.LEVEL.INFO, *args, **kwargs):
    """
    Constructs a new ListenerHandler object.

    Args:
      listener (AsyncListener): The Listener object to listen.
      handler (AsyncHandler): The Handler object to execute upon event occurrence.
      period_ms (int, optional): The period in milliseconds to check for events. Defaults to 100 ms.
      log_name (str, optional): The log name for this ListenerHandler instance. Defaults to "AsyncListenerAsyncHandler".
      log_level (Logging.Level, optional): The log level for this ListenerHandler instance. Defaults to Logging.LEVEL.INFO.
      *args: Additional arguments to pass to the Handler object.
      **kwargs: Additional keyword arguments to pass to the Handler object.
    """
    super().__init__(listener, period_ms, log_name, log_level, *args, **kwargs)
    self.handler: AsyncHandler = handler
  async def listen(self):
    while self.active:
      if await self.listener.listen():
        asyncio.create_task(self.handler.handle())
      await Sleep.async_ms(self.period_ms)
