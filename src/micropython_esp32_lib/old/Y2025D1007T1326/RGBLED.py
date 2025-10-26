import machine
import utime
import neopixel

try: 
  from . import utils
except ImportError:
  from HRChen import utils

class PWMLED:
  def __init__(self, pin: machine.Pin, statuOn_dutyRatio: float = 1.0, statuOff_dutyRatio: float = 0.0, frequency_Hz: int = 256) -> None:
    # self.pin: machine.Pin = pin
    self.pin_pwm: machine.PWM = machine.PWM(pin, freq=frequency_Hz)
    self.statuOn_dutyu16: int = int(utils.map(statuOn_dutyRatio, 0.0, 1.0, 0.0, 65535.0))
    self.statuOff_dutyu16: int = int(utils.map(statuOff_dutyRatio, 0.0, 1.0, 0.0, 65535.0))
  def on(self) -> None:
    self.pin_pwm.duty_u16(self.statuOn_dutyu16)
  def off(self) -> None:
    self.pin_pwm.duty_u16(self.statuOff_dutyu16)
  def set(self, value: float) -> None:
    self.pin_pwm.duty_u16(int(utils.map(value, 0, 1, self.statuOff_dutyu16, self.statuOn_dutyu16)))
  def toggle(self) -> None:
    self.pin_pwm.duty_u16(int(utils.map(self.pin_pwm.duty_u16(), self.statuOn_dutyu16, self.statuOff_dutyu16, self.statuOff_dutyu16, self.statuOn_dutyu16)))

class RGB:
  def __init__(self, r: int, g: int, b: int) -> None:
    self.set(r, g, b)
  def set(self, r: int, g: int, b: int) -> None:
    if 0 <= r <= 255 and 0 <= g <= 255 and 0 <= b <= 255:
      self.r, self.g, self.b = r, g, b
    else:
      raise Exception("r, g, b must be 0 <= r <= 255 and 0 <= g <= 255 and 0 <= b <= 255")
  def get(self) -> tuple[int, int, int]:
    return self.r, self.g, self.b
  def __str__(self) -> str:
    return f"RGB({self.r}, {self.g}, {self.b})"

class RGBA:
  def __init__(self, r: int, g: int, b: int, a: int = 255) -> None:
    self.set(r, g, b, a)
  def set(self, r: int, g: int, b: int, a: int = 255) -> None:
    if 0 <= r <= 255 and 0 <= g <= 255 and 0 <= b <= 255 and 0 <= a <= 255:
      self.r, self.g, self.b, self.a = r, g, b, a
    else:
      raise Exception("r, g, b, a must be 0 <= r <= 255 and 0 <= g <= 255 and 0 <= b <= 255 and 0 <= a <= 255")
  def get(self) -> tuple[int, int, int, int]:
    return self.r, self.g, self.b, self.a
  def __str__(self) -> str:
    return f"RGBA({self.r}, {self.g}, {self.b}, {self.a})"

class RGBLED:
  def __init__(self, pinR: PWMLED, pinG: PWMLED, pinB: PWMLED, pinAlpha: PWMLED | None = None) -> None:
    self.pinR: PWMLED = pinR
    self.pinG: PWMLED = pinG
    self.pinB: PWMLED = pinB
    self.pinAlpha: PWMLED | None = pinAlpha
  def set_ratio(self, r: float, g: float, b: float, a: float = 1.0) -> None:
    if 0.0 <= r <= 1.0 and 0.0 <= g <= 1.0 and 0.0 <= b <= 1.0 and 0.0 <= a <= 1.0:
      self.pinR.set(r)
      self.pinG.set(g)
      self.pinB.set(b)
      if self.pinAlpha is not None:
        self.pinAlpha.set(a)
    else:
      raise Exception("r, g, b, a must be 0.0 <= r <= 1.0 and 0.0 <= g <= 1.0 and 0.0 <= b <= 1.0 and 0.0 <= a <= 1.0")
  def set_color(self, r: int, g: int, b: int, a: int = 255) -> None:
    if 0 <= r <= 255 and 0 <= g <= 255 and 0 <= b <= 255 and 0 <= a <= 255:
      self.set_ratio(r / 255.0, g / 255.0, b / 255.0, a / 255.0)
    else:
      raise Exception("r, g, b, a must be 0 <= r <= 255 and 0 <= g <= 255 and 0 <= b <= 255 and 0 <= a <= 255")
  def set_RGBA(self, rgba: RGBA) -> None:
    self.set_color(rgba.r, rgba.g, rgba.b, rgba.a)

