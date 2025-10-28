# src/micropython_esp32_lib/Device/Button/RealTimeButton.py
import machine
# import _thread as thread
import asyncio

try:
  from ...System import Time
  from ...System import Sleep
  from ...System import Enum # Not directly used in Button but might be in EventHandler.Event
  from ...System import Logging
  from ...System import Digital
  from ...System import EventHandler
  from . import _digital_signal_filters as DigitalFilters # Import helper functions
except ImportError:
  from micropython_esp32_lib.System import Time
  from micropython_esp32_lib.System import Sleep
  from micropython_esp32_lib.System import Enum
  from micropython_esp32_lib.System import Logging
  from micropython_esp32_lib.System import Digital
  from micropython_esp32_lib.System import EventHandler
  from micropython_esp32_lib.Device.Button import _digital_signal_filters as DigitalFilters

class Button:
  def __init__(self, pin: machine.Pin, pressed_signal: Digital.Signal, released_signal: Digital.Signal, threshold: int, interval_ms: int, log_name: str = "RealTimeButton", log_level: Logging.Level = Logging.LEVEL.INFO) -> None:
    """Button state monitor

    Args:
        pin (machine.Pin): Button pin
        pressed_signal (Digital.Signal): Button pressed signal
        released_signal (Digital.Signal): Button released signal
        threshold (int): stability threshold
        interval_ms (int): sampling interval in milliseconds
    """
    self.pin: machine.Pin = pin
    self.pressed_signal: Digital.Signal = pressed_signal
    self.released_signal: Digital.Signal = released_signal

    self.threshold: int = threshold
    self.interval_ms: int = interval_ms

    self.EventHandlers: list[EventHandler.EventHandler] = []

    self.log_name: str = log_name
    self.log_level: Logging.Level = log_level

    self.logger = Logging.Log(self.log_name, self.log_level)

  def isPressed(self) -> bool:
    """Check if button is pressed"""
    result = self.pin.value() == self.pressed_signal.value
    self.logger.debug(f"isPressed: {result}")
    return result
  def isReleased(self) -> bool:
    """Check if button is released"""
    result = self.pin.value() == self.released_signal.value
    self.logger.debug(f"isReleased: {result}")
    return result
  
  def isStablyPressed_sync(self) -> bool:
    """Check if button is stably pressed"""
    result = DigitalFilters.countFiltering_sync(self.pin, self.pressed_signal, self.threshold, self.interval_ms)
    self.logger.debug(f"isStablyPressed_sync: {result}")
    return result
  def isStablyReleased_sync(self) -> bool:
    """Check if button is stably released"""
    result = DigitalFilters.countFiltering_sync(self.pin, self.released_signal, self.threshold, self.interval_ms)
    self.logger.debug(f"isStablyReleased_sync: {result}")
    return result
  
  async def isStablyPressed_async(self) -> bool:
    """Check if button is stably pressed"""
    result = await DigitalFilters.countFiltering_async(self.pin, self.pressed_signal, self.threshold, self.interval_ms)
    self.logger.debug(f"isStablyPressed_async: {result}")
    return result
  async def isStablyReleased_async(self) -> bool:
    """Check if button is stably released"""
    result = await DigitalFilters.countFiltering_async(self.pin, self.released_signal, self.threshold, self.interval_ms)
    self.logger.debug(f"isStablyReleased_async: {result}")
    return result

  def _isChanged_sync(self, start_signal: Digital.Signal, end_signal: Digital.Signal) -> bool:
    """Detect signal change

    Args:
        start_signal (Digital.Signal): start signal
        end_signal (Digital.Signal): end signal

    Returns:
        bool: button signal changed from start signal to end signal
    """
    # This calls the utility function directly, passing `threshold` and `interval_ms`
    result = DigitalFilters.isChanged_sync(self.pin, start_signal, end_signal, self.threshold, self.interval_ms)
    self.logger.debug(f"_isChanged_sync from {start_signal} to {end_signal}: {result}")
    return result
  async def _isChanged_async(self, start_signal: Digital.Signal, end_signal: Digital.Signal) -> bool:
    """Asynchronous Detect signal change

    Args:
        start_signal (Digital.Signal): start signal
        end_signal (Digital.Signal): end signal

    Returns:
        bool: button signal changed from start signal to end signal
    """
    result = await DigitalFilters.isChanged_async(self.pin, start_signal, end_signal, self.threshold, self.interval_ms)
    self.logger.debug(f"_isChanged_async from {start_signal} to {end_signal}: {result}")
    return result
  def _isChangedStably_sync(self, start_signal: Digital.Signal, end_signal: Digital.Signal) -> bool:
    """Detect signal change with Count Filtering Algorithm

    Args:
        start_signal (Digital.Signal): start signal
        end_signal (Digital.Signal): end signal

    Returns:
        bool: button signal changed from start signal to end signal and is stable at end signal
    """
    result = DigitalFilters.isChangedStably_sync(self.pin, start_signal, end_signal, self.threshold, self.interval_ms)
    self.logger.debug(f"_isChangedStably_sync from {start_signal} to {end_signal}: {result}")
    return result
  async def _isChangedStably_async(self, start_signal: Digital.Signal, end_signal: Digital.Signal) -> bool:
    """Asynchronous Detect signal change with Count Filtering Algorithm

    Args:
        start_signal (Digital.Signal): start signal
        end_signal (Digital.Signal): end signal

    Returns:
        bool: button signal changed from start signal to end signal and is stable at end signal
    """
    result = await DigitalFilters.isChangedStably_async(self.pin, start_signal, end_signal, self.threshold, self.interval_ms)
    self.logger.debug(f"_isChangedStably_async from {start_signal} to {end_signal}: {result}")
    return result

  def isToPressed_sync(self) -> bool:
    """Check if button is to pressed"""
    result = self._isChanged_sync(self.released_signal, self.pressed_signal)
    self.logger.debug(f"isToPressed_sync: {result}")
    return result
  def isToReleased_sync(self) -> bool:
    """Check if button is to released"""
    result = self._isChanged_sync(self.pressed_signal, self.released_signal)
    self.logger.debug(f"isToReleased_sync: {result}")
    return result
  async def isToPressed_async(self) -> bool:
    """Check if button is to pressed"""
    result = await self._isChanged_async(self.released_signal, self.pressed_signal)
    self.logger.debug(f"isToPressed_async: {result}")
    return result
  async def isToReleased_async(self) -> bool:
    """Check if button is to released"""
    result = await self._isChanged_async(self.pressed_signal, self.released_signal)
    self.logger.debug(f"isToReleased_async: {result}")
    return result

  def isToStablyPressed_sync(self) -> bool:
    """Check if button is to stably pressed"""
    result = self._isChangedStably_sync(self.released_signal, self.pressed_signal)
    self.logger.debug(f"isToStablyPressed_sync: {result}")
    return result
  def isToStablyReleased_sync(self) -> bool:
    """Check if button is to stably released"""
    result = self._isChangedStably_sync(self.pressed_signal, self.released_signal)
    self.logger.debug(f"isToStablyReleased_sync: {result}")
    return result
  async def isToStablyPressed_async(self) -> bool:
    """Check if button is to stably pressed"""
    result = await self._isChangedStably_async(self.released_signal, self.pressed_signal)
    self.logger.debug(f"isToStablyPressed_async: {result}")
    return result
  async def isToStablyReleased_async(self) -> bool:
    """Check if button is to stably released"""
    result = await self._isChangedStably_async(self.pressed_signal, self.released_signal)
    self.logger.debug(f"isToStablyReleased_async: {result}")
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
    self.logger.info("Starting all event handlers in sync mode")
    for eh in self.EventHandlers:
      eh.start_sync(self)
  def startEventHandlers_async(self) -> None:
    """Start all event handlers in async mode"""
    self.logger.info("Starting all event handlers in async mode")
    for eh in self.EventHandlers:
      eh.start_async(self)

  def stopEventHandlers(self) -> None:
    """Stop all event handlers in sync mode"""
    self.logger.info("Stopping all event handlers")
    for eh in self.EventHandlers:
      eh.stop()

