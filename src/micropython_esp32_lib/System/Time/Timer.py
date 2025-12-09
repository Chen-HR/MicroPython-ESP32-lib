
import machine # type: ignore
import uasyncio as asyncio # type: ignore

try:
  from ...Utils import Logging
  # from ...Utils import Flag
  # from ...Utils import Utils
  from ...Utils import ListenerHandler
  from . import Sleep
except ImportError:
  from micropython_esp32_lib.Utils import Logging
  # from micropython_esp32_lib.Utils import Flag
  # from micropython_esp32_lib.Utils import Utils
  from micropython_esp32_lib.Utils import ListenerHandler
  from micropython_esp32_lib.System.Time import Sleep



class MachineTimer:
  LIMIT: int = 4
  ALLOCATIONS: dict[int, "MachineTimer"] = {} # Allocation
  class Mode:
    def __init__(self, code: int, name: str):
      self.code: int = code
      self.name: str = name
    def __str__(self) -> str:
      return f"MachineTimer.Mode({self.code}, {self.name})"
    def __eq__(self, other: "MachineTimer.Mode") -> bool: # type: ignore
      return self.code == other.code and self.name == other.name
    @classmethod
    def query(cls, code: int) -> "MachineTimer.Mode":
      for mode in cls.__dict__.values():
        if isinstance(mode, cls):
          if mode.code == code:
            return mode
      raise ValueError(f"Unknown mode code: {code}")
    ONE_SHOT : "MachineTimer.Mode"
    PERIODIC : "MachineTimer.Mode"
  try: Mode.ONE_SHOT = Mode(machine.Timer.ONE_SHOT, "ONE_SHOT")
  except AttributeError: pass
  try: Mode.PERIODIC = Mode(machine.Timer.PERIODIC, "PERIODIC")
  except AttributeError: pass
  @classmethod
  def allocateID(cls) -> int:
    for _id in range(cls.LIMIT):
      if _id not in cls.ALLOCATIONS:
        return _id
    raise ValueError("No available timer ID.")
  @classmethod
  def allocate(cls, id: int, machineTimer: "MachineTimer") -> "MachineTimer":
    if id not in cls.ALLOCATIONS:
      cls.ALLOCATIONS[id] = machineTimer
    return cls.ALLOCATIONS[id]
  @classmethod
  def release(cls, id: int) -> None:
    if id in cls.ALLOCATIONS:
      del cls.ALLOCATIONS[id]
  @classmethod
  def get(cls, id: int) -> "MachineTimer":
    if id in cls.ALLOCATIONS:
      return cls.ALLOCATIONS[id]
    else:
      raise ValueError(f"Timer {id} does not exist.")

  def __init__(self, id: int | None = None):
    if id is None: 
      id = MachineTimer.allocateID()
    try:
      self._timer_obj = machine.Timer(id)
      self._timer_id = id
      MachineTimer.allocate(id, self)
      return
    except Exception as e:
      raise e
  def init(self, period_ms: int, callback, mode: Mode = Mode.PERIODIC) -> None:
    if self._timer_obj is None:
      raise ValueError("Timer is not initialized.")
    try:
      self._timer_obj.init(mode=mode.code, period=period_ms, callback=callback)
    except Exception as e:
      raise e
  def deinit(self) -> None:
    if self._timer_obj is None:
      raise ValueError("Timer is not initialized.")
    try:
      self._timer_obj.deinit()
      self._timer_obj = None
      MachineTimer.release(self._timer_id)
    except Exception as e:
      raise e
  def __del__(self):
    self.deinit()


if __name__ == "__main__":
  def MachineTimer_callback(timer):
    Logging.info(f"MachineTimer[{timer}] callback function triggered.")
  timer = MachineTimer()
  timer.init(period_ms=1000, callback=MachineTimer_callback)
  try:
    while True:
      pass
  except KeyboardInterrupt:
    timer.deinit()
    del timer

class AsyncTimer:
  def __init__(self, period_ms: int, async_callback):
    self._period_ms = period_ms
    self._async_callback = async_callback
    self.enable = False
  async def run(self) -> None:
    task = asyncio.get_event_loop().create_task(self._async_callback()) # type: ignore
    # TODO: delete the task after execution without waiting for the task to complete
  async def once(self) -> None:
    await Sleep.async_ms(self._period_ms)
    await self.run()
  async def loop(self) -> None:
    self.enable = True
    while self.enable: 
      await self.once()
  def stop(self) -> None:
    # print("stop")
    self.enable = False
  def delete(self) -> None:
    self.stop()
    self._async_callback = None
  def __del__(self):
    self.delete()

if __name__ == "__main__":
  async def AsyncTimer_callback():
    Logging.info(f"AsyncTimer Callback Function Executed.")
  async def test_AsyncTimer(asyncTimer: AsyncTimer):
    try:
      await asyncTimer.loop()
    except Exception as e:
      raise e
    finally:
      asyncTimer.stop()
  print(f"Test AsyncTimer...")
  asyncTimer = AsyncTimer(period_ms=1000, async_callback=AsyncTimer_callback)
  try:
    asyncio.run(test_AsyncTimer(asyncTimer))
    while True:
      pass
  except KeyboardInterrupt:
    asyncTimer.delete()
    del asyncTimer

