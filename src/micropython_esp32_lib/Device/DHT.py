"""
# ./Device/DHT.py
TODO: Stateful, do not continuously monitor
"""
import _thread as thread
import asyncio
from machine import Pin # type: ignore
import dht # type: ignore

try:
  from ..System import Time
  from ..System.Time import Sleep
  from ..Utils import Logging
except ImportError:
  from micropython_esp32_lib.System import Time
  from micropython_esp32_lib.System.Time import Sleep
  from micropython_esp32_lib.Utils import Logging

class DHT:
  def __init__(self, pin: Pin, type: str = "DHT11", log_name: str = "DHT") -> None:
    """DHT Sensor

    Args:
        pin (Pin): Data pin
        type (str, optional): Sensor type ("DHT11" or "DHT22"). Defaults to "DHT11".
        log_name (str, optional): The name for the logger. Defaults to "DHT".
        log_level (Logging.Level, optional): The log level. Defaults to Logging.LEVEL.INFO.
    """
    self.pin: Pin = pin
    # self.logger = Logging.Log(log_name, log_level)

    if type == "DHT11":
      self.sensor = dht.DHT11(self.pin)
      self.samplingPeriod_ms: int = 1000  # DHT11 minimum sampling period is 1 seconds
    elif type == "DHT22":
      self.sensor = dht.DHT22(self.pin)
      self.samplingPeriod_ms: int = 2000  # DHT22 minimum sampling period is 2 seconds
    else:
      # self.logger.error(f"Unsupported sensor type \"{type}\". Use \"DHT11\" or \"DHT22\".")
      raise ValueError(f"Unsupported sensor type \"{type}\". Use \"DHT11\" or \"DHT22\".")
    
    self.temperature_C: float | int = 0
    self.humidity_ratio: float | int = 0

    self.nextMeasureTime_ms = 0

    self.measure_thread_enabled: bool = False
    self.measure_thread_id: int | None = None

    self.measure_task_enabled: bool = False
    self.measure_task: asyncio.Task | None = None

  def _measure_sync_(self) -> tuple[float | int, float | int] | None:
    try:
      while Time.current_ms() < self.nextMeasureTime_ms:
        Sleep.sync_ms(1)
      self.sensor.measure()
      self.nextMeasureTime_ms: int = Time.current_ms() + self.samplingPeriod_ms
      self.temperature_C: float | int = self.sensor.temperature()
      self.humidity_ratio: float | int = self.sensor.humidity()
      return self.temperature_C, self.humidity_ratio
    except Exception as e:
      # self.logger.error(f"[_measure_sync_] Failed to measure: {e}")
      return None
  async def _measure_async_(self) -> tuple[float | int, float | int] | None:
    try:
      while Time.current_ms() < self.nextMeasureTime_ms:
        await Sleep.async_ms(1)
      self.sensor.measure()
      self.nextMeasureTime_ms: int = Time.current_ms() + self.samplingPeriod_ms
      self.temperature_C: float | int = self.sensor.temperature()
      self.humidity_ratio: float | int = self.sensor.humidity()
      return self.temperature_C, self.humidity_ratio
    except Exception as e:
      # self.logger.error(f"[_measure_async_] Failed to measure: {e}")
      return None

  def _monitor_sync_(self) -> None: # TODO: consider moving this monitoring pattern to System/EventHandler
    """Measure temperature and humidity"""
    try:
      while self.measure_thread_enabled:
        self._measure_sync_()
    except Exception as e:
      raise e
      # self.logger.error(f"[_monitor_sync_] Failed to monitor: {e}")
  async def _monitor_async_(self) -> None: # TODO: consider moving this monitoring pattern to System/EventHandler
    """Measure temperature and humidity"""
    try:
      while self.measure_thread_enabled:
        await self._measure_async_()
    except Exception as e:
      raise e
      # self.logger.error(f"[_monitor_async_] Failed to monitor: {e}")

  def startMonitor_sync(self) -> None: # TODO: consider moving this monitoring pattern to System/EventHandler
    """Start measuring in thread"""
    if not self.measure_thread_enabled:
      self.measure_thread_enabled = True
      self.measure_thread_id = thread.start_new_thread(self._monitor_sync_, ())
      # self.logger.info("Started synchronous DHT monitoring thread.")
  def startMonitor_async(self) -> None: # TODO: consider moving this monitoring pattern to System/EventHandler
    """Start measuring in task"""
    if not self.measure_task_enabled:
      self.measure_task_enabled = True
      self.measure_task = asyncio.create_task(self._monitor_async_())
      # self.logger.info("Started asynchronous DHT monitoring task.")

  def stopMonitor_sync(self) -> None: # TODO: consider moving this monitoring pattern to System/EventHandler
    """Stop measuring"""
    if self.measure_thread_enabled:
      self.measure_thread_enabled = False
      self.measure_thread_id = None
      # self.logger.info("Stopped synchronous DHT monitoring thread.")
  def stopMonitor_async(self) -> None: # TODO: consider moving this monitoring pattern to System/EventHandler
    """Stop measuring"""
    if self.measure_task_enabled:
      self.measure_task_enabled = False
      if self.measure_task:
          self.measure_task.cancel() # Safely cancel the task
      self.measure_task = None
      # self.logger.info("Stopped asynchronous DHT monitoring task.")

  def Temperature_C_sync(self) -> float | None: # TODO: consider exposing through an EventHandler pattern
    """Get temperature in Celsius"""
    if Time.current_ms() > self.nextMeasureTime_ms:
      self._measure_sync_()
    return self.temperature_C
  def Temperature_K_sync(self) -> float | None: # TODO: consider exposing through an EventHandler pattern
    """Get temperature in Kelvin"""
    if Time.current_ms() > self.nextMeasureTime_ms:
      self._measure_sync_()
    return self.temperature_C + 273.15
  def Temperature_F_sync(self) -> float | None: # TODO: consider exposing through an EventHandler pattern
    """Get temperature in Fahrenheit"""
    if Time.current_ms() > self.nextMeasureTime_ms:
      self._measure_sync_()
    return self.temperature_C * (9/5) + 32.0
  def Humidity_ratio_sync(self) -> float | int | None: # TODO: consider exposing through an EventHandler pattern
    """Get humidity ratio"""
    if Time.current_ms() > self.nextMeasureTime_ms:
      self._measure_sync_()
    return self.humidity_ratio

  async def Temperature_C_async(self) -> float | None: # TODO: consider exposing through an EventHandler pattern
    """Get temperature in Celsius"""
    if Time.current_ms() > self.nextMeasureTime_ms:
      await self._measure_async_()
    return self.temperature_C
  async def Temperature_K_async(self) -> float | None: # TODO: consider exposing through an EventHandler pattern
    """Get temperature in Kelvin"""
    if Time.current_ms() > self.nextMeasureTime_ms:
      await self._measure_async_()
    return self.temperature_C + 273.15
  async def Temperature_F_async(self) -> float | None: # TODO: consider exposing through an EventHandler pattern
    """Get temperature in Fahrenheit"""
    if Time.current_ms() > self.nextMeasureTime_ms:
      await self._measure_async_()
    return self.temperature_C * (9/5) + 32.0
  async def Humidity_ratio_async(self) -> float | int | None: # TODO: consider exposing through an EventHandler pattern
    """Get humidity ratio"""
    if Time.current_ms() > self.nextMeasureTime_ms:
      await self._measure_async_()
    return self.humidity_ratio

