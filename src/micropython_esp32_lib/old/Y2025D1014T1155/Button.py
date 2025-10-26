from machine import Pin

try: 
  from . import SystemTime
  from . import Wait
  from . import Digital
  from . import Log
  from . import EventHandler
except ImportError:
  from HRChen import SystemTime
  from HRChen import Wait
  from HRChen import Digital
  from HRChen import Log
  from HRChen import EventHandler

class Button:
  def __init__(self, pin: Pin, pressed_signal: Digital.Signal, released_signal: Digital.Signal, threshold: int, interval_ms: int, log_name: str = "Button.Button", log_level: int = Log.Log.LEVEL_INFO) -> None:
    """Button state monitor

    Args:
        pin (Pin): Button pin
        pressed_signal (Digital.Signal): Button pressed signal
        released_signal (Digital.Signal): Button released signal
        threshold (int): stability threshold
        interval_ms (int): sampling interval in milliseconds
    """
    self.pin: Pin = pin
    self.pressed_signal: Digital.Signal = pressed_signal
    self.released_signal: Digital.Signal = released_signal

    self.threshold: int = threshold
    self.interval_ms: int = interval_ms

    self.EventHandlers: list[EventHandler.EventHandler] = []

    self.log_name: str = log_name
    self.log_level: int = log_level

    self.log = Log.Log(self.log_name, self.log_level)

  def isPressed(self) -> bool:
    """Check if button is pressed"""
    # return self.pin.value() == self.pressed_signal.__int__()
    result = self.pin.value() == self.pressed_signal.__int__()
    self.log.debug(f"isPressed: {result}")
    return result
  def isReleased(self) -> bool:
    """Check if button is released"""
    # return self.pin.value() == self.released_signal.__int__()
    result = self.pin.value() == self.released_signal.__int__()
    self.log.debug(f"isReleased: {result}")
    return result
  
  def isStablyPressed_sync(self) -> bool:
    """Check if button is stably pressed"""
    # return Digital.countFiltering_sync(self.pin, self.pressed_signal, self.threshold, self.interval_ms)
    result = Digital.countFiltering_sync(self.pin, self.pressed_signal, self.threshold, self.interval_ms)
    self.log.debug(f"isStablyPressed_sync: {result}")
    return result
  def isStablyReleased_sync(self) -> bool:
    """Check if button is stably released"""
    # return Digital.countFiltering_sync(self.pin, self.released_signal, self.threshold, self.interval_ms)
    result = Digital.countFiltering_sync(self.pin, self.released_signal, self.threshold, self.interval_ms)
    self.log.debug(f"isStablyReleased_sync: {result}")
    return result
  
  async def isStablyPressed_async(self) -> bool:
    """Check if button is stably pressed"""
    # return await Digital.countFiltering_async(self.pin, self.pressed_signal, self.threshold, self.interval_ms)
    result = await Digital.countFiltering_async(self.pin, self.pressed_signal, self.threshold, self.interval_ms)
    self.log.debug(f"isStablyPressed_async: {result}")
    return result
  async def isStablyReleased_async(self) -> bool:
    """Check if button is stably released"""
    # return await Digital.countFiltering_async(self.pin, self.released_signal, self.threshold, self.interval_ms)
    result = await Digital.countFiltering_async(self.pin, self.released_signal, self.threshold, self.interval_ms)
    self.log.debug(f"isStablyReleased_async: {result}")
    return result

  def _isChanged_sync(self, start_signal: Digital.Signal, end_signal: Digital.Signal) -> bool:
    """Detect signal change

    Args:
        start_signal (Digital.Signal): start signal
        end_signal (Digital.Signal): end signal

    Returns:
        bool: button signal changed from start signal to end signal
    """
    # return Digital.isChanged_sync(self.pin, start_signal, end_signal, self.threshold, self.interval_ms)
    result = Digital.isChanged_sync(self.pin, start_signal, end_signal, self.threshold, self.interval_ms)
    self.log.debug(f"_isChanged_sync from {start_signal} to {end_signal}: {result}")
    return result
  async def _isChanged_async(self, start_signal: Digital.Signal, end_signal: Digital.Signal) -> bool:
    """Asynchronous Detect signal change

    Args:
        start_signal (Digital.Signal): start signal
        end_signal (Digital.Signal): end signal

    Returns:
        bool: button signal changed from start signal to end signal
    """
    # return await Digital.isChanged_async(self.pin, start_signal, end_signal, self.threshold, self.interval_ms)
    result = await Digital.isChanged_async(self.pin, start_signal, end_signal, self.threshold, self.interval_ms)
    self.log.debug(f"_isChanged_async from {start_signal} to {end_signal}: {result}")
    return result
  def _isChangedStably_sync(self, start_signal: Digital.Signal, end_signal: Digital.Signal) -> bool:
    """Detect signal change with Count Filtering Algorithm

    Args:
        start_signal (Digital.Signal): start signal
        end_signal (Digital.Signal): end signal

    Returns:
        bool: button signal changed from start signal to end signal and is stable at end signal
    """
    # return Digital.isChangedStably_sync(self.pin, start_signal, end_signal, self.threshold, self.interval_ms)
    result = Digital.isChangedStably_sync(self.pin, start_signal, end_signal, self.threshold, self.interval_ms)
    self.log.debug(f"_isChangedStably_sync from {start_signal} to {end_signal}: {result}")
    return result
  async def _isChangedStably_async(self, start_signal: Digital.Signal, end_signal: Digital.Signal) -> bool:
    """Asynchronous Detect signal change with Count Filtering Algorithm

    Args:
        start_signal (Digital.Signal): start signal
        end_signal (Digital.Signal): end signal

    Returns:
        bool: button signal changed from start signal to end signal and is stable at end signal
    """
    # return await Digital.isChangedStably_async(self.pin, start_signal, end_signal, self.threshold, self.interval_ms)
    result = await Digital.isChangedStably_async(self.pin, start_signal, end_signal, self.threshold, self.interval_ms)
    self.log.debug(f"_isChangedStably_async from {start_signal} to {end_signal}: {result}")
    return result

  def isToPressed_sync(self) -> bool:
    """Check if button is to pressed"""
    # return self._isChanged_sync(self.released_signal, self.pressed_signal)
    result = self._isChanged_sync(self.released_signal, self.pressed_signal)
    self.log.debug(f"isToPressed_sync: {result}")
    return result
  def isToReleased_sync(self) -> bool:
    """Check if button is to released"""
    # return self._isChanged_sync(self.pressed_signal, self.released_signal)
    result = self._isChanged_sync(self.pressed_signal, self.released_signal)
    self.log.debug(f"isToReleased_sync: {result}")
    return result
  async def isToPressed_async(self) -> bool:
    """Check if button is to pressed"""
    # return await self._isChanged_async(self.released_signal, self.pressed_signal)
    result = await self._isChanged_async(self.released_signal, self.pressed_signal)
    self.log.debug(f"isToPressed_async: {result}")
    return result
  async def isToReleased_async(self) -> bool:
    """Check if button is to released"""
    # return await self._isChanged_async(self.pressed_signal, self.released_signal)
    result = await self._isChanged_async(self.pressed_signal, self.released_signal)
    self.log.debug(f"isToReleased_async: {result}")
    return result

  def isToStablyPressed_sync(self) -> bool:
    """Check if button is to stably pressed"""
    # return self._isChangedStably_sync(self.released_signal, self.pressed_signal)
    result = self._isChangedStably_sync(self.released_signal, self.pressed_signal)
    self.log.debug(f"isToStablyPressed_sync: {result}")
    return result
  def isToStablyReleased_sync(self) -> bool:
    """Check if button is to stably released"""
    # return self._isChangedStably_sync(self.pressed_signal, self.released_signal)
    result = self._isChangedStably_sync(self.pressed_signal, self.released_signal)
    self.log.debug(f"isToStablyReleased_sync: {result}")
    return result
  async def isToStablyPressed_async(self) -> bool:
    """Check if button is to stably pressed"""
    # return await self._isChangedStably_async(self.released_signal, self.pressed_signal)
    result = await self._isChangedStably_async(self.released_signal, self.pressed_signal)
    self.log.debug(f"isToStablyPressed_async: {result}")
    return result
  async def isToStablyReleased_async(self) -> bool:
    """Check if button is to stably released"""
    # return await self._isChangedStably_async(self.pressed_signal, self.released_signal)
    result = await self._isChangedStably_async(self.pressed_signal, self.released_signal)
    self.log.debug(f"isToStablyReleased_async: {result}")
    return result

  def addEventHandler(self, eventHandler: EventHandler.EventHandler):
    """Add event handler

    Args:
        eventHandler (EventHandler.EventHandler): event handler
    """
    if not isinstance(eventHandler, EventHandler.EventHandler):
      raise TypeError("eventHandler must be an instance of EventHandler.EventHandler")
    self.EventHandlers.append(eventHandler)
    return self

  def startEventHandlers_sync(self) -> None:
    """Start all event handlers in sync mode"""
    self.log.info("Starting all event handlers in sync mode")
    for eh in self.EventHandlers:
      eh.start_sync(self)
  def startEventHandlers_async(self) -> None:
    """Start all event handlers in async mode"""
    self.log.info("Starting all event handlers in async mode")
    for eh in self.EventHandlers:
      eh.start_async(self)

  def stopEventHandlers(self) -> None:
    """Stop all event handlers in sync mode"""
    self.log.info("Stopping all event handlers")
    for eh in self.EventHandlers:
      eh.stop()