class ListenerTimer:
  class Mode:
    def __init__(self, code: int, name: str):
      self.code: int = code
      self.name: str = name
    def __str__(self) -> str:
      return f"ListenerTimer.Mode({self.code}, {self.name})"
    def __eq__(self, other: "ListenerTimer.Mode") -> bool: # type: ignore
      return self.code == other.code and self.name == other.name
    @classmethod
    def query(cls, code: int) -> "ListenerTimer.Mode":
      for mode in cls.__dict__.values():
        if isinstance(mode, cls):
          if mode.code == code:
            return mode
      raise ValueError(f"Unknown mode code: {code}")
    ONE_SHOT : "ListenerTimer.Mode"
    PERIODIC : "ListenerTimer.Mode"
  try: Mode.ONE_SHOT = Mode(machine.Timer.ONE_SHOT, "ONE_SHOT")
  except AttributeError: pass
  try: Mode.PERIODIC = Mode(machine.Timer.PERIODIC, "PERIODIC")
  except AttributeError: pass

  DEFULT_MODE: "ListenerTimer.Mode" = Mode.ONE_SHOT

  class AsyncListener(ListenerHandler.AsyncListener):
    async def listen(self, obj = None, *args, **kwargs) -> bool:
      return True
  class AsyncListenerSyncHandler(ListenerHandler.AsyncListenerSyncHandler):
    def __init__(self, period_ms: int, syncHandler: ListenerHandler.SyncHandler, mode = None, *args, **kwargs):
      self.asyncListener: ListenerTimer.AsyncListener = ListenerTimer.AsyncListener()
      self.syncHandler: ListenerHandler.SyncHandler = syncHandler
      self.period_ms: int = period_ms
      self.mode: "ListenerTimer.Mode" = mode if mode is not None else ListenerTimer.DEFULT_MODE
      self.active = True
      self.task: asyncio.Task | None = None
    async def listen(self):
      if self.active:
        await Sleep.async_ms(self.period_ms)
        if await self.asyncListener.listen():
          self.syncHandler.handle()
        if self.mode == ListenerTimer.Mode.ONE_SHOT:
          self.active = False
    def setMode(self, mode: "ListenerTimer.Mode"):
      self.mode = mode
    def deactivate(self):
      if self.task is not None:
        self.task.cancel()
        self.task = None
        self.active = False
    async def activate(self):
      if self.task is not None:
        self.deactivate()
      self.active = True
      self.task = asyncio.get_event_loop().create_task(self.listen())
  class AsyncListenerAsyncHandler(ListenerHandler.AsyncListenerAsyncHandler):
    def __init__(self, period_ms: int, asyncHandler: ListenerHandler.AsyncHandler, mode = None, *args, **kwargs):
      self.asyncListener: ListenerTimer.AsyncListener = ListenerTimer.AsyncListener()
      self.asyncHandler: ListenerHandler.AsyncHandler = asyncHandler
      self.period_ms: int = period_ms
      self.mode: "ListenerTimer.Mode" = mode if mode is not None else ListenerTimer.DEFULT_MODE
      self.active = True
    async def listen(self):
      if self.active:
        await Sleep.async_ms(self.period_ms)
        if await self.asyncListener.listen():
          asyncio.create_task(self.asyncHandler.handle())
        if self.mode == ListenerTimer.Mode.ONE_SHOT:
          self.active = False
    def setMode(self, mode: "ListenerTimer.Mode"):
      self.mode = mode
    def deactivate(self):
      if self.task is not None:
        self.task.cancel()
        self.task = None
        self.active = False
    async def activate(self):
      if self.task is not None:
        self.deactivate()
      self.active = True
      self.task = asyncio.get_event_loop().create_task(self.listen())

if __name__ == "__main__":
  class SyncHandler(ListenerHandler.SyncHandler):
    def handle(self):
      Logging.info("SyncHandler Executed.")
  class AsyncHandler(ListenerHandler.AsyncHandler):
    async def handle(self):
      Logging.info("AsyncHandler Executed.")
  async def test_ListenerTimer(listenerTimerSyncHandler: ListenerTimer.AsyncListenerSyncHandler, listenerTimerAsyncHandler: ListenerTimer.AsyncListenerAsyncHandler):
    await listenerTimerSyncHandler.activate()
    await listenerTimerAsyncHandler.activate()
    await Sleep.async_ms(3000)
  listenerTimerSyncHandler = ListenerTimer.AsyncListenerSyncHandler(1000, SyncHandler())
  listenerTimerAsyncHandler = ListenerTimer.AsyncListenerAsyncHandler(1000, AsyncHandler())
  try:
    asyncio.run(test_ListenerTimer(listenerTimerSyncHandler, listenerTimerAsyncHandler))
    while True:
      pass
  except KeyboardInterrupt:
    pass
  finally:
    listenerTimerSyncHandler.deactivate()
    listenerTimerAsyncHandler.deactivate()