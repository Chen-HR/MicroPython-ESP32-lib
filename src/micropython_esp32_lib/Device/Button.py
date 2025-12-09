"""
# file: ./Device/Button.py
"""

import machine # type: ignore
import asyncio
import abc

try:
  from ..System.Time import Timer
  from ..System.Time import Sleep
  from ..System import Digital
  from ..Utils import Logging
  from ..Utils import Flag
  from ..Utils import ListenerHandler
except ImportError:
  from micropython_esp32_lib.System.Time import Timer
  from micropython_esp32_lib.System.Time import Sleep
  from micropython_esp32_lib.System import Digital
  from micropython_esp32_lib.Utils import Logging
  from micropython_esp32_lib.Utils import Flag
  from micropython_esp32_lib.Utils import ListenerHandler

class State:
  def __init__(self, code: int, name: str):
    self.code: int = code
    self.name: str = name
  def __str__(self) -> str:
    return f"State({self.code}, {self.name})"
  def __eq__(self, other: "State") -> bool: # type: ignore
    return self.code == other.code and self.name == other.name
  @classmethod
  def query(cls, code: int) -> "State":
    for state in cls.__dict__.values():
      if isinstance(state, cls):
        if state.code == code:
          return state
    raise ValueError(f"Unknown State code: {code}")
  BOUNCING: "State"
  RELEASED: "State"
  PRESSED : "State"
State.BOUNCING = State(0, "BOUNCING")
State.RELEASED = State(1, "RELEASED")
State.PRESSED  = State(2, "PRESSED" )
class BaseButton(abc.ABC):
  def __init__(self, pin: machine.Pin, released_signal: Digital.Signal, interval_ms: int = 16):
    self.pin: machine.Pin = pin
    self.released_signal: Digital.Signal = released_signal
    self.pressed_signal: Digital.Signal = Digital.Signal.inverse(released_signal)
    self.interval_ms: int = interval_ms
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
  def __init__(self, pin: machine.Pin, released_signal: Digital.Signal, interval_ms: int = 16):
    super().__init__(pin, released_signal, interval_ms)
  async def getState(self) -> State:
    await Sleep.async_ms(1)
    pinValue: int = self.pin.value()
    if pinValue == self.released_signal: return State.RELEASED
    elif pinValue == self.pressed_signal: return State.PRESSED
    return State.BOUNCING
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
  def __init__(self, pin: machine.Pin, released_signal: Digital.Signal, interval_ms: int = 1, threshold: int = 16):
    super().__init__(pin, released_signal, interval_ms)
    self.threshold: int = threshold
  async def getState(self):
    cnt: int = 0
    for _ in range(self.threshold):
      cnt += self.pin.value()
      await Sleep.async_ms(self.interval_ms)
    if cnt == self.threshold: 
      return State.RELEASED if self.released_signal.value == 1 else State.PRESSED
    elif cnt == 0: 
      return State.PRESSED if self.pressed_signal.value == 0 else State.RELEASED
    return State.BOUNCING
  async def isReleased(self) -> bool:
    return await Digital.countFiltering_async(self.pin, self.released_signal, self.threshold, self.interval_ms)
  async def isPressed(self) -> bool:
    return await Digital.countFiltering_async(self.pin, self.pressed_signal, self.threshold, self.interval_ms)
  async def isToReleased(self) -> bool:
    return await Digital.isChangedStably_async(self.pin, self.pressed_signal, self.released_signal, self.threshold, self.interval_ms)
  async def isToPressed(self) -> bool:
    return await Digital.isChangedStably_async(self.pin, self.released_signal, self.pressed_signal, self.threshold, self.interval_ms)

