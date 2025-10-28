# src/micropython_esp32_lib/Device/Button/StateMechanismButton.py
import machine
import _thread as thread # For starting synchronous event handlers
import asyncio # For starting asynchronous event handlers

try:
  from ...System import Time
  from ...System import Sleep
  from ...System import Logging
  from ...System import Digital
  from ...System import EventHandler
  from ...System import Timer
  from ...System import Enum
except ImportError:
  # Fallback for direct execution/testing outside the package structure
  from micropython_esp32_lib.System import Time
  from micropython_esp32_lib.System import Sleep
  from micropython_esp32_lib.System import Logging
  from micropython_esp32_lib.System import Digital
  from micropython_esp32_lib.System import EventHandler
  from micropython_esp32_lib.System import Timer
  from micropython_esp32_lib.System import Enum

class BasicState(Enum.Unit):
  pass
class BASICSTATE:
  BOUNCING = BasicState("BOUNCING", 0)
  RELEASED = BasicState("RELEASED", 1)
  PRESSED = BasicState("PRESSED", 2)

class Button:
  def __init__(self, 
               pin: machine.Pin, 
               pressed_signal: Digital.Signal, 
               released_signal: Digital.Signal, 
               debounce_ms: int = 50, # Time to stabilize pin input
               long_press_timeout_ms: int = 1000, # Time for a long press to be detected
               multi_click_window_ms: int = 300, # Time window for subsequent clicks in a multi-click sequence
               timer_ids: tuple[int, int, int] = (-1, -1, -1), # (debounce_id, long_press_id, multi_click_id)
               log_name: str = "StateMechanismButton", 
               log_level: Logging.Level = Logging.LEVEL.INFO) -> None:
    
    self.pin: machine.Pin = pin
    self.pressed_signal: Digital.Signal = pressed_signal
    self.released_signal: Digital.Signal = released_signal
    
    self.debounce_ms: int = debounce_ms
    self.long_press_timeout_ms: int = long_press_timeout_ms
    self.multi_click_window_ms: int = multi_click_window_ms

    self.logger = Logging.Log(log_name, log_level)
    self.logger.warning("`micropython_esp32_lib.Device.Button.StateMechanismButton.py` does not work properly, it is recommended to use the instant asynchronous version")
  
    # Internal state and flags
    self._current_state: BasicState = BASICSTATE.RELEASED # Assume starts released
    self._last_irq_time_ms: int = 0 # To help manage rapid IRQs (though timer restart handles most debounce)

    # Event flags (to be polled by EventHandler.Event classes)
    self._on_press_flag: bool = False
    self._on_release_flag: bool = False
    self._on_long_press_flag: bool = False
    self._multi_click_event_flag: bool = False

    # Event related values
    self._press_start_time_ms: int = 0
    self._last_press_duration_ms: int = 0 # Duration of the last stable press
    self._multi_click_pending_count: int = 0 # Counts clicks within the active window
    self._finalized_click_count: int = 0 # The count when the multi-click window closes

    # Timers (using default -1 for virtual timers, or specific IDs if provided)
    try:
      self._debounce_timer_hw = Timer.AsyncTimer(id=timer_ids[0], log_name=f"{log_name}.DebounceTimer", log_level=log_level)
      self._long_press_timer_hw = Timer.AsyncTimer(id=timer_ids[1], log_name=f"{log_name}.LongPressTimer", log_level=log_level)
      self._multi_click_window_timer_hw = Timer.AsyncTimer(id=timer_ids[2], log_name=f"{log_name}.MultiClickTimer", log_level=log_level)
    except Exception as e:
      self.logger.error(f"Failed to initialize one or more timers. Button functionality may be limited: {e}")
      self._debounce_timer_hw = None
      self._long_press_timer_hw = None
      self._multi_click_window_timer_hw = None
      # Re-raise to indicate a critical setup failure if any timer fails
      raise e

    # Ensure timers are deinitialized initially
    self._deinit_all_timers()

    # Configure pin interrupt: trigger on both rising and falling edges
    # The handler itself must be registered after timers are initialized.
    self.pin.irq(trigger=machine.Pin.IRQ_RISING | machine.Pin.IRQ_FALLING, handler=self._pin_irq_handler)
    self.logger.info(f"Button initialized on pin {pin}. Debounce: {debounce_ms}ms, LongPress: {long_press_timeout_ms}ms, MultiClickWindow: {multi_click_window_ms}ms.")

    self.EventHandlers: list[EventHandler.EventHandler] = [] # For external event listeners

  def _deinit_all_timers(self) -> None:
    """Deinitializes all internal timers if they are active."""
    if self._debounce_timer_hw:
      self._debounce_timer_hw.deinit()
    if self._long_press_timer_hw:
      self._long_press_timer_hw.deinit()
    if self._multi_click_window_timer_hw:
      self._multi_click_window_timer_hw.deinit()
    self.logger.debug("All internal timers deinitialized.")

  def _pin_irq_handler(self, pin: machine.Pin) -> None:
    """
    Interrupt service routine (ISR) for pin changes.
    This function should be as fast as possible.
    It primarily sets the state to BOUNCING and schedules the debounce timer.
    """
    # Quick check to filter out spurious rapid IRQs if the platform is very noisy
    current_time_ms = Time.current_ms()
    if (current_time_ms - self._last_irq_time_ms) < 5: # Basic hardware-level filtering (e.g., 5ms)
        # self.logger.debug("Ignoring rapid IRQ event.") # Logging in ISR can cause issues, keep it minimal
        return
    self._last_irq_time_ms = current_time_ms
    
    # Set state to BOUNCING and restart debounce timer
    # AsyncTimer.init will automatically cancel any previous task associated with this timer.
    self._current_state = BASICSTATE.BOUNCING
    self.logger.debug(f"IRQ detected on pin {pin}. State set to BOUNCING.")

    if self._debounce_timer_hw:
      try:
        self._debounce_timer_hw.init(
          period_ms=self.debounce_ms,
          callback=lambda t: self._debounce_callback(), # No need to pass timer object if not used
          mode=Timer.MODE.ONE_SHOT
        )
        self.logger.debug(f"Debounce timer started for {self.debounce_ms}ms.")
      except Exception as e:
        self.logger.error(f"Failed to start debounce timer from IRQ: {e}")
    else:
      self.logger.error("Debounce timer not initialized. Button debouncing will not work.")

  def _debounce_callback(self) -> None:
    """
    Callback function for the debounce timer.
    Executes after the debounce period if no further pin changes occurred.
    Determines stable pin state and updates button logic.
    """
    # Always deinit debounce timer once its callback fires, it's a one-shot.
    # This also handles cases where a new IRQ re-initialized it, and this callback is stale.
    if self._debounce_timer_hw and self._debounce_timer_hw.active:
      self._debounce_timer_hw.deinit()

    current_time_ms = Time.current_ms()
    stable_pin_value = self.pin.value()
    
    if stable_pin_value == self.pressed_signal.value:
      if self._current_state != BASICSTATE.PRESSED: # Only process if state truly changed to PRESSED
        self.logger.info("Button state stable: PRESSED")
        self._current_state = BASICSTATE.PRESSED
        self._on_press_flag = True # Set event flag for OnPressEvent

        self._press_start_time_ms = current_time_ms # Record press start time

        # Start long press timer
        if self._long_press_timer_hw:
          # init handles deinit of previous task
          try:
            self._long_press_timer_hw.init(
              period_ms=self.long_press_timeout_ms,
              callback=lambda t: self._long_press_callback(),
              mode=Timer.MODE.ONE_SHOT
            )
            self.logger.debug(f"Long press timer started for {self.long_press_timeout_ms}ms.")
          except Exception as e:
            self.logger.error(f"Failed to start long press timer: {e}")
            
    elif stable_pin_value == self.released_signal.value:
      if self._current_state != BASICSTATE.RELEASED: # Only process if state truly changed to RELEASED
        self.logger.info("Button state stable: RELEASED")
        self._current_state = BASICSTATE.RELEASED
        self._on_release_flag = True # Set event flag for OnReleaseEvent

        # Calculate press duration
        if self._press_start_time_ms > 0:
          self._last_press_duration_ms = current_time_ms - self._press_start_time_ms
          self.logger.debug(f"Last press duration: {self._last_press_duration_ms}ms")
          self._press_start_time_ms = 0 # Reset press start time

        # Determine if it was a short press (potential click)
        is_short_press = False
        if self._long_press_timer_hw and self._long_press_timer_hw.active:
          self._long_press_timer_hw.deinit() # Button was released before long press timeout, so it's a click
          self.logger.debug("Long press timer deinitialized (button released early, detected as click).")
          is_short_press = True
        # else: if long press timer was not active, it either already fired (long press detected)
        # or it was never started (very quick press/release before debounce).
        # In the case of long press detected, _long_press_callback already finalized multiclicks.

        # Multi-click logic for short presses/clicks: increment count and restart window
        if is_short_press:
            self._multi_click_pending_count += 1
            self.logger.debug(f"Click detected. Multi-click pending count: {self._multi_click_pending_count}")

            if self._multi_click_window_timer_hw:
                # init handles deinit of previous task
                try:
                    self._multi_click_window_timer_hw.init(
                        period_ms=self.multi_click_window_ms,
                        callback=lambda t: self._multi_click_window_callback(),
                        mode=Timer.MODE.ONE_SHOT
                    )
                    self.logger.debug(f"Multi-click window timer started/restarted for {self.multi_click_window_ms}ms.")
                except Exception as e:
                    self.logger.error(f"Failed to start multi-click window timer: {e}")
        else:
            # If it was not a short press (e.g., a full long press completed),
            # ensure any pending multi-click sequence is finalized.
            if self._multi_click_pending_count > 0 and \
               self._multi_click_window_timer_hw and self._multi_click_window_timer_hw.active:
                 self._multi_click_window_timer_hw.deinit() # Manually close window
                 self._multi_click_window_callback() # Finalize clicks immediately
                 self.logger.debug("Multi-click window timer deinitialized and finalized after non-short press release.")

    else:
      self.logger.warning(f"Unexpected stable pin value {stable_pin_value}. Expected {self.pressed_signal.value} or {self.released_signal.value}.")

  def _long_press_callback(self) -> None:
    """
    Callback for the long press timer.
    Fires after long_press_timeout_ms. Checks if button is still pressed.
    """
    # Always deinit long press timer once its callback fires, it's a one-shot.
    if self._long_press_timer_hw and self._long_press_timer_hw.active:
      self._long_press_timer_hw.deinit()

    if self._current_state == BASICSTATE.PRESSED and self.pin.value() == self.pressed_signal.value:
      self.logger.info(f"Long press detected ({self.long_press_timeout_ms}ms).")
      self._on_long_press_flag = True
      
      # If a long press is detected, any ongoing multi-click sequence should be terminated and finalized.
      if self._multi_click_window_timer_hw and self._multi_click_window_timer_hw.active:
        self._multi_click_window_timer_hw.deinit()
        self.logger.debug("Long press finalized multi-click window.")
        self._multi_click_window_callback() # Manually trigger to finalize any previous clicks
    else:
      self.logger.debug("Long press timer fired, but button was not continuously pressed (false positive or early release).")

  def _multi_click_window_callback(self) -> None:
    """
    Callback for the multi-click window timer.
    Fires after multi_click_window_ms without further clicks.
    Finalizes the click count for the current sequence.
    """
    # Always deinit multi-click timer once its callback fires, it's a one-shot.
    if self._multi_click_window_timer_hw and self._multi_click_window_timer_hw.active:
      self._multi_click_window_timer_hw.deinit()

    self.logger.debug(f"Multi-click window closed. Finalizing {self._multi_click_pending_count} clicks.")
    self._finalized_click_count = self._multi_click_pending_count
    if self._finalized_click_count > 0:
      self._multi_click_event_flag = True
    self._multi_click_pending_count = 0 # Reset for the next sequence

  # --- Public Getters for Event Handlers ---
  # These methods are designed to be called by external EventHandler.Event objects
  # and will often clear the internal flag after reading.

  def get_on_press_flag(self) -> bool:
    """Returns True if a press event occurred and clears the flag."""
    if self._on_press_flag:
      self._on_press_flag = False
      return True
    return False

  def get_on_release_flag(self) -> bool:
    """Returns True if a release event occurred and clears the flag."""
    if self._on_release_flag:
      self._on_release_flag = False
      return True
    return False

  def get_on_long_press_flag(self) -> bool:
    """Returns True if a long press event occurred and clears the flag."""
    if self._on_long_press_flag:
      self._on_long_press_flag = False
      return True
    return False

  def get_last_press_duration_ms(self) -> int:
    """Returns the duration of the last stable press."""
    return self._last_press_duration_ms

  def get_finalized_click_count(self) -> int:
    """
    Returns the finalized count of clicks from the last multi-click window.
    Resets the multi-click event flag after being read.
    """
    if self._multi_click_event_flag:
      self._multi_click_event_flag = False
      return self._finalized_click_count
    return 0 # Return 0 if no finalized event

  # --- EventHandler Integration (re-used from RealTimeButton) ---
  def addEventHandler(self, eventHandler: EventHandler.EventHandler):
    """Add event handler"""
    if not isinstance(eventHandler, EventHandler.EventHandler):
      raise TypeError("eventHandler must be an instance of EventHandler.EventHandler")
    self.EventHandlers.append(eventHandler)
    return self

  def startEventHandlers_sync(self) -> None:
    """Start all event handlers in sync mode"""
    # WARNING: This attempts to start each event handler in a new thread.
    # MicroPython on ESP32 has limited thread support (often 1-2 user threads).
    # Running multiple buttons in sync mode this way will likely lead to OSError.
    self.logger.warning("Starting synchronous event handlers will attempt to create multiple threads. "
                        "MicroPython's _thread module on ESP32 may have limitations (e.g., 1-2 user threads). "
                        "This may result in OSError: can't create thread.")
    self.logger.info("Starting all event handlers in sync mode")
    for eh in self.EventHandlers:
      eh.start_sync(self)
  
  def startEventHandlers_async(self) -> None:
    """Start all event handlers in async mode"""
    self.logger.info("Starting all event handlers in async mode")
    for eh in self.EventHandlers:
      eh.start_async(self)

  def stopEventHandlers(self) -> None:
    """Stop all event handlers"""
    self.logger.info("Stopping all event handlers")
    # Deinitialize internal timers first to prevent further callbacks.
    self._deinit_all_timers()
    # Disable the pin IRQ to prevent further interrupts
    self.pin.irq(handler=None)
    # Stop external event handlers (which will cancel their tasks/threads)
    for eh in self.EventHandlers:
      eh.stop()

  def __del__(self) -> None:
    """Ensure all resources are cleaned up on object deletion."""
    self.stopEventHandlers()
    # It's good practice to free the Timer IDs if they were dynamically assigned
    if self._debounce_timer_hw: Timer.AsyncTimer.idManager.free(self._debounce_timer_hw._timer_id)
    if self._long_press_timer_hw: Timer.AsyncTimer.idManager.free(self._long_press_timer_hw._timer_id)
    if self._multi_click_window_timer_hw: Timer.AsyncTimer.idManager.free(self._multi_click_window_timer_hw._timer_id)
    self.logger.info("Button object deleted and resources cleaned up.")