class OnPressEvent(EventHandler.Event):
  def __init__(self, object: Button, log_name: str = "Button.OnPressEvent", log_level: Logging.Level = Logging.LEVEL.INFO, *args, **kwargs):
    super().__init__(object, *args, **kwargs)
    self.object: Button = object
    self.log_name: str = log_name
    self.log_level: Logging.Level = log_level
  def monitor_sync(self) -> bool:
    result = self.object.isToStablyPressed_sync()
    Logging.Log(f"{self.log_name}.monitor_sync {self.object.log_name}", self.log_level).debug(f"OnPressEvent.monitor_sync: {result}")
    return result
  async def monitor_async(self) -> bool:
    result = await self.object.isToStablyPressed_async()
    Logging.Log(f"{self.log_name}.monitor_async {self.object.log_name}", self.log_level).debug(f"OnPressEvent.monitor_async: {result}")
    return result

class OnReleaseEvent(EventHandler.Event):
  def __init__(self, object: Button, log_name: str = "Button.OnReleaseEvent", log_level: Logging.Level = Logging.LEVEL.INFO, *args, **kwargs):
    super().__init__(object, *args, **kwargs)
    self.object: Button = object
    self.log_name: str = log_name
    self.log_level: Logging.Level = log_level
  def monitor_sync(self) -> bool:
    result = self.object.isToStablyReleased_sync()
    Logging.Log(f"{self.log_name}.monitor_sync {self.object.log_name}", self.log_level).debug(f"OnReleaseEvent.monitor_sync: {result}")
    return result
  async def monitor_async(self) -> bool:
    result = await self.object.isToStablyReleased_async()
    Logging.Log(f"{self.log_name}.monitor_async {self.object.log_name}", self.log_level).debug(f"OnReleaseEvent.monitor_async: {result}")
    return result