class OnPressEvent(EventHandler.Event):
  def __init__(self, object: Button, log_name: str = "Button.OnReleaseEvent", log_level: int = Log.Log.LEVEL_INFO, *args, **kwargs):
    super().__init__(object, *args, **kwargs)
    self.object: Button = object
    self.log_name: str = log_name
    self.log_level: int = log_level
  def monitor_sync(self) -> bool:
    # return self.object.isToStablyPressed_sync()
    result = self.object.isToStablyPressed_sync()
    Log.Log(f"{self.log_name}.monitor_sync {self.object.log_name}", self.log_level).debug(f"OnPressEvent.monitor_sync: {result}")
    return result
  async def monitor_async(self) -> bool:
    # return await self.object.isToStablyPressed_async()
    result = await self.object.isToStablyPressed_async()
    Log.Log(f"{self.log_name}.monitor_async {self.object.log_name}", self.log_level).debug(f"OnPressEvent.monitor_async: {result}")
    return result

class OnReleaseEvent(EventHandler.Event):
  def __init__(self, object: Button, log_name: str = "Button.OnReleaseEvent", log_level: int = Log.Log.LEVEL_INFO, *args, **kwargs):
    super().__init__(object, *args, **kwargs)
    self.object: Button = object
    self.log_name: str = log_name
    self.log_level: int = log_level
  def monitor_sync(self) -> bool:
    # return self.object.isToStablyReleased_sync()
    result = self.object.isToStablyReleased_sync()
    Log.Log(f"{self.log_name}.monitor_sync {self.object.log_name}", self.log_level).debug(f"OnReleaseEvent.monitor_sync: {result}")
    return result
  async def monitor_async(self) -> bool:
    # return await self.object.isToStablyReleased_async()
    result = await self.object.isToStablyReleased_async()
    Log.Log(f"{self.log_name}.monitor_async {self.object.log_name}", self.log_level).debug(f"OnReleaseEvent.monitor_async: {result}")
    return result

