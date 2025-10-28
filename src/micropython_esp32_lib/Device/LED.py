# src/micropython_esp32_lib/Device/LED.py
import machine
import neopixel # For RGBLEDPixels
import urandom # For testing only

try:
  from ..System import Utils
  from ..System import Logging
  from ..System import Sleep # For utime.sleep_ms and utime.sleep in main block
except ImportError:
  from micropython_esp32_lib.System import Utils
  from micropython_esp32_lib.System import Logging
  from micropython_esp32_lib.System import Sleep

class PWMLED:
  def __init__(self, pin: machine.Pin, statuOn_dutyRatio: float = 1.0, statuOff_dutyRatio: float = 0.0, frequency_Hz: int = 256) -> None:
    self.pin_pwm: machine.PWM = machine.PWM(pin, freq=frequency_Hz)
    self.statuOn_dutyu16: int = int(Utils.map(statuOn_dutyRatio, 0.0, 1.0, 0.0, Utils.UINT16_MAX))
    self.statuOff_dutyu16: int = int(Utils.map(statuOff_dutyRatio, 0.0, 1.0, 0.0, Utils.UINT16_MAX))
    # No logger added here, as it's a very low-level component, and logging might be too verbose.
    # Higher-level components can log their usage of PWMLED.
  def on(self) -> None:
    self.pin_pwm.duty_u16(self.statuOn_dutyu16)
  def off(self) -> None:
    self.pin_pwm.duty_u16(self.statuOff_dutyu16)
  def set(self, value: float) -> None:
    # Map 'value' from 0-1 to the range defined by statuOff_dutyu16 to statuOn_dutyu16
    self.pin_pwm.duty_u16(int(Utils.map(value, 0, 1, self.statuOff_dutyu16, self.statuOn_dutyu16)))
  def toggle(self) -> None:
    current_duty = self.pin_pwm.duty_u16()
    if current_duty == self.statuOn_dutyu16:
      self.off()
    else:
      self.on()

class RGB:
  def __init__(self, r: int, g: int, b: int) -> None:
    self.set(r, g, b)
  def set(self, r: int, g: int, b: int) -> None:
    if 0 <= r <= Utils.UINT08_MAX and 0 <= g <= Utils.UINT08_MAX and 0 <= b <= Utils.UINT08_MAX: # Using Utils.UINT08_MAX
      self.r, self.g, self.b = r, g, b
    else:
      raise ValueError("r, g, b must be 0 <= value <= 255") # Changed Exception to ValueError
  def get(self) -> tuple[int, int, int]:
    return self.r, self.g, self.b
  def __str__(self) -> str:
    return f"RGB({self.r}, {self.g}, {self.b})"

class RGBA:
  def __init__(self, r: int, g: int, b: int, a: int = Utils.UINT08_MAX) -> None: # Using Utils.UINT08_MAX
    self.set(r, g, b, a)
  def set(self, r: int, g: int, b: int, a: int = Utils.UINT08_MAX) -> None: # Using Utils.UINT08_MAX
    if 0 <= r <= Utils.UINT08_MAX and 0 <= g <= Utils.UINT08_MAX and 0 <= b <= Utils.UINT08_MAX and 0 <= a <= Utils.UINT08_MAX:
      self.r, self.g, self.b, self.a = r, g, b, a
    else:
      raise ValueError("r, g, b, a must be 0 <= value <= 255") # Changed Exception to ValueError
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
      raise ValueError("r, g, b, a must be 0.0 <= value <= 1.0")
  def set_color(self, r: int, g: int, b: int, a: int = Utils.UINT08_MAX) -> None: # Using Utils.UINT08_MAX
    if 0 <= r <= Utils.UINT08_MAX and 0 <= g <= Utils.UINT08_MAX and 0 <= b <= Utils.UINT08_MAX and 0 <= a <= Utils.UINT08_MAX:
      self.set_ratio(r / Utils.UINT08_MAX, g / Utils.UINT08_MAX, b / Utils.UINT08_MAX, a / Utils.UINT08_MAX)
    else:
      raise ValueError("r, g, b, a must be 0 <= value <= 255")
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
    # Ensure the new list has the correct size
    if len(pixels) != self.size:
        raise ValueError(f"Expected {self.size} pixels, but got {len(pixels)}")
    self.pixels = pixels # Update internal reference first
    for i in range(self.size):
      self.neopixel[i] = self.pixels[i].get() # Use self.pixels[i] directly
    self.neopixel.write()
  def get(self) -> list[RGB]:
    # It's better to return a copy if the user might modify it and expect no change to internal state without calling set.
    return [RGB(p.r, p.g, p.b) for p in self.pixels] # Return a copy of RGB objects