# --- Event Classes adapted for StateMechanismButton ---

class OnPressEvent(EventHandler.Event):
  def __init__(self, object: Button, log_name: str = "Button.OnPressEvent", log_level: Logging.Level = Logging.LEVEL.INFO, *args, **kwargs):
    super().__init__(object, *args, **kwargs)
    self.object: Button = object
    self.logger = Logging.Log(f"{log_name}.{self.object.logger.name}", log_level)
  def monitor_sync(self) -> bool:
    # In synchronous mode, the main loop would typically call this periodically.
    # The flag is cleared upon reading.
    result = self.object.get_on_press_flag()
    self.logger.debug(f"OnPressEvent.monitor_sync: {result}")
    return result
  async def monitor_async(self) -> bool:
    # In asynchronous mode, an asyncio task would call this periodically.
    # The flag is cleared upon reading.
    result = self.object.get_on_press_flag() 
    self.logger.debug(f"OnPressEvent.monitor_async: {result}")
    return result

class OnReleaseEvent(EventHandler.Event):
  def __init__(self, object: Button, log_name: str = "Button.OnReleaseEvent", log_level: Logging.Level = Logging.LEVEL.INFO, *args, **kwargs):
    super().__init__(object, *args, **kwargs)
    self.object: Button = object
    self.logger = Logging.Log(f"{log_name}.{self.object.logger.name}", log_level)
  def monitor_sync(self) -> bool:
    result = self.object.get_on_release_flag()
    self.logger.debug(f"OnReleaseEvent.monitor_sync: {result}")
    return result
  async def monitor_async(self) -> bool:
    result = self.object.get_on_release_flag()
    self.logger.debug(f"OnReleaseEvent.monitor_async: {result}")
    return result