class OnLongPressEvent(EventHandler.Event):
  def __init__(self, object: Button, timeout_ms: int, log_name: str = "Button.OnLongPressEvent", log_level: int = Log.Log.LEVEL_INFO, *args, **kwargs):
    super().__init__(object, *args, **kwargs)
    self.object: Button = object
    if timeout_ms < 1:
      Log.Log(f"{self.log_name}.__init__ {self.object.log_name}", log_level).warning(f"Invalid timeout_ms: {timeout_ms}")
    self.timeout_ms: int = timeout_ms
    self.log_name: str = log_name
    self.log_level: int = log_level
  def monitor_sync(self) -> bool:
    if self.timeout_ms <= 0:
      Log.Log(f"{self.log_name}.monitor_sync {self.object.log_name}", self.log_level).warning(f"Invalid timeout_ms: {self.timeout_ms}")
      return False
    if self.object.isToStablyPressed_sync():
      endTime = SystemTime.current_ms() + self.timeout_ms
      outPressTime: bool = False
      while not outPressTime: 
        if not self.object.isStablyPressed_sync(): 
          Log.Log(f"{self.log_name}.monitor_sync {self.object.log_name}", self.log_level).debug("OnLongPressEvent.monitor_sync: False")
          return False
        Wait.sync_ms(self.object.interval_ms)
        outPressTime = SystemTime.current_ms() >= endTime
      Log.Log(f"{self.log_name}.monitor_sync {self.object.log_name}", self.log_level).debug("OnLongPressEvent.monitor_sync: True")
      return True
    Log.Log(f"{self.log_name}.monitor_sync {self.object.log_name}", self.log_level).debug("OnLongPressEvent.monitor_sync: False")
    return False
  async def monitor_async(self) -> bool:
    if self.timeout_ms <= 0:
      Log.Log(f"{self.log_name}.monitor_async {self.object.log_name}", self.log_level).warning(f"Invalid timeout_ms: {self.timeout_ms}")
      return False
    if await self.object.isToStablyPressed_async():
      endTime = SystemTime.current_ms() + self.timeout_ms
      outPressTime: bool = False
      while not outPressTime: 
        if not await self.object.isStablyPressed_async(): 
          Log.Log(f"{self.log_name}.monitor_async {self.object.log_name}", self.log_level).debug("OnLongPressEvent.monitor_async: False")
          return False
        await Wait.async_ms(self.object.interval_ms)
        outPressTime = SystemTime.current_ms() >= endTime
      Log.Log(f"{self.log_name}.monitor_async {self.object.log_name}", self.log_level).debug("OnLongPressEvent.monitor_async: True")
      return True
    Log.Log(f"{self.log_name}.monitor_async {self.object.log_name}", self.log_level).debug("OnLongPressEvent.monitor_async: False")
    return False