class OnLongPressEvent(EventHandler.Event):
  def __init__(self, object: Button, timeout_ms: int, log_name: str = "Button.OnLongPressEvent", log_level: Logging.Level = Logging.LEVEL.INFO, *args, **kwargs):
    super().__init__(object, *args, **kwargs)
    self.object: Button = object
    if timeout_ms < 1:
      Logging.Log(f"{self.log_name}.__init__ {self.object.log_name}", log_level).warning(f"Invalid timeout_ms: {timeout_ms}")
    self.timeout_ms: int = timeout_ms
    self.log_name: str = log_name
    self.log_level: Logging.Level = log_level
  def monitor_sync(self) -> bool:
    if self.timeout_ms <= 0:
      Logging.Log(f"{self.log_name}.monitor_sync {self.object.log_name}", self.log_level).warning(f"Invalid timeout_ms: {self.timeout_ms}")
      return False
    if self.object.isToStablyPressed_sync():
      endTime = Time.current_ms() + self.timeout_ms
      outPressTime: bool = False
      while not outPressTime: 
        if not self.object.isStablyPressed_sync(): 
          Logging.Log(f"{self.log_name}.monitor_sync {self.object.log_name}", self.log_level).debug("OnLongPressEvent.monitor_sync: False")
          return False
        Sleep.sync_ms(self.object.interval_ms)
        outPressTime = Time.current_ms() >= endTime
      Logging.Log(f"{self.log_name}.monitor_sync {self.object.log_name}", self.log_level).debug("OnLongPressEvent.monitor_sync: True")
      return True
    Logging.Log(f"{self.log_name}.monitor_sync {self.object.log_name}", self.log_level).debug("OnLongPressEvent.monitor_sync: False")
    return False
  async def monitor_async(self) -> bool:
    if self.timeout_ms <= 0:
      Logging.Log(f"{self.log_name}.monitor_async {self.object.log_name}", self.log_level).warning(f"Invalid timeout_ms: {self.timeout_ms}")
      return False
    if await self.object.isToStablyPressed_async():
      endTime = Time.current_ms() + self.timeout_ms
      outPressTime: bool = False
      while not outPressTime: 
        if not await self.object.isStablyPressed_async(): 
          Logging.Log(f"{self.log_name}.monitor_async {self.object.log_name}", self.log_level).debug("OnLongPressEvent.monitor_async: False")
          return False
        await Sleep.async_ms(self.object.interval_ms)
        outPressTime = Time.current_ms() >= endTime
      Logging.Log(f"{self.log_name}.monitor_async {self.object.log_name}", self.log_level).debug("OnLongPressEvent.monitor_async: True")
      return True
    Logging.Log(f"{self.log_name}.monitor_async {self.object.log_name}", self.log_level).debug("OnLongPressEvent.monitor_async: False")
    return False