class RGBLEDPixels:
  def __init__(self, pin: machine.Pin, size: int, bpp: int = 3, timing: int = 1, pixels: list[RGB] | None = None) -> None:
    self.pin: machine.Pin = pin
    self.size: int = size
    self.neopixel: neopixel.NeoPixel = neopixel.NeoPixel(pin, size, bpp=bpp, timing=timing)
    self.pixels: list[RGB] = [RGB(0, 0, 0) for _ in range(size)]
    if pixels is not None:
      self.set(pixels)
  def set(self, pixels: list[RGB]) -> None:
    del self.pixels
    for i in range(self.size):
      self.neopixel[i] = pixels[i].get()
    self.neopixel.write()
    self.pixels: list[RGB] = pixels
  def get(self) -> list[RGB]:
    return self.pixels

if __name__ == "__main__":
  # try:
  #   pwmled: PWMLED = PWMLED(machine.Pin(16))
  #   pwmled.on()
  #   utime.sleep(0.5)
  #   pwmled.off()
  #   utime.sleep(0.5)
  #   pwmled.toggle()
  #   utime.sleep(0.5)
  #   while True:
  #     for i in range(1000):
  #       pwmled.set(0.001 * i)
  #       utime.sleep(0.001)
  # except KeyboardInterrupt as e:
  #   pass

  try:
    print("[__main__] Testing RGBLED class with thread mode, Press Ctrl+C to stop the program.")
    import urandom
    rgbled: RGBLED = RGBLED(
      PWMLED(machine.Pin(18)),
      PWMLED(machine.Pin(17)),
      PWMLED(machine.Pin(16)),
      PWMLED(machine.Pin(15))
    )
    r_init, g_init, b_init, alpha = urandom.randint(0, 255), urandom.randint(0, 255), urandom.randint(0, 255), 0
    rgbled.set_color(r_init, g_init, b_init, alpha)
    while True:
      print(f"RGBA: ({r_init:03d}, {g_init:03d}, {b_init:03d}, {alpha:03d})")
      r_target, g_target, b_target= urandom.randint(0, 255), urandom.randint(0, 255), urandom.randint(0, 255)
      rounds: int = urandom.randint(300, 600)
      for i in range(rounds):
        r_tmp = utils.map(i, 0, rounds, r_init, r_target)
        g_tmp = utils.map(i, 0, rounds, g_init, g_target)
        b_tmp = utils.map(i, 0, rounds, b_init, b_target)
        rgbled.set_color(
          int(utils.map(i, 0, rounds, r_init, r_target)), 
          int(utils.map(i, 0, rounds, g_init, g_target)), 
          int(utils.map(i, 0, rounds, b_init, b_target)), 
          alpha
        )
        utime.sleep_ms(1)
      r_init, g_init, b_init = r_target, g_target, b_target
  except KeyboardInterrupt as e:
    print("[__main__] KeyboardInterrupt")
    pass

  # try: 
  #   import urandom
  #   import machine
  #   from neopixel import NeoPixel
  #   np: NeoPixel = NeoPixel(machine.Pin(48, machine.Pin.OUT), 1)
  #   while True:
  #     np[0] = (urandom.randint(0, 255), urandom.randint(0, 255), urandom.randint(0, 255))
  #     np.write()
  #     utime.sleep(0.1)
  # except KeyboardInterrupt as e:
  #   pass

  try:
    print("[__main__] Testing RGBLEDPixels class with thread mode, Press Ctrl+C to stop the program.")
    import urandom
    size: int = 1
    rgbLedPixels: RGBLEDPixels = RGBLEDPixels(machine.Pin(48, machine.Pin.OUT), size, pixels=[RGB(urandom.randint(0, 255), urandom.randint(0, 255), urandom.randint(0, 255)) for _ in range(size)])
    while True:
      print(f"RGB: ({rgbLedPixels.get()[0].r:03d}, {rgbLedPixels.get()[0].g:03d}, {rgbLedPixels.get()[0].b:03d})")
      old_pixels: list[RGB] = rgbLedPixels.get()
      new_pixels: list[RGB] = [RGB(urandom.randint(0, 255), urandom.randint(0, 255), urandom.randint(0, 255)) for _ in range(size)]
      rounds: int = urandom.randint(300, 600)
      for i in range(rounds):
        tmp_pixels: list[RGB] = []
        for j in range(size):
          r_tmp = utils.map(i, 0, rounds, old_pixels[j].r, new_pixels[j].r)
          g_tmp = utils.map(i, 0, rounds, old_pixels[j].g, new_pixels[j].g)
          b_tmp = utils.map(i, 0, rounds, old_pixels[j].b, new_pixels[j].b)
          tmp_pixels.append(RGB(int(r_tmp), int(g_tmp), int(b_tmp)))
        rgbLedPixels.set(tmp_pixels)
        utime.sleep_ms(1)
  except KeyboardInterrupt as e:
    print("[__main__] KeyboardInterrupt")
    pass
