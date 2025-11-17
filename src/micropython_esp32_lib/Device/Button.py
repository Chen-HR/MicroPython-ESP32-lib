"""
# file: ./Device/Button.py
"""

import machine
import asyncio
import abc

try:
  from ..System import Timer
  from ..System import Sleep
  from ..System import Digital
  from ..Utils import Enum
  from ..Utils import Flag
  from ..Utils import Logging
  from ..Utils import DigitalFilters
  from ..Utils import ListenerHandler
except ImportError:
  from micropython_esp32_lib.System import Timer
  from micropython_esp32_lib.System import Sleep
  from micropython_esp32_lib.System import Digital
  from micropython_esp32_lib.Utils import Enum
  from micropython_esp32_lib.Utils import Flag
  from micropython_esp32_lib.Utils import Logging
  from micropython_esp32_lib.Utils import DigitalFilters
  from micropython_esp32_lib.Utils import ListenerHandler

class State(Enum.Unit):
  pass
class STATE:
  BOUNCING = State("BOUNCING", 0)
  RELEASED = State("RELEASED", 1)
  PRESSED = State("PRESSED", 2)

class BaseButton(abc.ABC):
  def __init__(self, pin: machine.Pin, released_signal: Digital.Signal, interval_ms: int = 16, log_name: str = "Button", log_level: Logging.Level = Logging.LEVEL.INFO):
    self.pin: machine.Pin = pin
    self.released_signal: Digital.Signal = released_signal
    self.pressed_signal: Digital.Signal = Digital.SIGNAL.inverse(released_signal)
    self.interval_ms: int = interval_ms
    self.logger: Logging.Log = Logging.Log(log_name, log_level)
  @abc.abstractmethod
  async def getState(self) -> State:
    pass
  @abc.abstractmethod
  async def isReleased(self) -> bool:
    pass
  @abc.abstractmethod
  async def isPressed(self) -> bool:
    pass
  @abc.abstractmethod
  async def isToReleased(self) -> bool:
    pass
  @abc.abstractmethod
  async def isToPressed(self) -> bool:
    pass


class ImmediateDebounceButton(BaseButton):
  def __init__(self, pin: machine.Pin, released_signal: Digital.Signal, interval_ms: int = 16, log_name: str = "ImmediateDebounceButton", log_level: Logging.Level = Logging.LEVEL.INFO):
    super().__init__(pin, released_signal, interval_ms, log_name, log_level)
  async def getState(self) -> State:
    await Sleep.async_ms(1)
    pinValue: int = self.pin.value()
    if pinValue == self.released_signal: return STATE.RELEASED
    elif pinValue == self.pressed_signal: return STATE.PRESSED
    return STATE.BOUNCING
  async def isReleased(self) -> bool:
    await Sleep.async_ms(1)
    return self.pin.value() == self.released_signal
  async def isPressed(self) -> bool:
    await Sleep.async_ms(1)
    return self.pin.value() == self.pressed_signal
  async def isToReleased(self) -> bool:
    if await self.isPressed():
      await Sleep.async_ms(self.interval_ms)
      if await self.isReleased(): return True
    return False
  async def isToPressed(self) -> bool:
    if await self.isReleased():
      await Sleep.async_ms(self.interval_ms)
      if await self.isPressed(): return True
    return False

class CountFilteringImmediateDebounceButton(ImmediateDebounceButton):
  def __init__(self, pin: machine.Pin, released_signal: Digital.Signal, interval_ms: int = 1, threshold: int = 16, log_name: str = "CountFilteringImmediateDebounceButton", log_level: Logging.Level = Logging.LEVEL.INFO):
    super().__init__(pin, released_signal, interval_ms, log_name, log_level)
    self.threshold: int = threshold
  async def getState(self):
    cnt: int = 0
    for _ in range(self.threshold):
      cnt += self.pin.value()
      await Sleep.async_ms(self.interval_ms)
    if cnt == self.threshold: 
      return STATE.RELEASED if self.released_signal.value == 1 else STATE.PRESSED
    elif cnt == 0: 
      return STATE.PRESSED if self.pressed_signal.value == 0 else STATE.RELEASED
    return STATE.BOUNCING
  async def isReleased(self) -> bool:
    return await DigitalFilters.countFiltering_async(self.pin, self.released_signal, self.threshold, self.interval_ms)
  async def isPressed(self) -> bool:
    return await DigitalFilters.countFiltering_async(self.pin, self.pressed_signal, self.threshold, self.interval_ms)
  async def isToReleased(self) -> bool:
    return await DigitalFilters.isChangedStably_async(self.pin, self.pressed_signal, self.released_signal, self.threshold, self.interval_ms)
  async def isToPressed(self) -> bool:
    return await DigitalFilters.isChangedStably_async(self.pin, self.released_signal, self.pressed_signal, self.threshold, self.interval_ms)

