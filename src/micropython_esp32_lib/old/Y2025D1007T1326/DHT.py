import _thread as thread
import time
import asyncio
from machine import Pin
import dht

try: 
  from . import SystemTime
  from . import Wait
except ImportError:
  from HRChen import SystemTime
  from HRChen import Wait

class DHT:
  def __init__(self, pin: Pin, type: str = "DHT11", logger_perfix: str | None = None) -> None:
    """DHT Sensor

    Args:
        pin (Pin): Data pin
        type (str, optional): Sensor type ("DHT11" or "DHT22"). Defaults to "DHT11".
    """
    self.pin: Pin = pin
    self.logger_perfix: str | None = logger_perfix

    if type == "DHT11":
      self.sensor = dht.DHT11(self.pin)
      self.samplingPeriod_ms: int = 1000  # DHT11 minimum sampling period is 1 seconds
    elif type == "DHT22":
      self.sensor = dht.DHT22(self.pin)
      self.samplingPeriod_ms: int = 2000  # DHT22 minimum sampling period is 2 seconds
    else:
      if logger_perfix is not None: print(logger_perfix, f"Unsupported sensor type \"{type}\". Use \"DHT11\" or \"DHT22\".")
      raise ValueError(f"Unsupported sensor type \"{type}\". Use \"DHT11\" or \"DHT22\".")
    
    self.temperature_C: float | int = 0
    self.humidity_ratio: float | int = 0

    self.nextMeasureTime_ms = 0

    self.measure_thread_enabled: bool = False
    self.measure_thread_id: int | None = None

    self.measure_task_enabled: bool = False
    self.measure_task: asyncio.Task | None = None

  def _measure_sync_(self) -> tuple[float | int, float | int] | None: # TODO: public this
    try:
      while SystemTime.current_ms() < self.nextMeasureTime_ms:
        Wait.sync_ms(1)
      self.sensor.measure()
      self.nextMeasureTime_ms: int = SystemTime.current_ms() + self.samplingPeriod_ms
      self.temperature_C: float | int = self.sensor.temperature()
      self.humidity_ratio: float | int = self.sensor.humidity()
      return self.temperature_C, self.humidity_ratio
    except Exception as e:
      if self.logger_perfix is not None: print(self.logger_perfix, f" [_measure_sync_] Failed to measure: {e}")
  async def _measure_async_(self) -> tuple[float | int, float | int] | None: # TODO: public this
    try:
      while SystemTime.current_ms() < self.nextMeasureTime_ms:
        await Wait.async_ms(1)
      self.sensor.measure()
      self.nextMeasureTime_ms: int = SystemTime.current_ms() + self.samplingPeriod_ms
      self.temperature_C: float | int = self.sensor.temperature()
      self.humidity_ratio: float | int = self.sensor.humidity()
      return self.temperature_C, self.humidity_ratio
    except Exception as e:
      if self.logger_perfix is not None: print(self.logger_perfix, f" [_measure_async_] Failed to measure: {e}")

  def _monitor_sync_(self) -> None: # TODO: move to EventHandler
    """Measure temperature and humidity"""
    try:
      while self.measure_thread_enabled:
        self._measure_sync_()
    except Exception as e:
      if self.logger_perfix is not None: print(self.logger_perfix, f" [_monitor_sync_] Failed to monitor: {e}")
  async def _monitor_async_(self) -> None: # TODO: move to EventHandler
    """Measure temperature and humidity"""
    try:
      while self.measure_thread_enabled:
        await self._measure_async_()
    except Exception as e:
      if self.logger_perfix is not None: print(self.logger_perfix, f" [_monitor_async_] Failed to monitor: {e}")

  def startMonitor_sync(self) -> None: # TODO: move to EventHandler
    """Start measuring in thread"""
    if not self.measure_thread_enabled:
      self.measure_thread_enabled = True
      self.measure_thread_id = thread.start_new_thread(self._monitor_sync_, ()) 
  def startMonitor_async(self) -> None: # TODO: move to EventHandler
    """Start measuring in task"""
    if not self.measure_task_enabled:
      self.measure_task_enabled = True
      self.measure_task = asyncio.create_task(self._monitor_async_())

  def stopMonitor_sync(self) -> None: # TODO: move to EventHandler
    """Stop measuring"""
    if self.measure_thread_enabled:
      self.measure_thread_enabled = False
      self.measure_thread_id = None
  def stopMonitor_async(self) -> None: # TODO: move to EventHandler
    """Stop measuring"""
    if self.measure_task_enabled:
      self.measure_task_enabled = False
      self.measure_task = None

  def Temperature_C_sync(self) -> float | None: # TODO: move to EventHandler
    """Get temperature in Celsius"""
    if SystemTime.current_ms() > self.nextMeasureTime_ms: 
      self._measure_sync_()
    return self.temperature_C
  def Temperature_K_sync(self) -> float | None: # TODO: move to EventHandler
    """Get temperature in Kelvin"""
    if SystemTime.current_ms() > self.nextMeasureTime_ms: 
      self._measure_sync_()
    return self.temperature_C + 273.15
  def Temperature_F_sync(self) -> float | None: # TODO: move to EventHandler
    """Get temperature in Fahrenheit"""
    if SystemTime.current_ms() > self.nextMeasureTime_ms: 
      self._measure_sync_()
    return self.temperature_C * (9/5) + 32.0
  def Humidity_ratio_sync(self) -> float | None: # TODO: move to EventHandler
    """Get humidity ratio"""
    if SystemTime.current_ms() > self.nextMeasureTime_ms: 
      self._measure_sync_()
    return self.humidity_ratio

  async def Temperature_C_async(self) -> float | None: # TODO: move to EventHandler
    """Get temperature in Celsius"""
    if SystemTime.current_ms() > self.nextMeasureTime_ms: 
      await self._measure_async_()
    return self.temperature_C
  async def Temperature_K_async(self) -> float | None: # TODO: move to EventHandler
    """Get temperature in Kelvin"""
    if SystemTime.current_ms() > self.nextMeasureTime_ms: 
      await self._measure_async_()
    return self.temperature_C + 273.15
  async def Temperature_F_async(self) -> float | None: # TODO: move to EventHandler
    """Get temperature in Fahrenheit"""
    if SystemTime.current_ms() > self.nextMeasureTime_ms: 
      await self._measure_async_()
    return self.temperature_C * (9/5) + 32.0
  async def Humidity_ratio_async(self) -> float | None: # TODO: move to EventHandler
    """Get humidity ratio"""
    if SystemTime.current_ms() > self.nextMeasureTime_ms: 
      await self._measure_async_()
    return self.humidity_ratio

