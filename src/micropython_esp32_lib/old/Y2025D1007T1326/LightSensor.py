import _thread as thread
import utime as time
from machine import Pin, ADC # Assuming ADC is available in the machine module

try: 
  from . import utils
except ImportError:
  from HRChen import utils

class LightSensor: # TODO: samplingTimes: int = 10, interval_ms: int = 10
  def __init__(self, pin: Pin, signal_highLight: int = utils.UINT16_MAX, signal_lowLight: int = 0):
    self.pin: Pin = pin
    self.adc: ADC = ADC(pin)
    self.signal_highLight: int = signal_highLight
    self.signal_lowLight: int = signal_lowLight
    # self.samplingTimes: int = samplingTimes
    # self.interval_ms: int = interval_ms

  def signal_u16(self) -> int:
    return self.adc.read_u16()

  def light_u16(self) -> int:
    return int(utils.map(self.adc.read_u16(), self.signal_lowLight, self.signal_highLight, 0, utils.UINT16_MAX))


class PhotoResistor(LightSensor):
  def __init__(self, pin: Pin, signal_highLight: int = 0, signal_lowLight: int = utils.UINT16_MAX):
    super().__init__(pin, signal_highLight, signal_lowLight)

class TEMT6000(LightSensor):
  def __init__(self, pin: Pin, signal_highLight: int = utils.UINT16_MAX, signal_lowLight: int = 0):
    super().__init__(pin, signal_highLight, signal_lowLight)

if __name__ == '__main__':
  sensor = PhotoResistor(Pin(5))
  # sensor = TEMT6000(Pin(5))
  while True:
    print(sensor.light_u16())
    time.sleep_ms(200)