class StateDebounceButton(BaseButton):
  def __init__(self, pin: machine.Pin, released_signal: Digital.Signal, interval_ms: int = 16, log_name: str = "StateDebounceButton", log_level: Logging.Level = Logging.LEVEL.INFO):
    super().__init__(pin, released_signal, interval_ms, log_name, log_level)
    self._last_state: State = STATE.BOUNCING
  async def getState(self):
    # await Sleep.async_ms(1)
    pinValue: int = self.pin.value()
    if pinValue == self.released_signal.value: 
      self._last_state = STATE.RELEASED
    elif pinValue == self.pressed_signal.value: 
      self._last_state = STATE.PRESSED
    else: 
      self._last_state = STATE.BOUNCING
    return self._last_state
  async def isReleased(self) -> bool:
    state = await self.getState()
    return state == STATE.RELEASED
  async def isPressed(self) -> bool:
    state = await self.getState()
    return state == STATE.PRESSED
  async def isToReleased(self) -> bool:
    if self._last_state == STATE.BOUNCING: self._last_state = await self.getState()
    if self._last_state == STATE.PRESSED:
      await Sleep.async_ms(self.interval_ms)
      if await self.isReleased():
        return True
    return False
  async def isToPressed(self) -> bool:
    if self._last_state == STATE.BOUNCING: self._last_state = await self.getState()
    if self._last_state == STATE.RELEASED:
      await Sleep.async_ms(self.interval_ms)
      if await self.isPressed():
        return True
    return False

class InterruptDrivenStateDebounceButton(StateDebounceButton):
  class EdgeHandler(ListenerHandler.AsyncHandler):
    def __init__(self, handler):
      self.handler = handler
    async def handle(self) -> None:
      asyncio.create_task(self.handler())
  def __init__(self, pin: machine.Pin, released_signal: Digital.Signal, 
               interval_ms: int = 32, 
               log_name: str = "InterruptDrivenStateDebounceButton", log_level: Logging.Level = Logging.LEVEL.INFO):
    super().__init__(pin, released_signal, interval_ms, log_name, log_level)
    self._current_state: State = STATE.BOUNCING
    self.pin.irq(trigger=Digital.IRQCode.IRQ_RISING | Digital.IRQCode.IRQ_FALLING, handler=self._irq_handler)
    self._irq_flag: Flag.BooleanFlag = Flag.BooleanFlag()
    self._irq_listenerHandler: ListenerHandler.SyncListenerAsyncHandler = ListenerHandler.SyncListenerAsyncHandler(Flag.BooleanFlagListener(self._irq_flag), InterruptDrivenStateDebounceButton.EdgeHandler(self._irq_agentHandler))
    self._debounce_timer = Timer.AsyncTimer(interval_ms=self.interval_ms, callback=self._debounce_handler, callback_isAsync=True, repeat=False, log_name=f"{log_name}.DebounceTimer", log_level=log_level)
    self._toReleased_flag: Flag.BooleanFlag = Flag.BooleanFlag()
    self._toPressed_flag: Flag.BooleanFlag = Flag.BooleanFlag()
  async def activate(self):
    self.logger.debug("[activate] Initializing InterruptDrivenStateDebounceButton...")
    await self._debounce_timer.activate()
    await self._irq_listenerHandler.activate()
  def _irq_handler(self, pin: machine.Pin):
    self._irq_flag.activate()
  async def _irq_agentHandler(self):
    self.logger.debug("[_irq_agentHandler] IRQ flag detected.")
    self._last_state = self._current_state
    self._current_state = STATE.BOUNCING
    await self._debounce_timer.reactivate()
    self._irq_flag.deactivate()
  async def _debounce_handler(self):
    pinValue: int = self.pin.value()
    self.logger.debug(f"[_debounce_handler] Debounce handler triggered. pinValue={pinValue}, lastState={self._last_state}, currentState={self._current_state}")
    if pinValue == self.released_signal.value: 
      self._current_state = STATE.RELEASED
    elif pinValue == self.pressed_signal.value: 
      self._current_state = STATE.PRESSED
    else: 
      await self._debounce_timer.reactivate()
      self.logger.warning("Pin state is still ambiguous after debounce.")
    
    if self._current_state == STATE.RELEASED and self._last_state != STATE.RELEASED:
      self._toReleased_flag.activate()
      await Sleep.async_ms(self.interval_ms<<1)
      self._toReleased_flag.deactivate()
    elif self._current_state == STATE.PRESSED and self._last_state != STATE.PRESSED:
      self._toPressed_flag.activate()
      await Sleep.async_ms(self.interval_ms<<1)
      self._toPressed_flag.deactivate()
  async def getState(self) -> State:
    await Sleep.async_ms(1)
    return self._current_state
  async def isReleased(self) -> bool:
    await Sleep.async_ms(1)
    return self._current_state == STATE.RELEASED
  async def isPressed(self) -> bool:
    await Sleep.async_ms(1)
    return self._current_state == STATE.PRESSED
  async def isBouncing(self) -> bool:
    await Sleep.async_ms(1)
    return self._current_state == STATE.BOUNCING
  async def isToReleased(self) -> bool:
    if self._toReleased_flag.isActivate():
      self._toReleased_flag.deactivate()
      return True
    return False
  async def isToPressed(self) -> bool:
    if self._toPressed_flag.isActivate():
      self._toPressed_flag.deactivate()
      return True
    return False
  def deactivate(self):
    self._debounce_timer.deactivate()
    self._irq_listenerHandler.deactivate()