if __name__ == "__main__":
  logger_main = Logging.Log("LED_Test", Logging.LEVEL.INFO)
  
  # Test 1: PWMLED
  logger_main.info("Testing PWMLED class.")
  pwmled: PWMLED = PWMLED(machine.Pin(16, machine.Pin.OUT)) # Specify Pin.OUT
  try:
    pwmled.on()
    Sleep.sync_s(0.5)
    pwmled.off()
    Sleep.sync_s(0.5)
    pwmled.toggle()
    Sleep.sync_s(0.5)
    logger_main.info("Fading in/out LED...")
    for i in range(1001):
      pwmled.set(i / 1000.0)
      Sleep.sync_ms(1)
    for i in range(1001):
      pwmled.set(1.0 - (i / 1000.0))
      Sleep.sync_ms(1)
    pwmled.off() # Ensure it's off after test
  except KeyboardInterrupt:
    logger_main.info("PWMLED test interrupted.")
  except Exception as e:
    logger_main.error(f"PWMLED test failed: {e}")
  finally:
    try: # Ensure PWM resource is deinitialized
        pwmled.pin_pwm.deinit()
    except AttributeError:
        pass # pwmled might not have been fully initialized

  logger_main.info("\n" + "="*50)
  # Test 2: RGBLED (Common Anode/Cathode) - assuming common anode for simplicity (lower duty = brighter)
  # For ESP32, you often specify the pin mode explicitly, e.g., machine.Pin(PIN, machine.Pin.OUT)
  logger_main.info("Testing RGBLED class.")
  rgbled_pins = {
    'R': machine.Pin(18, machine.Pin.OUT),
    'G': machine.Pin(17, machine.Pin.OUT),
    'B': machine.Pin(16, machine.Pin.OUT),
    'A': machine.Pin(15, machine.Pin.OUT) # Assuming an alpha/brightness control pin
  }
  # Assuming Common Anode for PWMLED where duty 0 is brightest, 65535 is off
  # Adjust statuOn_dutyRatio/statuOff_dutyRatio based on whether it's common anode or cathode.
  # For common cathode, 1.0 (65535) is brightest, 0.0 (0) is off. The current Utils.map is for common cathode.
  # If common anode, invert the duty ratios for PWMLED.
  # For this example, let's assume common cathode for simplicity, as the map function expects 0-1 brightness mapping to 0-65535 duty.
  rgbled: RGBLED = RGBLED(
    PWMLED(rgbled_pins['R']),
    PWMLED(rgbled_pins['G']),
    PWMLED(rgbled_pins['B']),
    PWMLED(rgbled_pins['A'])
  )
  try:
    
    r_init, g_init, b_init = urandom.randint(0, Utils.UINT08_MAX), urandom.randint(0, Utils.UINT08_MAX), urandom.randint(0, Utils.UINT08_MAX)
    alpha = urandom.randint(100, Utils.UINT08_MAX) # Initial alpha for test
    rgbled.set_color(r_init, g_init, b_init, alpha)
    logger_main.info(f"Initial RGBA: ({r_init:03d}, {g_init:03d}, {b_init:03d}, {alpha:03d})")

    while True:
      r_target, g_target, b_target = urandom.randint(0, Utils.UINT08_MAX), urandom.randint(0, Utils.UINT08_MAX), urandom.randint(0, Utils.UINT08_MAX)
      alpha_target = urandom.randint(100, Utils.UINT08_MAX)
      rounds: int = urandom.randint(300, 600)
      
      logger_main.info(f"Fading to RGBA: ({r_target:03d}, {g_target:03d}, {b_target:03d}, {alpha_target:03d}) over {rounds} steps.")
      
      for i in range(rounds):
        r_tmp = Utils.map(i, 0, rounds, r_init, r_target)
        g_tmp = Utils.map(i, 0, rounds, g_init, g_target)
        b_tmp = Utils.map(i, 0, rounds, b_init, b_target)
        a_tmp = Utils.map(i, 0, rounds, alpha, alpha_target)
        rgbled.set_color(int(r_tmp), int(g_tmp), int(b_tmp), int(a_tmp))
        Sleep.sync_ms(1)
      
      r_init, g_init, b_init, alpha = r_target, g_target, b_target, alpha_target
      Sleep.sync_ms(500) # Short pause before next fade
  except KeyboardInterrupt:
    logger_main.info("RGBLED test interrupted.")
  except Exception as e:
    logger_main.error(f"RGBLED test failed: {e}")
  finally:
    rgbled.set_color(0, 0, 0, 0) # Turn off LED
    # Deinitialize PWM pins
    for pin_obj in rgbled_pins.values():
        try:
            machine.PWM(pin_obj).deinit() # Re-initialize to deinit, safe way
        except (TypeError, ValueError, AttributeError): # Added AttributeError
            pass # Pin might not be a PWM pin or already deinit'd
    logger_main.info("RGBLED test ended.")

  logger_main.info("\n" + "="*50)
  # Test 3: RGBLEDPixels (NeoPixel/WS2812B)
  logger_main.info("Testing RGBLEDPixels class.")
  size: int = 4 # Number of pixels
  # Ensure pin is configured for output when creating NeoPixel instance
  neopixel_pin = machine.Pin(48, machine.Pin.OUT) 
  rgbLedPixels: RGBLEDPixels = RGBLEDPixels(neopixel_pin, size, pixels=[RGB(urandom.randint(0, Utils.UINT08_MAX), urandom.randint(0, Utils.UINT08_MAX), urandom.randint(0, Utils.UINT08_MAX)) for _ in range(size)])
  logger_main.info(f"Initial NeoPixel RGB values: {[p.get() for p in rgbLedPixels.get()]}")
  try:

    while True:
      old_pixels: list[RGB] = rgbLedPixels.get()
      new_pixels: list[RGB] = [RGB(urandom.randint(0, Utils.UINT08_MAX), urandom.randint(0, Utils.UINT08_MAX), urandom.randint(0, Utils.UINT08_MAX)) for _ in range(size)]
      rounds: int = urandom.randint(300, 600)
      
      logger_main.info(f"Fading NeoPixels to new colors over {rounds} steps.")
      
      tmp_pixels_list: list[RGB] = []
      for i in range(rounds):
        tmp_pixels_list.clear() # Clear for new frame
        for j in range(size):
          r_tmp = Utils.map(i, 0, rounds, old_pixels[j].r, new_pixels[j].r)
          g_tmp = Utils.map(i, 0, rounds, old_pixels[j].g, new_pixels[j].g)
          b_tmp = Utils.map(i, 0, rounds, old_pixels[j].b, new_pixels[j].b)
          tmp_pixels_list.append(RGB(int(r_tmp), int(g_tmp), int(b_tmp)))
        rgbLedPixels.set(tmp_pixels_list)
        Sleep.sync_ms(1)
      
      logger_main.info(f"Current NeoPixel RGB values: {[p.get() for p in rgbLedPixels.get()]}")
      Sleep.sync_ms(500) # Short pause before next fade
  except KeyboardInterrupt:
    logger_main.info("RGBLEDPixels test interrupted.")
  except Exception as e:
    logger_main.error(f"RGBLEDPixels test failed: {e}")
  finally:
    # Clear NeoPixels
    try:
        rgbLedPixels.set([RGB(0,0,0) for _ in range(size)])
    except UnboundLocalError: # If rgbLedPixels was never initialized
        pass
    logger_main.info("RGBLEDPixels test ended.")