class OnMultiClickEvent(EventHandler.Event):
  def __init__(self, object: Button, times: int, timeout_ms: int, log_name: str = "Button.OnMultiClickEvent", log_level: Logging.Level = Logging.LEVEL.INFO, *args, **kwargs):
    super().__init__(object, *args, **kwargs)
    self.object: Button = object
    if times < 1 or timeout_ms < 1:
      Logging.Log(f"{self.log_name}.__init__ {self.object.log_name}", log_level).warning(f"Invalid times ({times}) or timeout_ms ({timeout_ms})")
    self.times: int = times
    self.timeout_ms: int = timeout_ms
    self.log_name: str = log_name
    self.log_level: Logging.Level = log_level
  def monitor_sync(self) -> bool:
    if self.times <= 0 or self.timeout_ms <= 0:
      Logging.Log(f"{self.log_name}.monitor_sync {self.object.log_name}", self.log_level).warning(f"Invalid times ({self.times}) or timeout_ms ({self.timeout_ms})")
      return False
    if self.object.isToStablyPressed_sync():
      endTime = Time.current_ms() + self.timeout_ms
      while not self.object.isStablyReleased_sync():
        Sleep.sync_ms(self.object.interval_ms)
        if Time.current_ms() >= endTime: 
          Logging.Log(f"{self.log_name}.monitor_sync {self.object.log_name}", self.log_level).debug("OnMultiClickEvent.monitor_sync: False")
          return False
      current_clicks = 1
      while current_clicks < self.times:
        while not self.object.isToStablyPressed_sync(): # Wait for next press
          Sleep.sync_ms(self.object.interval_ms)
          if Time.current_ms() >= endTime: 
            Logging.Log(f"{self.log_name}.monitor_sync {self.object.log_name}", self.log_level).debug("OnMultiClickEvent.monitor_sync: False")
            return False
        while not self.object.isToStablyReleased_sync(): # Wait for release of next press
          Sleep.sync_ms(self.object.interval_ms)
          if Time.current_ms() >= endTime:
            Logging.Log(f"{self.log_name}.monitor_sync {self.object.log_name}", self.log_level).debug("OnMultiClickEvent.monitor_sync: False")
            return False
        current_clicks += 1
        # Add a small delay for stable state before next click check (optional but good for real buttons)
        Sleep.sync_ms(self.object.interval_ms) 
      if current_clicks == self.times: 
        Logging.Log(f"{self.log_name}.monitor_sync {self.object.log_name}", self.log_level).debug("OnMultiClickEvent.monitor_sync: True")
        return True
    Logging.Log(f"{self.log_name}.monitor_sync {self.object.log_name}", self.log_level).debug("OnMultiClickEvent.monitor_sync: False")
    return False
  async def monitor_async(self) -> bool:
    if self.times <= 0 or self.timeout_ms <= 0:
      Logging.Log(f"{self.log_name}.monitor_async {self.object.log_name}", self.log_level).warning(f"Invalid times ({self.times}) or timeout_ms ({self.timeout_ms})")
      return False
    if await self.object.isToStablyPressed_async():
      endTime = Time.current_ms() + self.timeout_ms
      while not await self.object.isToStablyReleased_async():
        await Sleep.async_ms(self.object.interval_ms)
        if Time.current_ms() >= endTime: 
          Logging.Log(f"{self.log_name}.monitor_async {self.object.log_name}", self.log_level).debug("OnMultiClickEvent.monitor_async: False")
          return False
      current_clicks = 1
      while current_clicks < self.times:
        while not await self.object.isToStablyPressed_async(): # Wait for next press
          await Sleep.async_ms(self.object.interval_ms)
          if Time.current_ms() >= endTime: 
            Logging.Log(f"{self.log_name}.monitor_async {self.object.log_name}", self.log_level).debug("OnMultiClickEvent.monitor_async: False")
            return False
        while not await self.object.isToStablyReleased_async(): # Wait for release of next press
          await Sleep.async_ms(self.object.interval_ms)
          if Time.current_ms() >= endTime: 
            Logging.Log(f"{self.log_name}.monitor_async {self.object.log_name}", self.log_level).debug("OnMultiClickEvent.monitor_async: False")
            return False
        current_clicks += 1
        # Add a small delay for stable state before next click check (optional but good for real buttons)
        await Sleep.async_ms(self.object.interval_ms)
      if current_clicks == self.times: 
        Logging.Log(f"{self.log_name}.monitor_async {self.object.log_name}", self.log_level).debug("OnMultiClickEvent.monitor_async: True")
        return True
    Logging.Log(f"{self.log_name}.monitor_async {self.object.log_name}", self.log_level).debug("OnMultiClickEvent.monitor_async: False")
    return False

