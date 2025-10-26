import _thread as thread
import utime as time
import uasyncio as asyncio
from machine import Pin

try: 
  from . import SystemTime
  from . import Wait
except ImportError:
  from HRChen import SystemTime
  from HRChen import Wait

class Button:
  def __init__(self, pin: Pin, pressed_signal: int, released_signal: int, threshold: int, interval_ms: int, onPress = None, onRelease = None, onLongPress = None, onLongPress_timeout_ms: int = 0, onDoubleClick = None, onDoubleClick_timeout_ms: int = 0) -> None:
    """Button state monitor

    Args:
        pin (Pin): Button pin
        pressed_signal (int): Button pressed signal
        released_signal (int): Button released signal
        threshold (int): stability threshold
        interval_ms (int): sampling interval in milliseconds
        onPress (tuple[Callable[[tuple], None], tuple], optional): on press event function and it arguments. Defaults to None.
        onRelease (tuple[Callable[[tuple], None], tuple], optional): on release event function and it arguments. Defaults to None.
    """
    self.pin: Pin = pin
    self.pressed_signal: int = pressed_signal
    self.released_signal: int = released_signal

    self.threshold: int = threshold
    self.interval_ms: int = interval_ms

    self.onPress = onPress
    self.onPress_thread_id: int | None = None
    self.onPress_thread_enabled: bool = False
    self.onPress_task: asyncio.Task | None = None
    self.onPress_task_enabled: bool = False

    self.onRelease = onRelease
    self.onRelease_thread_id: int | None = None
    self.onRelease_thread_enabled: bool = False
    self.onRelease_task: asyncio.Task | None = None
    self.onRelease_task_enabled: bool = False

    self.onLongPress = onLongPress # TODO: upgrade to onPress_holding
    self.onLongPress_timeout_ms: int = onLongPress_timeout_ms
    self.onLongPress_thread_id: int | None = None
    self.onLongPress_thread_enabled: bool = False
    self.onLongPress_task: asyncio.Task | None = None
    self.onLongPress_task_enabled: bool = False

    self.onDoubleClick = onDoubleClick # TODO: upgrade to onClick_times
    self.onDoubleClick_timeout_ms: int = onDoubleClick_timeout_ms
    self.onDoubleClick_thread_id: int | None = None
    self.onDoubleClick_thread_enabled: bool = False
    self.onDoubleClick_task: asyncio.Task | None = None
    self.onDoubleClick_task_enabled: bool = False

  def isPressed(self) -> bool:
    """Check if button is pressed"""
    return self.pin.value() == self.pressed_signal
  def isReleased(self) -> bool:
    """Check if button is released"""
    return self.pin.value() == self.released_signal
  
  def set_onPress(self, on_press) -> None:
    self.onPress = on_press

  def set_onRelease(self, on_release) -> None:
    self.onRelease = on_release

  def set_onLongPress(self, on_long_press, timeout_ms: int) -> None:
    self.onLongPress = on_long_press
    self.onLongPress_timeout_ms: int = timeout_ms

  def set_onDoubleClick(self, on_double_click, timeout_ms: int) -> None:
    self.onDoubleClick = on_double_click
    self.onDoubleClick_timeout_ms: int = timeout_ms

  def _countFiltering(self, target_signal: float) -> bool: # TODO: move to utils
    """Count Filtering Algorithm

    Args:
      target_signal (float): target signal

    Returns:
      bool: button signal is stable at target signal
    """
    if self.pin.value() == target_signal:
      # init counters
      cnt = 0
      uncnt = 0
      while True:
        # check signal and update counters
        if self.pin.value() == target_signal:
          cnt += 1
          uncnt = 0
        else:
          cnt = 0
          uncnt += 1
        # check counters
        if cnt > self.threshold:
          return True
        elif uncnt > self.threshold:
          return False
        time.sleep_ms(self.interval_ms)
    return False

  async def _countFiltering_async(self, target_signal: float) -> bool: # TODO: move to utils
    """Asynchronous Count Filtering Algorithm

    Args:
      target_signal (float): target signal

    Returns:
      bool: button signal is stable at target signal
    """
    if self.pin.value() == target_signal:
      # init counters
      cnt = 0
      uncnt = 0
      while True:
        # check signal and update counters
        if self.pin.value() == target_signal:
          cnt += 1
          uncnt = 0
        else:
          cnt = 0
          uncnt += 1
        # check counters
        if cnt > self.threshold:
          return True
        elif uncnt > self.threshold:
          return False
        await asyncio.sleep_ms(self.interval_ms)
    return False
  
  def _isChanged_sync(self, start_signal: int, end_signal: int) -> bool: # TODO: public this
    """Detect signal change with Count Filtering Algorithm

    Args:
        start_signal (int): start signal
        end_signal (int): end signal

    Returns:
        bool: button signal changed from start signal to end signal and is stable at end signal
    """
    while self.pin.value() == start_signal:
      time.sleep_ms(self.interval_ms)
    return self._countFiltering(end_signal)

  async def _isChanged_async(self, start_signal: int, end_signal: int) -> bool: # TODO: public this
    """Asynchronous Detect signal change with Count Filtering Algorithm

    Args:
        start_signal (int): start signal
        end_signal (int): end signal

    Returns:
        bool: button signal changed from start signal to end signal and is stable at end signal
    """
    while self.pin.value() == start_signal:
      await asyncio.sleep_ms(self.interval_ms)
    return await self._countFiltering_async(end_signal)

  def _onPress_monitor_sync(self) -> None: # TODO: move to EventHandler
    """Button onPress monitor"""
    while self.onPress_thread_enabled:
      if self.onPress is not None and self._isChanged_sync(self.released_signal, self.pressed_signal):
        try:
          self.onPress[0](self.onPress[1])
        except Exception as e:
          print(f"Button onPress exception: {e}")
        while self.isPressed():
          time.sleep_ms(self.interval_ms)
      time.sleep_ms(self.interval_ms)
  async def _onPress_monitor_async(self) -> None: # TODO: move to EventHandler
    """Asynchronous Button onPress monitor"""
    while self.onPress_task_enabled:
      if self.onPress is not None and await self._isChanged_async(self.released_signal, self.pressed_signal):
        try:
          self.onPress[0](self.onPress[1])
        except Exception as e:
          print(f"Button onPress exception: {e}")
        while self.isPressed():
          await asyncio.sleep_ms(self.interval_ms)
      await asyncio.sleep_ms(self.interval_ms)

  def _onRelease_monitor_sync(self) -> None:
    """Button onRelease monitor"""
    while self.onRelease_thread_enabled:
      if self.onRelease is not None and self._isChanged_sync(self.pressed_signal, self.released_signal):
        try:
          self.onRelease[0](self.onRelease[1])
        except Exception as e:
          print(f"Button onRelease exception: {e}")
        while self.isReleased():
          time.sleep_ms(self.interval_ms)
      time.sleep_ms(self.interval_ms)
  async def _onRelease_monitor_async(self) -> None: # TODO: move to EventHandler
    """Asynchronous Button onRelease monitor"""
    while self.onRelease_task_enabled:
      if self.onRelease is not None and await self._isChanged_async(self.pressed_signal, self.released_signal):
        try:
          self.onRelease[0](self.onRelease[1])
        except Exception as e:
          print(f"Button onRelease exception: {e}")
        while self.isReleased():
          await asyncio.sleep_ms(self.interval_ms)
      await asyncio.sleep_ms(self.interval_ms)
  
  def _onLongPress_monitor_sync(self) -> None: # TODO: move to EventHandler
    """Button onLongPress monitor"""
    while self.onLongPress_thread_enabled:
      if self.onLongPress is not None and self.onLongPress_timeout_ms > 0 and self._isChanged_sync(self.released_signal, self.pressed_signal):
        endTime_ms = SystemTime.current_ms() + self.onLongPress_timeout_ms
        timeOut: bool = False
        longPress: bool = True
        # while not released and not timeOut:
        #   time.sleep_ms(self.interval_ms)
        #   released = self._isChanged_sync(self.pressed_signal, self.released_signal)
        #   timeOut = SystemTime.current_ms() >= endTime_ms
        while longPress and not timeOut: 
          if self.isReleased():
            longPress = False
            print(f"longPress (L262): {longPress}")
          timeOut = SystemTime.current_ms() >= endTime_ms
        if longPress and timeOut:
          try:
            self.onLongPress[0](self.onLongPress[1])
          except Exception as e:
            print(f"Button onLongPress exception: {e}")
        while self.isPressed():
          time.sleep_ms(self.interval_ms)
      time.sleep_ms(self.interval_ms)
  async def _onLongPress_monitor_async(self) -> None: # TODO: move to EventHandler
    """Asynchronous Button onLongPress monitor"""
    while self.onLongPress_task_enabled:
      if self.onLongPress is not None and self.onLongPress_timeout_ms > 0 and await self._isChanged_async(self.released_signal, self.pressed_signal):
        endTime_ms = SystemTime.current_ms() + self.onLongPress_timeout_ms
        timeOut: bool = False
        longPress: bool = True
        # while not released and not timeOut:
        #   await asyncio.sleep_ms(self.interval_ms)
        #   released = await self._isChanged_async(self.pressed_signal, self.released_signal)
        #   timeOut = SystemTime.current_ms() >= endTime_ms
        while longPress and not timeOut: 
          if self.isReleased():
            longPress = False
            print(f"longPress (L262): {longPress}")
          timeOut = SystemTime.current_ms() >= endTime_ms
        if longPress and timeOut:
          try:
            self.onLongPress[0](self.onLongPress[1])
          except Exception as e:
            print(f"Button onLongPress exception: {e}")
        while self.isPressed():
          time.sleep_ms(self.interval_ms)
      await asyncio.sleep_ms(self.interval_ms)

  def _onDoubleClick_monitor_sync(self) -> None: # TODO: move to EventHandler
    """Button onDoubleClick monitor"""
    while self.onDoubleClick_thread_enabled:
      if self.onDoubleClick is not None and self.onDoubleClick_timeout_ms > 0 and self._isChanged_sync(self.released_signal, self.pressed_signal):
        endTime_ms = SystemTime.current_ms() + self.onDoubleClick_timeout_ms
        timeOut: bool = False
        releasedTimes: int = 0
        # while releasedTimes < 2 and not timeOut:
        #   time.sleep_ms(self.interval_ms)
        #   timeOut = SystemTime.current_ms() >= endTime_ms
        #   releasedTimes += 1 if self._isChanged_sync(self.pressed_signal, self.released_signal) else 0
        #   print(f"releasedTimes: {releasedTimes}")
        while not timeOut: 
          if self._isChanged_sync(self.pressed_signal, self.released_signal):
            releasedTimes += 1 
            # print(f"releasedTimes (L262): {releasedTimes}")
            break
        timeOut = SystemTime.current_ms() >= endTime_ms
        while not timeOut:
          if self._isChanged_sync(self.released_signal, self.pressed_signal):
            break
        timeOut = SystemTime.current_ms() >= endTime_ms
        while not timeOut: 
          if self._isChanged_sync(self.pressed_signal, self.released_signal):
            releasedTimes += 1 
            # print(f"releasedTimes (L272): {releasedTimes}")
            break
        timeOut = SystemTime.current_ms() >= endTime_ms
        if releasedTimes >= 2 and not timeOut:
          try:
            self.onDoubleClick[0](self.onDoubleClick[1])
          except Exception as e:
            print(f"Button onDoubleClick exception: {e}")
      time.sleep_ms(self.interval_ms)
  async def _onDoubleClick_monitor_async(self) -> None: # TODO: move to EventHandler
    """Button onDoubleClick monitor"""
    while self.onDoubleClick_task_enabled:
      if self.onDoubleClick is not None and self.onDoubleClick_timeout_ms > 0 and await self._isChanged_async(self.released_signal, self.pressed_signal):
        endTime_ms = SystemTime.current_ms() + self.onDoubleClick_timeout_ms
        timeOut: bool = False
        releasedTimes: int = 0
        # while releasedTimes < 2 and not timeOut:
        #   await asyncio.sleep_ms(self.interval_ms)
        #   timeOut = SystemTime.current_ms() >= endTime_ms
        #   releasedTimes += 1 if await self._isChanged_async(self.pressed_signal, self.released_signal) else 0
        #   print(f"releasedTimes: {releasedTimes}")
        while not timeOut: 
          if await self._isChanged_async(self.pressed_signal, self.released_signal):
            releasedTimes += 1 
            # print(f"releasedTimes (L262): {releasedTimes}")
            break
        timeOut = SystemTime.current_ms() >= endTime_ms
        while not timeOut:
          if await self._isChanged_async(self.released_signal, self.pressed_signal):
            break
        timeOut = SystemTime.current_ms() >= endTime_ms
        while not timeOut: 
          if await self._isChanged_async(self.pressed_signal, self.released_signal):
            releasedTimes += 1 
            # print(f"releasedTimes (L272): {releasedTimes}")
            break
        timeOut = SystemTime.current_ms() >= endTime_ms
        if releasedTimes >= 2 and not timeOut:
          try:
            self.onDoubleClick[0](self.onDoubleClick[1])
          except Exception as e:
            print(f"Button onDoubleClick exception: {e}")
      await asyncio.sleep_ms(self.interval_ms)

  def startMonitor_sync(self) -> None: # TODO: move to EventHandler
    """Start button monitor in thread"""
    if self.onPress_thread_id is None and self.onPress is not None:
      self.onPress_thread_enabled = True
      self.onPress_thread_id = thread.start_new_thread(self._onPress_monitor_sync, ())
    if self.onRelease_thread_id is None and self.onRelease is not None:
      self.onRelease_thread_enabled = True
      self.onRelease_thread_id = thread.start_new_thread(self._onRelease_monitor_sync, ())
    if self.onLongPress_thread_id is None and self.onLongPress is not None:
      self.onLongPress_thread_enabled = True
      self.onLongPress_thread_id = thread.start_new_thread(self._onLongPress_monitor_sync, ())
    if self.onDoubleClick_thread_id is None and self.onDoubleClick is not None:
      self.onDoubleClick_thread_enabled = True
      self.onDoubleClick_thread_id = thread.start_new_thread(self._onDoubleClick_monitor_sync, ())
  def startMonitor_async(self) -> None: # TODO: move to EventHandler
    """Start button monitor in asyncio task"""
    if self.onPress_task is None and self.onPress is not None:
      self.onPress_task_enabled = True
      self.onPress_task = asyncio.create_task(self._onPress_monitor_async())
    if self.onRelease_task is None and self.onRelease is not None:
      self.onRelease_task_enabled = True
      self.onRelease_task = asyncio.create_task(self._onRelease_monitor_async())
    if self.onLongPress_task is None and self.onLongPress is not None:
      self.onLongPress_task_enabled = True
      self.onLongPress_task = asyncio.create_task(self._onLongPress_monitor_async())
    if self.onDoubleClick_task is None and self.onDoubleClick is not None:
      self.onDoubleClick_task_enabled = True
      self.onDoubleClick_task = asyncio.create_task(self._onDoubleClick_monitor_async())

  def stopMonitor_sync(self) -> None: # TODO: move to EventHandler
    """Stop button monitor in thread"""
    if self.onPress_thread_id is not None:
      self.onPress_thread_enabled = False
      self.onPress_thread_id = None
    if self.onRelease_thread_id is not None:
      self.onRelease_thread_enabled = False
      self.onRelease_thread_id = None
    if self.onLongPress_thread_id is not None:
      self.onLongPress_thread_enabled = False
      self.onLongPress_thread_id = None
    if self.onDoubleClick_thread_id is not None:
      self.onDoubleClick_thread_enabled = False
      self.onDoubleClick_thread_id = None
  def stopMonitor_async(self) -> None: # TODO: move to EventHandler
    """Stop button monitor in asyncio task"""
    if self.onPress_task is not None:
      self.onRelease_task_enabled = False
      self.onPress_task = None
    if self.onRelease_task is not None:
      self.onRelease_task_enabled = False
      self.onRelease_task = None
    if self.onLongPress_task is not None:
      self.onLongPress_task_enabled = False
      self.onLongPress_task = None
    if self.onDoubleClick_task is not None:
      self.onDoubleClick_task_enabled = False
      self.onDoubleClick_task = None

