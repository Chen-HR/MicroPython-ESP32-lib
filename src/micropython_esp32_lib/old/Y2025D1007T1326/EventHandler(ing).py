class EventHandler:
  def __init__(self, handler, *args, **kwargs):
    self.handler = handler
    self.args = args
    self.kwargs = kwargs

  def _monitor_sync(self):
    self.handler(*self.args, **self.kwargs)






  # async def _onPress_monitor_async(self) -> None: # TODO: move to EventHandler
  #   """Asynchronous Button onPress monitor"""
  #   while self.onPress_task_enabled:
  #     if await self._isChanged_async(self.released_signal, self.pressed_signal):
  #       if self.onPress is not None:
  #         try:
  #           self.onPress[0](self.onPress[1])
  #         except Exception as e:
  #           print(f"Button onPress exception: {e}")
  #       while self.isPressed():
  #         await asyncio.sleep_ms(self.interval_ms)
  #     await asyncio.sleep_ms(self.interval_ms)
  # async def _onRelease_monitor_async(self) -> None: # TODO: move to EventHandler
  #   """Asynchronous Button onRelease monitor"""
  #   while self.onRelease_task_enabled:
  #     if await self._isChanged_async(self.pressed_signal, self.released_signal):
  #       if self.onRelease is not None:
  #         try:
  #           self.onRelease[0](self.onRelease[1])
  #         except Exception as e:
  #           print(f"Button onRelease exception: {e}")
  #       while self.isReleased():
  #         await asyncio.sleep_ms(self.interval_ms)
  #     await asyncio.sleep_ms(self.interval_ms)

  # def startMonitor(self) -> None: # TODO: move to EventHandler
  #   """Start button monitor in thread"""
  #   if self.onPress_thread_id is None and self.onPress is not None:
  #     self.onPress_thread_enabled = True
  #     self.onPress_thread_id = thread.start_new_thread(self._onPress_monitor, ())
  #     # print(f"onPress_thread_id: {self.onPress_thread_id}")
  #   if self.onRelease_thread_id is None and self.onRelease is not None:
  #     self.onRelease_thread_enabled = True
  #     self.onRelease_thread_id = thread.start_new_thread(self._onRelease_monitor, ())
  #     # print(f"onRelease_thread_id: {self.onRelease_thread_id}")
  # def startMonitor_async(self) -> None: # TODO: move to EventHandler
  #   """Start button monitor in asyncio task"""
  #   if self.onPress_task is None and self.onPress is not None:
  #     self.onPress_task_enabled = True
  #     self.onPress_task = asyncio.create_task(self._onPress_monitor_async())
  #     # print(f"onPress_task: {self.onPress_task}")
  #   if self.onRelease_task is None and self.onRelease is not None:
  #     self.onRelease_task_enabled = True
  #     self.onRelease_task = asyncio.create_task(self._onRelease_monitor_async())
  #     # print(f"onRelease_task: {self.onRelease_task}")

  # def stopMonitor(self) -> None: # TODO: move to EventHandler
  #   """Stop button monitor in thread"""
  #   if self.onPress_thread_id is not None:
  #     self.onPress_thread_enabled = False
  #     self.onPress_thread_id = None
  #   if self.onRelease_thread_id is not None:
  #     self.onRelease_thread_enabled = False
  #     self.onRelease_thread_id = None
  # def stopMonitor_async(self) -> None: # TODO: move to EventHandler
  #   """Stop button monitor in asyncio task"""
  #   if self.onPress_task is not None:
  #     self.onRelease_task_enabled = False
  #     # self.onPress_task.cancel()
  #     self.onPress_task = None
  #   if self.onRelease_task is not None:
  #     self.onRelease_task_enabled = False
  #     # self.onRelease_task.cancel()
  #     self.onRelease_task = None