if __name__ == "__main__":
  # Logging = Logging.Log("DHT_Test", Logging.LEVEL.INFO)

  def main_sync_test(dht_sensor: DHT) -> None:
    Logging.info("Testing DHT class with thread mode, Press Ctrl+C to stop the program.")
    dht_sensor.startMonitor_sync()
    try:
      while True:
        Sleep.sync_ms(dht_sensor.samplingPeriod_ms)
        Logging.info(f'Temperature: {dht_sensor.Temperature_K_sync():3.1f} K')
        Logging.info(f'Temperature: {dht_sensor.Temperature_C_sync():3.1f} C')
        Logging.info(f'Temperature: {dht_sensor.Temperature_F_sync():3.1f} F')
        Logging.info(f'Humidity: {dht_sensor.Humidity_ratio_sync():3.1f} %')
        Logging.info('\n\n')
    except KeyboardInterrupt:
      Logging.info("Program interrupted")
    finally:
      dht_sensor.stopMonitor_sync()
      Logging.info("Program ended")

  async def main_async_test(dht_sensor: DHT) -> None:
    Logging.info("Testing DHT class with task mode, Press Ctrl+C to stop the program.")
    dht_sensor.startMonitor_async()
    try:
      while True:
        await Sleep.async_ms(dht_sensor.samplingPeriod_ms)
        Logging.info(f'Temperature: {(await dht_sensor.Temperature_K_async()):3.1f} K')
        Logging.info(f'Temperature: {(await dht_sensor.Temperature_C_async()):3.1f} C')
        Logging.info(f'Temperature: {(await dht_sensor.Temperature_F_async()):3.1f} F')
        Logging.info(f'Humidity: {(await dht_sensor.Humidity_ratio_async()):3.1f} %')
        Logging.info('\n\n')
    except KeyboardInterrupt:
      Logging.info("Program interrupted")
    finally:
      dht_sensor.stopMonitor_async()
      Logging.info("Program ended")

  dht_sensor_instance = DHT(Pin(4), "DHT11")
  main_sync_test(dht_sensor_instance)
  asyncio.run(main_async_test(dht_sensor_instance))