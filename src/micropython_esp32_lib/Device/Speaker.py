"""
# file: ./Device/Speaker.py
"""

import utime
import machine

try: 
  from ..System import Digital
  from ..System import Sleep
  from ..Utils import Utils
except ImportError:
  import micropython_esp32_lib.System.Digital as Digital
  import micropython_esp32_lib.System.Sleep as Sleep
  import micropython_esp32_lib.Utils.Utils as Utils

class Temperament:
  def __init__(self, freq: float):
    self.freq = freq
class TEMPERAMENT:
  QUIET = Temperament(0.0)

class Equal(Temperament):
  RATIO: float = 2**(1/12)
  A4_REF_FREQ = 440.0
  @classmethod
  def calculate_frequency(cls, ref_freq: float, n: int) -> float:
    return ref_freq * pow(cls.RATIO, n)
class EQUAL:
  # --- C3 OCTAVE (n = -21 to -10) ---
  C3 = Equal(Equal.calculate_frequency(Equal.A4_REF_FREQ, -21)) # ~= 130.81 Hz
  CS3 = Equal(Equal.calculate_frequency(Equal.A4_REF_FREQ, -20))# ~= 138.59 Hz
  DB3 = CS3
  D3 = Equal(Equal.calculate_frequency(Equal.A4_REF_FREQ, -19)) # ~= 146.83 Hz
  DS3 = Equal(Equal.calculate_frequency(Equal.A4_REF_FREQ, -18))# ~= 155.56 Hz
  EB3 = DS3
  E3 = Equal(Equal.calculate_frequency(Equal.A4_REF_FREQ, -17)) # ~= 164.81 Hz
  F3 = Equal(Equal.calculate_frequency(Equal.A4_REF_FREQ, -16)) # ~= 174.61 Hz
  FS3 = Equal(Equal.calculate_frequency(Equal.A4_REF_FREQ, -15))# ~= 184.99 Hz
  GB3 = FS3
  G3 = Equal(Equal.calculate_frequency(Equal.A4_REF_FREQ, -14)) # ~= 196.00 Hz
  GS3 = Equal(Equal.calculate_frequency(Equal.A4_REF_FREQ, -13))# ~= 207.65 Hz
  AB3 = GS3
  A3 = Equal(Equal.calculate_frequency(Equal.A4_REF_FREQ, -12)) # ~= 220.00 Hz
  AS3 = Equal(Equal.calculate_frequency(Equal.A4_REF_FREQ, -11))# ~= 233.08 Hz
  BB3 = AS3
  B3 = Equal(Equal.calculate_frequency(Equal.A4_REF_FREQ, -10)) # ~= 246.94 Hz

  # --- C4 OCTAVE (n = -9 to 2) ---
  C4 = Equal(Equal.calculate_frequency(Equal.A4_REF_FREQ, -9))  # ~= 261.63 Hz
  CS4 = Equal(Equal.calculate_frequency(Equal.A4_REF_FREQ, -8)) # ~= 277.18 Hz
  DB4 = CS4
  D4 = Equal(Equal.calculate_frequency(Equal.A4_REF_FREQ, -7))  # ~= 293.66 Hz
  DS4 = Equal(Equal.calculate_frequency(Equal.A4_REF_FREQ, -6)) # ~= 311.13 Hz
  EB4 = DS4
  E4 = Equal(Equal.calculate_frequency(Equal.A4_REF_FREQ, -5))  # ~= 329.63 Hz
  F4 = Equal(Equal.calculate_frequency(Equal.A4_REF_FREQ, -4))  # ~= 349.23 Hz
  FS4 = Equal(Equal.calculate_frequency(Equal.A4_REF_FREQ, -3)) # ~= 369.99 Hz
  GB4 = FS4
  G4 = Equal(Equal.calculate_frequency(Equal.A4_REF_FREQ, -2))  # ~= 392.00 Hz
  GS4 = Equal(Equal.calculate_frequency(Equal.A4_REF_FREQ, -1)) # ~= 415.30 Hz
  AB4 = GS4
  A4 = Equal(Equal.calculate_frequency(Equal.A4_REF_FREQ, 0))   #  = 440.00 Hz
  AS4 = Equal(Equal.calculate_frequency(Equal.A4_REF_FREQ, 1))  # ~= 466.16 Hz
  BB4 = AS4
  B4 = Equal(Equal.calculate_frequency(Equal.A4_REF_FREQ, 2))   # ~= 493.88 Hz
  
  # --- C5 OCTAVE (n = 3 to 14) ---
  C5 = Equal(Equal.calculate_frequency(Equal.A4_REF_FREQ, 3))   # ~= 523.25 Hz
  CS5 = Equal(Equal.calculate_frequency(Equal.A4_REF_FREQ, 4))  # ~= 554.37 Hz
  DB5 = CS5
  D5 = Equal(Equal.calculate_frequency(Equal.A4_REF_FREQ, 5))   # ~= 587.33 Hz
  DS5 = Equal(Equal.calculate_frequency(Equal.A4_REF_FREQ, 6))  # ~= 622.25 Hz
  EB5 = DS5
  E5 = Equal(Equal.calculate_frequency(Equal.A4_REF_FREQ, 7))   # ~= 659.26 Hz
  F5 = Equal(Equal.calculate_frequency(Equal.A4_REF_FREQ, 8))   # ~= 698.46 Hz
  FS5 = Equal(Equal.calculate_frequency(Equal.A4_REF_FREQ, 9))  # ~= 739.99 Hz
  GB5 = FS5
  G5 = Equal(Equal.calculate_frequency(Equal.A4_REF_FREQ, 10))  # ~= 783.99 Hz
  GS5 = Equal(Equal.calculate_frequency(Equal.A4_REF_FREQ, 11)) # ~= 830.61 Hz
  AB5 = GS5
  A5 = Equal(Equal.calculate_frequency(Equal.A4_REF_FREQ, 12))  # ~= 880.00 Hz
  AS5 = Equal(Equal.calculate_frequency(Equal.A4_REF_FREQ, 13)) # ~= 932.33 Hz
  BB5 = AS5
  B5 = Equal(Equal.calculate_frequency(Equal.A4_REF_FREQ, 14))  # ~= 987.77 Hz

# class Twelve(Enum.Unit):
#   ...
# class TWELVE(Twelve): # G, S, J, Z, Y
#   ...


class NoteEvent:
  def __init__(self, pitch: Temperament, amplitude: float, duration_ms: int):
    self.pitch = pitch
    if amplitude < 0.0: amplitude = 0.0
    elif amplitude > 1.0: amplitude = 1.0
    self.amplitude = amplitude
    self.duration_ms = duration_ms

class Speaker:
  def __init__(self, pin: machine.Pin):
    self.main = machine.PWM(machine.Pin(pin, Digital.MODE.OUT.value))
    self.quiet()
  def set(self, noteEvent: NoteEvent) -> None:
    self.main.duty_u16(int(Utils.UINT16_MAX*noteEvent.amplitude))
    self.main.freq(int(noteEvent.pitch.freq))
    Sleep.sync_ms(noteEvent.duration_ms)
  def quiet(self) -> None:
    self.set(NoteEvent(TEMPERAMENT.QUIET, 0.0, 0))
  def play(self, noteEvents: list[NoteEvent]):
    for noteEvent in noteEvents:
      self.set(noteEvent)
  def __del__(self):
    self.quiet()
    self.main.deinit()