class StateDebounceButton(BaseButton):
  def __init__(self, pin: machine.Pin, released_signal: Digital.Signal, interval_ms: int = 16):
    super().__init__(pin, released_signal, interval_ms)
    self._last_state: State = State.BOUNCING
  async def getState(self):
    # await Sleep.async_ms(1)
    pinValue: int = self.pin.value()
    if pinValue == self.released_signal.value: 
      self._last_state = State.RELEASED
    elif pinValue == self.pressed_signal.value: 
      self._last_state = State.PRESSED
    else: 
      self._last_state = State.BOUNCING
    return self._last_state
  async def isReleased(self) -> bool:
    state = await self.getState()
    return state == State.RELEASED
  async def isPressed(self) -> bool:
    state = await self.getState()
    return state == State.PRESSED
  async def isToReleased(self) -> bool:
    if self._last_state == State.BOUNCING: self._last_state = await self.getState()
    if self._last_state == State.PRESSED:
      await Sleep.async_ms(self.interval_ms)
      if await self.isReleased():
        return True
    return False
  async def isToPressed(self) -> bool:
    if self._last_state == State.BOUNCING: self._last_state = await self.getState()
    if self._last_state == State.RELEASED:
      await Sleep.async_ms(self.interval_ms)
      if await self.isPressed():
        return True
    return False

class InterruptDrivenStateDebounceButton(StateDebounceButton):
  class EdgeHandler(ListenerHandler.AsyncHandler):
    def __init__(self, handler):
      self.handler = handler
    async def handle(self, obj = None, *args, **kwargs) -> None:
      asyncio.create_task(self.handler())
  def __init__(self, pin: machine.Pin, released_signal: Digital.Signal, interval_ms: int = 32):
    super().__init__(pin, released_signal, interval_ms)
    self._current_state: State = State.BOUNCING
    self.pin.irq(trigger=Digital.IRQTrigger.RISING.code | Digital.IRQTrigger.FALLING.code, handler=self._irq_handler)
    self._irq_flag: Flag.BooleanFlag = Flag.BooleanFlag()
    self._irq_listenerHandler: ListenerHandler.SyncListenerAsyncHandler = ListenerHandler.SyncListenerAsyncHandler(Flag.BooleanFlagListener(self._irq_flag), InterruptDrivenStateDebounceButton.EdgeHandler(self._irq_agentHandler))
    # self._debounce_timer = Timer.AsyncTimer(period_ms=self.interval_ms, async_callback=InterruptDrivenStateDebounceButton.EdgeHandler(self._debounce_handler))
    self._debounce_timer = Timer.ListenerTimer.AsyncListenerAsyncHandler(period_ms=self.interval_ms, asyncHandler=InterruptDrivenStateDebounceButton.EdgeHandler(self._debounce_handler), mode=Timer.ListenerTimer.Mode.ONE_SHOT)
    self._toReleased_flag: Flag.BooleanFlag = Flag.BooleanFlag()
    self._toPressed_flag: Flag.BooleanFlag = Flag.BooleanFlag()
  async def activate(self):
    # self.logger.debug("[activate] Initializing InterruptDrivenStateDebounceButton...")
    await self._debounce_timer.activate()
    await self._irq_listenerHandler.activate()
  def _irq_handler(self, pin: machine.Pin):
    self._irq_flag.activate()
  async def _irq_agentHandler(self):
    # self.logger.debug("[_irq_agentHandler] IRQ flag detected.")
    self._last_state = self._current_state
    self._current_state = State.BOUNCING
    await self._debounce_timer.activate()
    self._irq_flag.deactivate()
  async def _debounce_handler(self):
    pinValue: int = self.pin.value()
    # self.logger.debug(f"[_debounce_handler] Debounce handler triggered. pinValue={pinValue}, lastState={self._last_state}, currentState={self._current_state}")
    if pinValue == self.released_signal.value: 
      self._current_state = State.RELEASED
    elif pinValue == self.pressed_signal.value: 
      self._current_state = State.PRESSED
    else: 
      await self._debounce_timer.activate()
      # self.logger.warning("Pin state is still ambiguous after debounce.")
    
    if self._current_state == State.RELEASED and self._last_state != State.RELEASED:
      self._toReleased_flag.activate()
      await Sleep.async_ms(self.interval_ms<<1)
      self._toReleased_flag.deactivate()
    elif self._current_state == State.PRESSED and self._last_state != State.PRESSED:
      self._toPressed_flag.activate()
      await Sleep.async_ms(self.interval_ms<<1)
      self._toPressed_flag.deactivate()
  async def getState(self) -> State:
    await Sleep.async_ms(1)
    return self._current_state
  async def isReleased(self) -> bool:
    await Sleep.async_ms(1)
    return self._current_state == State.RELEASED
  async def isPressed(self) -> bool:
    await Sleep.async_ms(1)
    return self._current_state == State.PRESSED
  async def isBouncing(self) -> bool:
    await Sleep.async_ms(1)
    return self._current_state == State.BOUNCING
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
  def __init__(self, button: BaseButton, interval_ms: int = 10):
    self.button: BaseButton = button
    self.interval_ms: int = interval_ms
    # self.logger: Logging.Log = Logging.Log(log_name, log_level)
  async def listen(self, obj = None, *args, **kwargs) -> bool:
    return await self.button.isToPressed()