def main_sync(dht: DHT) -> None:
  print("[main_sync] Testing DHT class with thread mode, Press Ctrl+C to stop the program.")
  dht.startMonitor_sync()
  try:
    while True:
      Wait.sync_ms(dht.samplingPeriod_ms)
      print(f'[main_sync] Temperature: {dht.Temperature_K_sync():3.1f} K')
      print(f'[main_sync] Temperature: {dht.Temperature_C_sync():3.1f} C')
      print(f'[main_sync] Temperature: {dht.Temperature_F_sync():3.1f} F')
      print(f'[main_sync] Humidity: {dht.Humidity_ratio_sync():3.1f} %')
      print('\n\n')
  except KeyboardInterrupt:
    print("[main_sync] Program interrupted")
  finally:
    dht.stopMonitor_sync()
    print("[main_sync] Program ended")

async def main_async(dht: DHT) -> None:
  print("[main_async] Testing DHT class with task mode, Press Ctrl+C to stop the program.")
  dht.startMonitor_async()
  try:
    while True:
      await Wait.async_ms(dht.samplingPeriod_ms)
      print(f'[main_async] Temperature: {(await dht.Temperature_K_async()):3.1f} K')
      print(f'[main_async] Temperature: {(await dht.Temperature_C_async()):3.1f} C')
      print(f'[main_async] Temperature: {(await dht.Temperature_F_async()):3.1f} F')
      print(f'[main_async] Humidity: {(await dht.Humidity_ratio_async()):3.1f} %')
      print('\n\n')
  except KeyboardInterrupt:
    print("[main_async] Program interrupted")
  finally:
    dht.stopMonitor_async()
    print("[main_async] Program ended")

if __name__ == "__main__":
  dhtSensor = DHT(Pin(4), "DHT11")
  main_sync(dhtSensor)
  asyncio.run(main_async(dhtSensor))