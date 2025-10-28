# src/micropython_esp32_lib/Device/LightSensor.py
import utime
from machine import Pin, ADC # Assuming ADC is available in the machine module

try:
  from ..System import Utils
  from ..System import Logging
  from ..System import Sleep # For main block test
except ImportError:
  from micropython_esp32_lib.System import Utils
  from micropython_esp32_lib.System import Logging
  from micropython_esp32_lib.System import Sleep

class LightSensor: # TODO: samplingTimes: int = 10, interval_ms: int = 10
  def __init__(self, pin: Pin, signal_highLight: int = Utils.UINT16_MAX, signal_lowLight: int = 0, log_name: str = "LightSensor", log_level: Logging.Level = Logging.LEVEL.INFO):
    self.pin: Pin = pin
    self.adc: ADC = ADC(pin)
    self.signal_highLight: int = signal_highLight
    self.signal_lowLight: int = signal_lowLight
    self.logger = Logging.Log(log_name, log_level)
    self.logger.debug(f"LightSensor initialized on pin {pin} with high_light={signal_highLight}, low_light={signal_lowLight}")

  def signal_u16(self) -> int:
    return self.adc.read_u16()

  def light_u16(self) -> int:
    return int(Utils.map(self.adc.read_u16(), self.signal_lowLight, self.signal_highLight, 0, Utils.UINT16_MAX))


class PhotoResistor(LightSensor):
  def __init__(self, pin: Pin, signal_highLight: int = 0, signal_lowLight: int = Utils.UINT16_MAX, log_name: str = "PhotoResistor", log_level: Logging.Level = Logging.LEVEL.INFO):
    super().__init__(pin, signal_highLight, signal_lowLight, log_name, log_level)

class TEMT6000(LightSensor):
  def __init__(self, pin: Pin, signal_highLight: int = Utils.UINT16_MAX, signal_lowLight: int = 0, log_name: str = "TEMT6000", log_level: Logging.Level = Logging.LEVEL.INFO):
    super().__init__(pin, signal_highLight, signal_lowLight, log_name, log_level)

if __name__ == '__main__':
  logger_main = Logging.Log("LightSensorTest", Logging.LEVEL.INFO)
  logger_main.info("Testing PhotoResistor class.")
  sensor = PhotoResistor(Pin(5), log_level=Logging.LEVEL.DEBUG)
  # sensor = TEMT6000(Pin(5))
  try:
    while True:
      logger_main.info(f"Light value: {sensor.light_u16()}")
      Sleep.sync_ms(200)
  except KeyboardInterrupt:
    logger_main.info("Program interrupted.")
  finally:
    logger_main.info("LightSensor test ended.")