if __name__ == "__main__":
  class Counter:
    def __init__(self) -> None:
      self.cnt: int = 0
    def increment(self) -> None:
      self.cnt = (self.cnt + 1) % 100
    def get(self) -> int:
      return self.cnt
  # def onPress(name: str, cnt: Counter) -> None:
  def onPress(arg: tuple) -> None:
    try:
      name: str = arg[0]
      cnt: Counter = arg[1]
    except Exception as e:
      print(f"onPress argument error: {e}")
      return
    cnt.increment()
    print(f"{name} press {cnt.get()} times")
  def onRelease(arg: tuple) -> None:
    try:
      name: str = arg[0]
      cnt: Counter = arg[1]
    except Exception as e:
      print(f"onRelease argument error: {e}")
      return
    print(f"{name} released {cnt.get()} times") 
  def onLongPress(arg: tuple) -> None:
    try:
      name: str = arg[0]
    except Exception as e:
      print(f"onLongPress argument error: {e}")
      return
    print(f"{name} LongPress detected!")

  def onDoubleClick(arg: tuple) -> None:
    try:
      name: str = arg[0]
    except Exception as e:
      print(f"onDoubleClick argument error: {e}")
      return
    print(f"{name} DoubleClick detected!")

  button0_cnt = Counter()
  button0 = Button(Pin(19, Pin.IN, Pin.PULL_UP), 
                   0, 1, 
                   10, 1, 
                   (onPress, ("button 0", button0_cnt)), 
                   (onRelease, ("button 0", button0_cnt)),
                   (onLongPress, ("button 0", 0)), 500, 
                   (onDoubleClick, ("button 0", 0)), 500)
  
  
  button1_cnt = Counter()
  button1 = Button(Pin(20, Pin.IN, Pin.PULL_UP), 
                   0, 1, 
                   10, 1, 
                   (onPress, ("button 1", button1_cnt)), 
                   (onRelease, ("button 1", button1_cnt)), 
                   (onLongPress, ("button 1", 0)), 500, 
                   (onDoubleClick, ("button 1", 0)), 500)
  
  button2_cnt = Counter()
  button2 = Button(Pin(21, Pin.IN, Pin.PULL_UP), 
                   0, 1, 
                   10, 1, 
                   (onPress, ("button 2", button2_cnt)), 
                   (onRelease, ("button 2", button2_cnt)), 
                   (onLongPress, ("button 2", 0)), 500, 
                   (onDoubleClick, ("button 2", 0)), 500)

  try:
    print("Testing Button class with Count Filtering Algorithm with thread mode, Press Ctrl+C to stop the program.")
    button0.startMonitor_sync()
    button1.startMonitor_sync()
    button2.startMonitor_sync()
    while True:
      pass
  except KeyboardInterrupt:
    print("Program interrupted")
  finally:
    button0.stopMonitor_sync()
    button1.stopMonitor_sync()
    button2.stopMonitor_sync()

  try:
    print("Testing Button class with Count Filtering Algorithm with async mode, Press Ctrl+C to stop the program.")
    button0.startMonitor_async()
    button1.startMonitor_async()
    button2.startMonitor_async()
    asyncio.get_event_loop().run_forever()
  except KeyboardInterrupt:
    print("Program interrupted")
  finally:
    button0.stopMonitor_async()
    button1.stopMonitor_async()
    button2.stopMonitor_async()
    print("Program ended")
