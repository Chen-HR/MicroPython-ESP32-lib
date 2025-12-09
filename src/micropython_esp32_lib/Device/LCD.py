"""
# [GitHub/dhylands/python_lcd/7affb0b](https://github.com/dhylands/python_lcd/commit/7affb0bceae672624ce1360a18c90623ca6857c1)

This is only for building the installation package at [GitHub/dhylands/python_lcd/7affb0b](https://github.com/dhylands/python_lcd/commit/7affb0bceae672624ce1360a18c90623ca6857c1)
"""
from lcd.esp32_gpio_lcd import GpioLcd
from machine import Pin, PWM

class LCD_GPIO(GpioLcd):
  def __init__(self, 
    rs: Pin,
    enable: Pin,
    d0: Pin | None = None,
    d1: Pin | None = None,
    d2: Pin | None = None,
    d3: Pin | None = None,
    d4: Pin | None = None,
    d5: Pin | None = None,
    d6: Pin | None = None,
    d7: Pin | None = None,
    rw: Pin | None = None,
    v0: Pin | None = None,
    backlight: Pin | None = None,
    contrast_u16: int = 65536//2, 
    num_lines: int = 2,
    num_columns: int = 16
  ):
    super().__init__(rs_pin=rs, enable_pin=enable, d0_pin=d0, d1_pin=d1, d2_pin=d2, d3_pin=d3, d4_pin=d4, d5_pin=d5, d6_pin=d6, d7_pin=d7, rw_pin=rw, backlight_pin=backlight, num_lines=num_lines, num_columns=num_columns)
    if v0 is not None:
      self.v0_pin: Pin = v0
      self.v0_pwm: PWM = PWM(Pin(v0), freq=8192)
      self.v0_pwm.duty_u16(contrast_u16)
    super().clear()
  def setContrast(self, contrast_u16: int):
    if self.v0_pin is not None:
      self.v0_pwm.duty_u16(contrast_u16)

if __name__ == "__main__":
  try:
    from ..System import Time
    from ..System import Logging
    from ..System.Time import Sleep
  except ImportError:
    from micropython_esp32_lib.System import Time
    from micropython_esp32_lib.System import Logging
    from micropython_esp32_lib.System.Time import Sleep
  logger = Logging.Logger(name="LCD", level=Logging.Level.INFO)
  logger.addHandler(Logging.StreamHandler())
  logger.info("Testing LCD class.")
  lcd: LCD_GPIO = LCD_GPIO(rs=Pin(16), enable=Pin(17), d4=Pin(25), d5=Pin(26), d6=Pin(32), d7=Pin(33), v0=Pin(22), contrast_u16=(int)((65535/16)*11), num_lines=2, num_columns=16)
  # lcd: GpioLcd = GpioLcd(rs_pin=Pin(16), enable_pin=Pin(17), d4_pin=Pin(25), d5_pin=Pin(26), d6_pin=Pin(32), d7_pin=Pin(33), num_lines=2, num_columns=16)
  # lcd_contrast = PWM(Pin(22), freq=8192)
  # lcd_contrast.duty_u16((int)(65535/16)*11)
  while True:
    ts = '\n'.join(Time.Formater.format(Time.Time(), Time.Formater.String.DEFAULT).split(' '))
    logger.info(ts.replace('\n', '\\n'))
    lcd.putstr(ts)
    Sleep.sync_ms(965)
    lcd.clear()