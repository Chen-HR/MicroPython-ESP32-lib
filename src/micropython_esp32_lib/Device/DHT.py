"""
# ./Device/DHT.py
"""
from machine import Pin # type: ignore
import dht # type: ignore

try:
  from ..System import Time
except ImportError:
  from micropython_esp32_lib.System import Time

class DHT11(dht.DHT11):
  def __init__(self, pin: Pin, interval_ms: int = 1000) -> None:
    super().__init__(pin)
    self.lastMeasureTime_ms = 0
    self.interval_ms = interval_ms
    self._temperature_C: float = 0.0
    self._humidity_ratio: float = 0.0
  
  def _measure(self) -> None:
    super().measure()
    self.lastMeasureTime_ms = Time.current_ms()
    self._temperature_C = self.temperature()
    self._humidity_ratio = self.humidity()
  def measure(self) -> None:
    if Time.current_ms() > self.lastMeasureTime_ms + self.interval_ms:
      self._measure()
  
  def temperature_C(self) -> float:
    self.measure()
    return self._temperature_C
  def temperature_F(self) -> float:
    return self.temperature_C() * (9/5) + 32
  def temperature_K(self) -> float:
    return self.temperature_C() + 273.15
  
  def humidity_ratio(self) -> float:
    self.measure()
    return self._humidity_ratio

class DHT22(dht.DHT22):
  def __init__(self, pin: Pin, interval_ms: int = 2000) -> None:
    super().__init__(pin)
    self.lastMeasureTime_ms = 0
    self.interval_ms = interval_ms
    self._temperature_C: float = 0.0
    self._humidity_ratio: float = 0.0
  
  def _measure(self) -> None:
    super().measure()
    self.lastMeasureTime_ms = Time.current_ms()
    self._temperature_C = self.temperature()
    self._humidity_ratio = self.humidity()
  def measure(self) -> None:
    if Time.current_ms() > self.lastMeasureTime_ms + self.interval_ms:
      self._measure()
  
  def temperature_C(self) -> float:
    self.measure()
    return self._temperature_C
  def temperature_F(self) -> float:
    return self.temperature_C() * (9/5) + 32
  def temperature_K(self) -> float:
    return self.temperature_C() + 273.15
  
  def humidity_ratio(self) -> float:
    self.measure()
    return self._humidity_ratio