class OnMultiClickEvent(EventHandler.Event):
  def __init__(self, object: Button, times: int, timeout_ms: int, log_name: str = "Button.OnMultiClickEvent", log_level: int = Log.Log.LEVEL_INFO, *args, **kwargs):
    super().__init__(object, *args, **kwargs)
    self.object: Button = object
    if times < 1 or timeout_ms < 1:
      Log.Log(f"{self.log_name}.__init__ {self.object.log_name}", log_level).warning(f"Invalid times ({times}) or timeout_ms ({timeout_ms})")
    self.times: int = times
    self.timeout_ms: int = timeout_ms
    self.log_name: str = log_name
    self.log_level: int = log_level
  def monitor_sync(self) -> bool:
    if self.times <= 0 or self.timeout_ms <= 0:
      Log.Log(f"{self.log_name}.monitor_sync {self.object.log_name}", self.log_level).warning(f"Invalid times ({self.times}) or timeout_ms ({self.timeout_ms})")
      return False
    if self.object.isToStablyPressed_sync():
      endTime = SystemTime.current_ms() + self.timeout_ms
      while not self.object.isStablyReleased_sync():
        Wait.sync_ms(self.object.interval_ms)
        if SystemTime.current_ms() >= endTime: 
          Log.Log(f"{self.log_name}.monitor_sync {self.object.log_name}", self.log_level).debug("OnMultiClickEvent.monitor_sync: False")
          return False
      current_clicks = 1
      while current_clicks < self.times:
        while not self.object.isStablyPressed_sync():
          Wait.sync_ms(self.object.interval_ms)
          if SystemTime.current_ms() >= endTime: 
            Log.Log(f"{self.log_name}.monitor_sync {self.object.log_name}", self.log_level).debug("OnMultiClickEvent.monitor_sync: False")
            return False
        while not self.object.isStablyReleased_sync():
          Wait.sync_ms(self.object.interval_ms)
          if SystemTime.current_ms() >= endTime:
            Log.Log(f"{self.log_name}.monitor_sync {self.object.log_name}", self.log_level).debug("OnMultiClickEvent.monitor_sync: False")
            return False
        current_clicks += 1
        Wait.sync_ms(self.object.interval_ms)
      if current_clicks == self.times: 
        Log.Log(f"{self.log_name}.monitor_sync {self.object.log_name}", self.log_level).debug("OnMultiClickEvent.monitor_sync: True")
        return True
    Log.Log(f"{self.log_name}.monitor_sync {self.object.log_name}", self.log_level).debug("OnMultiClickEvent.monitor_sync: False")
    return False
  async def monitor_async(self) -> bool:
    if self.times <= 0 or self.timeout_ms <= 0:
      Log.Log(f"{self.log_name}.monitor_async {self.object.log_name}", self.log_level).warning(f"Invalid times ({self.times}) or timeout_ms ({self.timeout_ms})")
      return False
    if await self.object.isToStablyPressed_async():
      endTime = SystemTime.current_ms() + self.timeout_ms
      while not await self.object.isStablyReleased_async():
        await Wait.async_ms(self.object.interval_ms)
        if SystemTime.current_ms() >= endTime: 
          Log.Log(f"{self.log_name}.monitor_async {self.object.log_name}", self.log_level).debug("OnMultiClickEvent.monitor_async: False")
          return False
      current_clicks = 1
      while current_clicks < self.times:
        while not await self.object.isStablyPressed_async():
          await Wait.async_ms(self.object.interval_ms)
          if SystemTime.current_ms() >= endTime: 
            Log.Log(f"{self.log_name}.monitor_async {self.object.log_name}", self.log_level).debug("OnMultiClickEvent.monitor_async: False")
            return False
        while not await self.object.isStablyReleased_async():
          await Wait.async_ms(self.object.interval_ms)
          if SystemTime.current_ms() >= endTime: 
            Log.Log(f"{self.log_name}.monitor_async {self.object.log_name}", self.log_level).debug("OnMultiClickEvent.monitor_async: False")
            return False
        current_clicks += 1
        await Wait.async_ms(self.object.interval_ms)
      if current_clicks == self.times: 
        Log.Log(f"{self.log_name}.monitor_async {self.object.log_name}", self.log_level).debug("OnMultiClickEvent.monitor_async: True")
        return True
    Log.Log(f"{self.log_name}.monitor_async {self.object.log_name}", self.log_level).debug("OnMultiClickEvent.monitor_async: False")
    return False