class OnReleasedListener(ListenerHandler.AsyncListener):
  def __init__(self, button: BaseButton, interval_ms: int = 10):
    self.button: BaseButton = button
    self.interval_ms: int = interval_ms
    # self.logger: Logging.Log = Logging.Log(log_name, log_level)
  async def listen(self, obj = None, *args, **kwargs) -> bool:
    return await self.button.isToReleased()

if __name__ == "__main__":
  class TestSyncHandler(ListenerHandler.SyncHandler):
    # def __init__(self):
    #   self.logger = Logging.Log(log_name, log_level)
    def handle(self, obj = None, *args, **kwargs) -> None:
      Logging.info("TestSyncHandler.handle() executed.")
  class TestAsyncHandler(ListenerHandler.AsyncHandler):
    # def __init__(self):
    #   self.logger = Logging.Log(log_name, log_level)
    async def handle(self, obj = None, *args, **kwargs) -> None:
      await Sleep.async_ms(1)
      Logging.info(f"TestAsyncHandler.handle() executed.")

  # logger = Logging.Log("main", Logging.LEVEL.INFO)
  pin_a = machine.Pin(19, machine.Pin.IN, machine.Pin.PULL_UP)
  pin_b = machine.Pin(20, machine.Pin.IN, machine.Pin.PULL_UP)
  pin_c = machine.Pin(21, machine.Pin.IN, machine.Pin.PULL_UP)

  # log_level = Logging.LEVEL.INFO
  btn_a = CountFilteringImmediateDebounceButton (pin_a, Digital.Signal.HIGH)
  btn_b = StateDebounceButton                   (pin_b, Digital.Signal.HIGH)
  btn_c = InterruptDrivenStateDebounceButton    (pin_c, Digital.Signal.HIGH)
  try: 
    async def testSyncHandler():
      Logging.info("Starting TestSyncHandler...")
      await btn_c.activate()
      await ListenerHandler.AsyncListenerSyncHandler(OnPressedListener (btn_a), TestSyncHandler()).activate()
      # await ListenerHandler.AsyncListenerSyncHandler(OnReleasedListener(btn_a), TestSyncHandler()).activate()

      # await ListenerHandler.AsyncListenerSyncHandler(OnPressedListener (btn_b), TestSyncHandler()).activate()
      await ListenerHandler.AsyncListenerSyncHandler(OnReleasedListener(btn_b), TestSyncHandler()).activate()

      await ListenerHandler.AsyncListenerSyncHandler(OnPressedListener (btn_c), TestSyncHandler()).activate()
      await ListenerHandler.AsyncListenerSyncHandler(OnReleasedListener(btn_c), TestSyncHandler()).activate()
      while True:
        await Sleep.async_s(1)
    asyncio.run(testSyncHandler())
  except KeyboardInterrupt:
    pass
  del btn_a
  del btn_b
  del btn_c