class OnPressedListener(ListenerHandler.AsyncListener):
  def __init__(self, button: BaseButton, interval_ms: int = 10, log_name: str = "OnPressedListener", log_level: Logging.Level = Logging.LEVEL.INFO):
    self.button: BaseButton = button
    self.interval_ms: int = interval_ms
    self.logger: Logging.Log = Logging.Log(log_name, log_level)
  async def listen(self) -> bool:
    return await self.button.isToPressed()
class OnReleasedListener(ListenerHandler.AsyncListener):
  def __init__(self, button: BaseButton, interval_ms: int = 10, log_name: str = "OnReleasedListener", log_level: Logging.Level = Logging.LEVEL.INFO):
    self.button: BaseButton = button
    self.interval_ms: int = interval_ms
    self.logger: Logging.Log = Logging.Log(log_name, log_level)
  async def listen(self) -> bool:
    return await self.button.isToReleased()

if __name__ == "__main__":
  class TestSyncHandler(ListenerHandler.SyncHandler):
    def __init__(self, log_name: str, log_level: Logging.Level = Logging.LEVEL.INFO):
      self.logger = Logging.Log(log_name, log_level)
    def handle(self) -> None:
      self.logger.info("TestSyncHandler.handle() executed.")
  class TestAsyncHandler(ListenerHandler.AsyncHandler):
    def __init__(self, log_name: str, log_level: Logging.Level = Logging.LEVEL.INFO):
      self.logger = Logging.Log(log_name, log_level)
    async def handle(self) -> None:
      await Sleep.async_ms(1)
      self.logger.info(f"TestAsyncHandler.handle() executed.")

  logger = Logging.Log("main", Logging.LEVEL.INFO)
  pin_a = machine.Pin(19, machine.Pin.IN, machine.Pin.PULL_UP)
  pin_b = machine.Pin(20, machine.Pin.IN, machine.Pin.PULL_UP)
  pin_c = machine.Pin(21, machine.Pin.IN, machine.Pin.PULL_UP)

  log_level = Logging.LEVEL.INFO
  btn_a = CountFilteringImmediateDebounceButton (pin_a, Digital.SIGNAL.HIGH, log_name="btn_a", log_level=log_level)
  btn_b = StateDebounceButton                   (pin_b, Digital.SIGNAL.HIGH, log_name="btn_b", log_level=log_level)
  btn_c = InterruptDrivenStateDebounceButton    (pin_c, Digital.SIGNAL.HIGH, log_name="btn_c", log_level=log_level)
  try: 
    async def testSyncHandler():
      logger.info("Starting TestSyncHandler...")
      await btn_c.activate()
      await ListenerHandler.AsyncListenerSyncHandler(OnPressedListener (btn_a, log_name="btn_a.OnPressedListener" , log_level=log_level), TestSyncHandler(log_name="btn_a.OnPressedHandler" , log_level=log_level), log_name="btn_a.OnPressedListenerSyncHandler" , log_level=log_level).activate()
      await ListenerHandler.AsyncListenerSyncHandler(OnReleasedListener(btn_a, log_name="btn_a.OnReleasedListener", log_level=log_level), TestSyncHandler(log_name="btn_a.OnReleasedHandler", log_level=log_level), log_name="btn_a.OnReleasedListenerSyncHandler", log_level=log_level).activate()
      await ListenerHandler.AsyncListenerSyncHandler(OnPressedListener (btn_b, log_name="btn_b.OnPressedListener" , log_level=log_level), TestSyncHandler(log_name="btn_b.OnPressedHandler" , log_level=log_level), log_name="btn_b.OnPressedListenerSyncHandler" , log_level=log_level).activate()
      await ListenerHandler.AsyncListenerSyncHandler(OnReleasedListener(btn_b, log_name="btn_b.OnReleasedListener", log_level=log_level), TestSyncHandler(log_name="btn_b.OnReleasedHandler", log_level=log_level), log_name="btn_b.OnReleasedListenerSyncHandler", log_level=log_level).activate()
      await ListenerHandler.AsyncListenerSyncHandler(OnPressedListener (btn_c, log_name="btn_c.OnPressedListener" , log_level=log_level), TestSyncHandler(log_name="btn_c.OnPressedHandler" , log_level=log_level), log_name="btn_c.OnPressedListenerSyncHandler" , log_level=log_level).activate()
      await ListenerHandler.AsyncListenerSyncHandler(OnReleasedListener(btn_c, log_name="btn_c.OnReleasedListener", log_level=log_level), TestSyncHandler(log_name="btn_c.OnReleasedHandler", log_level=log_level), log_name="btn_c.OnReleasedListenerSyncHandler", log_level=log_level).activate()
      while True:
        await Sleep.async_s(1)
    asyncio.run(testSyncHandler())
  except KeyboardInterrupt:
    pass
  del btn_a
  del btn_b
  del btn_c