if __name__ == "__main__":
  # This __main__ block is for testing and assumes a MicroPython environment.
  # It largely mirrors the original's test structure but uses the new imports.
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

  class TestHandler(EventHandler.Handler):
    """A concrete Handler to execute button event logic."""
    def __init__(self, button_name: str, event_type: str, counter: Counter | None = None):
      super().__init__(None) # No object needed for this generic handler
      self.button_name: str = button_name
      self.event_type: str = event_type
      self.counter: Counter = counter if counter is not None else Counter(f"Counter.{event_type}")
      self.logger = Logging.Log(f"TestHandler.{event_type}", Logging.LEVEL.INFO)
    def handle_sync(self) -> None:
      """Synchronous event execution."""
      self.counter.increment()
      self.logger.info(f"[{self.button_name}] {self.event_type} detected {self.counter.get()} times")
    async def handle_async(self) -> None:
      """Asynchronous event execution."""
      self.logger.debug(f"Async handling {self.event_type} for {self.button_name}")
      self.handle_sync()
      await Sleep.async_ms(1) # Small delay to yield control

  PIN_A = 19
  PIN_B = 20
  PIN_C = 21
  THRESHOLD = 10
  INTERVAL_MS = 1
  PRESSED_SIGNAL: Digital.Signal = Digital.SIGNAL.LOW  # Assuming active-low button with PULL_UP
  RELEASED_SIGNAL: Digital.Signal = Digital.SIGNAL.HIGH # Assuming active-low button with PULL_UP
  LONGPRESS_TIMEOUT = 500
  MULTICLICK_TIMES = 2
  MULTICLICK_TIMEOUT = 500

  pin_a = machine.Pin(PIN_A, machine.Pin.IN, machine.Pin.PULL_UP)
  pin_b = machine.Pin(PIN_B, machine.Pin.IN, machine.Pin.PULL_UP)
  pin_c = machine.Pin(PIN_C, machine.Pin.IN, machine.Pin.PULL_UP)

  button_a = Button(pin_a, PRESSED_SIGNAL, RELEASED_SIGNAL, THRESHOLD, INTERVAL_MS, log_name="Button.A")
  button_a.addEventHandler(EventHandler.EventHandler(OnPressEvent(button_a), TestHandler("Button A", "Press", Counter("ButtonA_Press"))))\
          .addEventHandler(EventHandler.EventHandler(OnReleaseEvent(button_a), TestHandler("Button A", "Release", Counter("ButtonA_Release"))))\
          .addEventHandler(EventHandler.EventHandler(OnLongPressEvent(button_a, LONGPRESS_TIMEOUT), TestHandler("Button A", "LongPress", Counter("ButtonA_LongPress"))))\
          .addEventHandler(EventHandler.EventHandler(OnMultiClickEvent(button_a, MULTICLICK_TIMES, MULTICLICK_TIMEOUT), TestHandler("Button A", "DoubleClick", Counter("ButtonA_DoubleClick"))))
  
  button_b = Button(pin_b, PRESSED_SIGNAL, RELEASED_SIGNAL, THRESHOLD, INTERVAL_MS, log_name="Button.B")
  button_b.addEventHandler(EventHandler.EventHandler(OnPressEvent(button_b), TestHandler("Button B", "Press", Counter("ButtonB_Press"))))\
          .addEventHandler(EventHandler.EventHandler(OnReleaseEvent(button_b), TestHandler("Button B", "Release", Counter("ButtonB_Release", -1))))\
          .addEventHandler(EventHandler.EventHandler(OnLongPressEvent(button_b, LONGPRESS_TIMEOUT), TestHandler("Button B", "LongPress", Counter("ButtonB_LongPress"))))\
          .addEventHandler(EventHandler.EventHandler(OnMultiClickEvent(button_b, MULTICLICK_TIMES, MULTICLICK_TIMEOUT), TestHandler("Button B", "DoubleClick", Counter("ButtonB_DoubleClick"))))

  button_c = Button(pin_c, PRESSED_SIGNAL, RELEASED_SIGNAL, THRESHOLD, INTERVAL_MS, log_name="Button.C")
  button_c.addEventHandler(EventHandler.EventHandler(OnPressEvent(button_c), TestHandler("Button C", "Press", Counter("ButtonC_Press"))))\
          .addEventHandler(EventHandler.EventHandler(OnReleaseEvent(button_c), TestHandler("Button C", "Release", Counter("ButtonC_Release", -1))))\
          .addEventHandler(EventHandler.EventHandler(OnLongPressEvent(button_c, LONGPRESS_TIMEOUT), TestHandler("Button C", "LongPress", Counter("ButtonC_LongPress"))))\
          .addEventHandler(EventHandler.EventHandler(OnMultiClickEvent(button_c, MULTICLICK_TIMES, MULTICLICK_TIMEOUT), TestHandler("Button C", "DoubleClick", Counter("ButtonC_DoubleClick"))))
  
  logger = Logging.Log(name="main", level=Logging.LEVEL.DEBUG)
  logger.info("\n\n")

  try:
    logger.info("Testing RealTimeButton class with asynchronous (Asyncio) mode. ")
    logger.info("  (Press: OnPress, Release: OnRelease, Hold > 500ms: LongPress, Double-Click < 500ms: DoubleClick) ")
    logger.info("  (Press Ctrl+C to stop the program.)")

    button_a.startEventHandlers_async()
    button_b.startEventHandlers_async()
    button_c.startEventHandlers_async()

    async def main_async_test():
      while True: await Sleep.async_ms(100)
    asyncio.run(main_async_test())
  except KeyboardInterrupt:
    logger.info("Program interrupted")
  finally:
    button_a.stopEventHandlers()
    button_b.stopEventHandlers()
    button_c.stopEventHandlers()
    logger.info("Asynchronous monitors stopped.")

  logger.info("\n\n")

  try:
    logger.info("Testing RealTimeButton class with synchronous (Thread) mode. ")
    logger.info("  (Press: OnPress, Release: OnRelease, Hold > 500ms: LongPress, Double-Click < 500ms: DoubleClick) ")
    logger.info("  (Press Ctrl+C to stop the program.)")
    logger.info("  (Not recommended, may be limited by the number of threads.)")
    
    button_a.startEventHandlers_sync()
    button_b.startEventHandlers_sync()
    # button_c.startEventHandlers_sync()

    while True: Sleep.sync_ms(100)
  except KeyboardInterrupt:
    logger.info("Program interrupted")
  finally:
    button_a.stopEventHandlers()
    button_b.stopEventHandlers()
    button_c.stopEventHandlers()
    logger.info("Synchronous monitors stopped.")

  logger.info("Program ended.")