if __name__ == "__main__":
  class Counter:
    """Simple counter for event tracking."""
    def __init__(self, name: str, start: int = 0) -> None:
      self.name: str = name
      self.cnt: int = start
    def increment(self) -> None:
      self.cnt = (self.cnt + 1) % 100
    def get(self) -> int:
      return self.cnt
    def get_name(self) -> str:
      return self.name

  class MyHandler(EventHandler.Handler):
    """A concrete Handler to execute button event logic."""
    def __init__(self, button_name: str, event_type: str, counter: Counter | None = None):
      super().__init__(None)
      self.button_name: str = button_name
      self.event_type: str = event_type
      self.counter: Counter = counter if counter is not None else Counter(f"Counter.{event_type}")
      self.logger = Log.Log(f"TestHandler.{event_type}", Log.Log.LEVEL_INFO)
    def handle_sync(self) -> None:
      """Synchronous event execution."""
      self.counter.increment()
      self.logger.info(f"[{self.button_name}] {self.event_type} detected {self.counter.get()} times")
    async def handle_async(self) -> None:
      """Asynchronous event execution."""
      self.logger.debug(f"Async handling {self.event_type} for {self.button_name}")
      self.handle_sync()
      await Wait.async_ms(1)

  PIN_A = 19
  PIN_B = 20
  PIN_C = 21
  THRESHOLD = 10
  INTERVAL_MS = 1
  PRESSED = 0
  RELEASED = 1
  LONGPRESS_TIMEOUT = 500
  MULTICLICK_TIMES = 2
  MULTICLICK_TIMEOUT = 500

  button_a = Button(Pin(PIN_A, Pin.IN, Pin.PULL_UP), Digital.Signal(PRESSED), Digital.Signal(RELEASED), THRESHOLD, INTERVAL_MS, log_name="Button.A")
  button_a.addEventHandler(EventHandler.EventHandler(OnPressEvent(button_a), MyHandler("Button A", "Press", Counter("ButtonA_Press"))))\
          .addEventHandler(EventHandler.EventHandler(OnReleaseEvent(button_a), MyHandler("Button A", "Release", Counter("ButtonA_Release"))))\
          .addEventHandler(EventHandler.EventHandler(OnLongPressEvent(button_a, LONGPRESS_TIMEOUT), MyHandler("Button A", "LongPress", Counter("ButtonA_LongPress"))))\
          .addEventHandler(EventHandler.EventHandler(OnMultiClickEvent(button_a, MULTICLICK_TIMES, MULTICLICK_TIMEOUT), MyHandler("Button A", "DoubleClick", Counter("ButtonA_DoubleClick"))))
  
  button_b = Button(Pin(PIN_B, Pin.IN, Pin.PULL_UP), Digital.Signal(PRESSED), Digital.Signal(RELEASED), THRESHOLD, INTERVAL_MS, log_name="Button.B")
  button_b.addEventHandler(EventHandler.EventHandler(OnPressEvent(button_b), MyHandler("Button B", "Press", Counter("ButtonB_Press"))))\
          .addEventHandler(EventHandler.EventHandler(OnReleaseEvent(button_b), MyHandler("Button B", "Release", Counter("ButtonB_Release", -1))))\
          .addEventHandler(EventHandler.EventHandler(OnLongPressEvent(button_b, LONGPRESS_TIMEOUT), MyHandler("Button B", "LongPress", Counter("ButtonB_LongPress"))))\
          .addEventHandler(EventHandler.EventHandler(OnMultiClickEvent(button_b, MULTICLICK_TIMES, MULTICLICK_TIMEOUT), MyHandler("Button B", "DoubleClick", Counter("ButtonB_DoubleClick"))))

  button_c = Button(Pin(PIN_C, Pin.IN, Pin.PULL_UP), Digital.Signal(PRESSED), Digital.Signal(RELEASED), THRESHOLD, INTERVAL_MS, log_name="Button.C")
  button_c.addEventHandler(EventHandler.EventHandler(OnPressEvent(button_c), MyHandler("Button C", "Press", Counter("ButtonC_Press"))))\
          .addEventHandler(EventHandler.EventHandler(OnReleaseEvent(button_c), MyHandler("Button C", "Release", Counter("ButtonC_Release", -1))))\
          .addEventHandler(EventHandler.EventHandler(OnLongPressEvent(button_c, LONGPRESS_TIMEOUT), MyHandler("Button C", "LongPress", Counter("ButtonC_LongPress"))))\
          .addEventHandler(EventHandler.EventHandler(OnMultiClickEvent(button_c, MULTICLICK_TIMES, MULTICLICK_TIMEOUT), MyHandler("Button C", "DoubleClick", Counter("ButtonC_DoubleClick"))))

  try:
    print("\n" + "="*50)
    print("Testing Button class with asynchronous (Asyncio) mode.")
    print(" (Press: OnPress, Release: OnRelease, Hold > 500ms: LongPress, Double-Click < 500ms: DoubleClick)")
    print(" (Press Ctrl+C to stop the program.)")
    print("="*50)

    async def main_async_test():
      button_a.startEventHandlers_async()
      button_b.startEventHandlers_async()
      button_c.startEventHandlers_async()
      
      while True:
        await Wait.async_ms(100)

    Wait.asyncio.run(main_async_test())
  except KeyboardInterrupt:
    print("\nProgram interrupted")
  finally:
    button_a.stopEventHandlers()
    button_b.stopEventHandlers()
    button_c.stopEventHandlers()
    print("Asynchronous monitors stopped.")

  try:
    print("\n" + "="*50)
    print("Testing Button class with synchronous (Thread) mode.")
    print(" (Press: OnPress, Release: OnRelease, Hold > 500ms: LongPress, Double-Click < 500ms: DoubleClick)")
    print(" (Press Ctrl+C to stop the program.)")
    print("="*50)
    
    button_a.startEventHandlers_sync()
    button_b.startEventHandlers_sync()
    button_c.startEventHandlers_sync()
    
    while True:
      Wait.sync_ms(100)
      
  except KeyboardInterrupt:
    print("\nProgram interrupted")
  finally:
    button_a.stopEventHandlers()
    button_b.stopEventHandlers()
    button_c.stopEventHandlers()
    print("Synchronous monitors stopped.")

  print("Program ended.")