class OnLongPressEvent(EventHandler.Event):
  def __init__(self, object: Button, log_name: str = "Button.OnLongPressEvent", log_level: Logging.Level = Logging.LEVEL.INFO, *args, **kwargs):
    super().__init__(object, *args, **kwargs)
    self.object: Button = object
    self.logger = Logging.Log(f"{log_name}.{self.object.logger.name}", log_level)
  def monitor_sync(self) -> bool:
    result = self.object.get_on_long_press_flag()
    self.logger.debug(f"OnLongPressEvent.monitor_sync: {result}")
    return result
  async def monitor_async(self) -> bool:
    result = self.object.get_on_long_press_flag()
    self.logger.debug(f"OnLongPressEvent.monitor_async: {result}")
    return result

class OnMultiClickEvent(EventHandler.Event):
  def __init__(self, object: Button, min_clicks: int, max_clicks: int = 0, log_name: str = "Button.OnMultiClickEvent", log_level: Logging.Level = Logging.LEVEL.INFO, *args, **kwargs):
    super().__init__(object, *args, **kwargs)
    self.object: Button = object
    self.min_clicks: int = min_clicks
    # Ensure max_clicks is at least min_clicks if provided, or defaults to min_clicks for exact match
    self.max_clicks: int = max_clicks if max_clicks >= min_clicks else min_clicks 
    self.logger = Logging.Log(f"{log_name}.{self.object.logger.name}", log_level)
    if min_clicks <= 0:
      self.logger.warning(f"Invalid min_clicks: {min_clicks}. Must be > 0.")

  def monitor_sync(self) -> bool:
    finalized_count = self.object.get_finalized_click_count()
    if finalized_count > 0: # Only process if there was a finalized click event
      self.logger.debug(f"OnMultiClickEvent.monitor_sync - Finalized count: {finalized_count}, Min: {self.min_clicks}, Max: {self.max_clicks}")
      if self.min_clicks <= finalized_count and (self.max_clicks == 0 or finalized_count <= self.max_clicks):
        return True
    return False

  async def monitor_async(self) -> bool:
    finalized_count = self.object.get_finalized_click_count()
    if finalized_count > 0: # Only process if there was a finalized click event
      self.logger.debug(f"OnMultiClickEvent.monitor_async - Finalized count: {finalized_count}, Min: {self.min_clicks}, Max: {self.max_clicks}")
      if self.min_clicks <= finalized_count and (self.max_clicks == 0 or finalized_count <= self.max_clicks):
        return True
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

  class TestHandler(EventHandler.Handler):
    """A concrete Handler to execute button event logic."""
    def __init__(self, button_name: str, event_type: str, counter: Counter | None = None, log_level: Logging.Level = Logging.LEVEL.INFO):
      super().__init__(None) # No object needed for this generic handler in its simplest form
      self.button_name: str = button_name
      self.event_type: str = event_type
      self.counter: Counter = counter if counter is not None else Counter(f"Counter.{event_type}")
      self.logger = Logging.Log(f"TestHandler.{event_type}", log_level)
    
    # Store the button object if needed for specific data like duration/click_count
    # This assumes the EventHandler.Event passes the button object to the Handler during setup if needed.
    # For simplicity, we are assuming 'object' refers to the Button instance in the event classes.
    _button_instance_ref = None # A placeholder to hold the button instance for duration/count

    def handle_sync(self) -> None:
      """Synchronous event execution."""
      self.counter.increment()
      message_suffix = ""
      # Access button object from self.object if EventHandler.Event passed it
      # For now, let's assume the context of `self.object` refers to the Button in these handlers
      # This needs careful design, typically a handler's `__init__` takes required data or the event object.
      # For this test, we'll try to infer it via the event's object.
      
      # NOTE: Direct access to self.object.get_X() from handler is NOT robust,
      # as `self.object` in TestHandler is None.
      # Proper way: Handler `__init__` should receive `button` instance or relevant data.
      # For this example, let's make `TestHandler` slightly more aware for demonstration.
      # A better design would be for the Event to pass specific data to the Handler `handle_sync/async` method.
      
      # For demonstration purposes, we will access the button object via the event wrapper
      # This requires modifying the EventHandler.EventHandler to pass the source object to the handler's handle method.
      # Given the current EventHandler design: `handler.handle_sync()`
      # We would need `handler.handle_sync(self.object)` if `self.object` from event is the button.
      # However, this changes the interface.
      # Let's assume for this specific test, we'll try to get data from the 'event' object if available
      
      # Simplified: If the TestHandler *knew* which button it belongs to, it could get data directly.
      # For now, we'll make a slight adjustment to the message format, knowing which event it is.
      
      if self.event_type == 'Release' and hasattr(self._button_instance_ref, 'get_last_press_duration_ms'):
          duration = self._button_instance_ref.get_last_press_duration_ms()
          message_suffix = f" (Duration: {duration}ms)"
      elif 'Click' in self.event_type and hasattr(self._button_instance_ref, 'get_finalized_click_count'):
          # The OnMultiClickEvent already filters by min/max clicks, so handler just logs success.
          # If we needed the *exact* count, OnMultiClickEvent could pass it.
          # For now, we'll just acknowledge the event.
          pass # Message suffix already handled by event_type
          
      self.logger.info(f"[{self.button_name}] {self.event_type} detected {self.counter.get()} times.{message_suffix}")
    
    async def handle_async(self) -> None:
      """Asynchronous event execution."""
      self.logger.debug(f"Async handling {self.event_type} for {self.button_name}")
      self.handle_sync() # Call sync version for message generation
      await Sleep.async_ms(1) # Small delay to yield control

  # Dynamically set the button instance reference for TestHandler if possible
  def create_test_handler_with_button_ref(button_obj, button_name, event_type, counter_name, log_level):
      handler = TestHandler(button_name, event_type, Counter(counter_name), log_level)
      handler._button_instance_ref = button_obj # Attach the button instance
      return handler

  PIN_A = 19
  PIN_B = 20
  PIN_C = 21
  DEBOUNCE_MS = 50
  LONGPRESS_TIMEOUT = 1000 # 1 second
  MULTICLICK_WINDOW = 400 # 400ms window for multi-clicks
  PRESSED_SIGNAL: Digital.Signal = Digital.SIGNAL.LOW  # Assuming active-low button with PULL_UP
  RELEASED_SIGNAL: Digital.Signal = Digital.SIGNAL.HIGH # Assuming active-low button with PULL_UP

  # For demonstration, use arbitrary timer IDs. In a real application, ensure uniqueness
  # or use id=-1 for virtual timers if multiple hardware timers are scarce/conflicting.
  # ESP32 usually has 4 hardware timers (0-3).
  # Note: AsyncTimer.idManager handles ID allocation for -1, but explicit IDs are used for clarity here.
  TIMER_IDS_A = (0, 1, 2) 
  TIMER_IDS_B = (-1, -1, -1) # Using virtual timers for B and C to reduce hardware timer contention
  TIMER_IDS_C = (-1, -1, -1)

  logger = Logging.Log(name="main", level=Logging.LEVEL.INFO)
  logger.warning("Note: Using multiple explicit hardware AsyncTimers (e.g., TIMER_IDS_A) may be limited by the number of hardware timers available on some MicroPython ports (ESP32 typically has 4). Virtual timers (id=-1, as for B and C) use software-based timing which is more flexible but might be less precise under heavy load.")
  logger.info("\n\n")

  pin_a = machine.Pin(PIN_A, machine.Pin.IN, machine.Pin.PULL_UP)
  pin_b = machine.Pin(PIN_B, machine.Pin.IN, machine.Pin.PULL_UP)
  pin_c = machine.Pin(PIN_C, machine.Pin.IN, machine.Pin.PULL_UP)

  # Initialize Buttons
  button_a = Button(pin_a, PRESSED_SIGNAL, RELEASED_SIGNAL, DEBOUNCE_MS, LONGPRESS_TIMEOUT, MULTICLICK_WINDOW, TIMER_IDS_A, log_name="Button.A", log_level=Logging.LEVEL.DEBUG)
  button_b = Button(pin_b, PRESSED_SIGNAL, RELEASED_SIGNAL, DEBOUNCE_MS, LONGPRESS_TIMEOUT, MULTICLICK_WINDOW, TIMER_IDS_B, log_name="Button.B", log_level=Logging.LEVEL.DEBUG)
  button_c = Button(pin_c, PRESSED_SIGNAL, RELEASED_SIGNAL, DEBOUNCE_MS, LONGPRESS_TIMEOUT, MULTICLICK_WINDOW, TIMER_IDS_C, log_name="Button.C", log_level=Logging.LEVEL.DEBUG)

  # Add Event Handlers for Button A
  button_a.addEventHandler(EventHandler.EventHandler(OnPressEvent(button_a), create_test_handler_with_button_ref(button_a, "Button A", "Press", "ButtonA_Press", Logging.LEVEL.INFO)))\
          .addEventHandler(EventHandler.EventHandler(OnReleaseEvent(button_a), create_test_handler_with_button_ref(button_a, "Button A", "Release", "ButtonA_Release", Logging.LEVEL.INFO)))\
          .addEventHandler(EventHandler.EventHandler(OnLongPressEvent(button_a), create_test_handler_with_button_ref(button_a, "Button A", "LongPress", "ButtonA_LongPress", Logging.LEVEL.INFO)))\
          .addEventHandler(EventHandler.EventHandler(OnMultiClickEvent(button_a, min_clicks=2, max_clicks=2), create_test_handler_with_button_ref(button_a, "Button A", "DoubleClick", "ButtonA_DoubleClick", Logging.LEVEL.INFO)))\
          .addEventHandler(EventHandler.EventHandler(OnMultiClickEvent(button_a, min_clicks=3), create_test_handler_with_button_ref(button_a, "Button A", "TripleClick", "ButtonA_TripleClick", Logging.LEVEL.INFO)))
  
  # Add Event Handlers for Button B
  button_b.addEventHandler(EventHandler.EventHandler(OnPressEvent(button_b), create_test_handler_with_button_ref(button_b, "Button B", "Press", "ButtonB_Press", Logging.LEVEL.INFO)))\
          .addEventHandler(EventHandler.EventHandler(OnReleaseEvent(button_b), create_test_handler_with_button_ref(button_b, "Button B", "Release", "ButtonB_Release", Logging.LEVEL.INFO)))\
          .addEventHandler(EventHandler.EventHandler(OnLongPressEvent(button_b), create_test_handler_with_button_ref(button_b, "Button B", "LongPress", "ButtonB_LongPress", Logging.LEVEL.INFO)))\
          .addEventHandler(EventHandler.EventHandler(OnMultiClickEvent(button_b, min_clicks=2, max_clicks=2), create_test_handler_with_button_ref(button_b, "Button B", "DoubleClick", "ButtonB_DoubleClick", Logging.LEVEL.INFO)))

  # Add Event Handlers for Button C
  button_c.addEventHandler(EventHandler.EventHandler(OnPressEvent(button_c), create_test_handler_with_button_ref(button_c, "Button C", "Press", "ButtonC_Press", Logging.LEVEL.INFO)))\
          .addEventHandler(EventHandler.EventHandler(OnReleaseEvent(button_c), create_test_handler_with_button_ref(button_c, "Button C", "Release", "ButtonC_Release", Logging.LEVEL.INFO)))\
          .addEventHandler(EventHandler.EventHandler(OnLongPressEvent(button_c), create_test_handler_with_button_ref(button_c, "Button C", "LongPress", "ButtonC_LongPress", Logging.LEVEL.INFO)))\
          .addEventHandler(EventHandler.EventHandler(OnMultiClickEvent(button_c, min_clicks=2, max_clicks=2), create_test_handler_with_button_ref(button_c, "Button C", "DoubleClick", "ButtonC_DoubleClick", Logging.LEVEL.INFO)))

  logger.info("Testing StateMechanismButton class.")
  logger.info("  (Press: OnPress, Release: OnRelease (shows duration), Hold > 1s: LongPress, Double-Click < 400ms: DoubleClick, Triple-Click < 400ms: TripleClick)")
  logger.info("  (Press Ctrl+C to stop the program.)")
  try:
    logger.info("Starting asynchronous (Asyncio) monitors...")
    button_a.startEventHandlers_async()
    button_b.startEventHandlers_async()
    button_c.startEventHandlers_async()

    async def main_async_test():
      while True: 
          await Sleep.async_ms(100) # Keep event loop running for handlers to poll
    asyncio.run(main_async_test())
  except KeyboardInterrupt:
    logger.info("Program interrupted by KeyboardInterrupt.")
  finally:
    button_a.stopEventHandlers()
    button_b.stopEventHandlers()
    button_c.stopEventHandlers()
    logger.info("Asynchronous monitors stopped. Program ended.")

  logger.info("\n\n")

  # --- Synchronous Test (Likely to hit thread limit on ESP32) ---
  logger.info("Testing StateMechanismButton class with synchronous (Thread) mode.")
  logger.info("  (Press: OnPress, Release: OnRelease (shows duration), Hold > 1s: LongPress, Double-Click < 400ms: DoubleClick, Triple-Click < 400ms: TripleClick)")
  logger.info("  (Press Ctrl+C to stop the program.)")
  try:
    logger.info("Starting synchronous (Thread) monitors...")
    button_a.startEventHandlers_sync()
    button_b.startEventHandlers_sync()
    # button_c.startEventHandlers_sync()
    while True: 
        Sleep.sync_ms(100) # Keep main thread alive, allowing other threads to run
  except KeyboardInterrupt:
    logger.info("Program interrupted by KeyboardInterrupt.")
  except OSError as e:
    logger.error(f"OSError during synchronous monitoring: {e}. This likely means too many threads were attempted. "
                 "Try running with fewer buttons in synchronous mode, or stick to asyncio for multi-event handling.")
  finally:
    button_a.stopEventHandlers()
    button_b.stopEventHandlers()
    # button_c.stopEventHandlers()
    logger.info("Synchronous monitors stopped. Program ended.")