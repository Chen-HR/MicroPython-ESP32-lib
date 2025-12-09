# file: micropython_esp32_lib/Device/Speaker.py

"""
# file: ./Device/Speaker.py
"""

import utime
import machine

try: 
  from ..System.Time import Sleep
  from ..Utils import Utils
except ImportError:
  from micropython_esp32_lib.System.Time import Sleep
  from micropython_esp32_lib.Utils import Utils

class Temperament:
  def __init__(self, freq: float):
    self.freq = freq
  QUIET: "Temperament"
Temperament.QUIET = Temperament(0.0)

class Equal(Temperament):
  RATIO: float = 2**(1/12)
  A4_REF_FREQ = 440.0
  @classmethod
  def calculate_frequency(cls, ref_freq: float, n: int) -> float:
    return ref_freq * pow(cls.RATIO, n)
  # ... (Omitted for brevity, content remains the same)
  # --- C3 OCTAVE (n = -21 to -10) ---
  C3: "Equal"
  CS3: "Equal"
  DB3: "Equal"
  D3: "Equal"
  DS3: "Equal"
  EB3: "Equal"
  E3: "Equal"
  F3: "Equal"
  FS3: "Equal"
  GB3: "Equal"
  G3: "Equal"
  GS3: "Equal"
  AB3: "Equal"
  A3: "Equal"
  AS3: "Equal"
  BB3: "Equal"
  B3: "Equal"

  # --- C4 OCTAVE (n = -9 to 2) ---
  C4: "Equal"
  CS4: "Equal"
  DB4: "Equal"
  D4: "Equal"
  DS4: "Equal"
  EB4: "Equal"
  E4: "Equal"
  F4: "Equal"
  FS4: "Equal"
  GB4: "Equal"
  G4: "Equal"
  GS4: "Equal"
  AB4: "Equal"
  A4: "Equal"
  AS4: "Equal"
  BB4: "Equal"
  B4: "Equal"
  
  # --- C5 OCTAVE (n = 3 to 14) ---
  C5: "Equal"
  CS5: "Equal"
  DB5: "Equal"
  D5: "Equal"
  DS5: "Equal"
  EB5: "Equal"
  E5: "Equal"
  F5: "Equal"
  FS5: "Equal"
  GB5: "Equal"
  G5: "Equal"
  GS5: "Equal"
  AB5: "Equal"
  A5: "Equal"
  AS5: "Equal"
  BB5: "Equal"
  B5: "Equal"

Equal.C3 = Equal(Equal.calculate_frequency(Equal.A4_REF_FREQ, -21)) # ~= 130.81 Hz
Equal.CS3 = Equal(Equal.calculate_frequency(Equal.A4_REF_FREQ, -20))# ~= 138.59 Hz
Equal.DB3 = Equal.CS3
Equal.D3 = Equal(Equal.calculate_frequency(Equal.A4_REF_FREQ, -19)) # ~= 146.83 Hz
Equal.DS3 = Equal(Equal.calculate_frequency(Equal.A4_REF_FREQ, -18))# ~= 155.56 Hz
Equal.EB3 = Equal.DS3
Equal.E3 = Equal(Equal.calculate_frequency(Equal.A4_REF_FREQ, -17)) # ~= 164.81 Hz
Equal.F3 = Equal(Equal.calculate_frequency(Equal.A4_REF_FREQ, -16)) # ~= 174.61 Hz
Equal.FS3 = Equal(Equal.calculate_frequency(Equal.A4_REF_FREQ, -15))# ~= 184.99 Hz
Equal.GB3 = Equal.FS3
Equal.G3 = Equal(Equal.calculate_frequency(Equal.A4_REF_FREQ, -14)) # ~= 196.00 Hz
Equal.GS3 = Equal(Equal.calculate_frequency(Equal.A4_REF_FREQ, -13))# ~= 207.65 Hz
Equal.AB3 = Equal.GS3
Equal.A3 = Equal(Equal.calculate_frequency(Equal.A4_REF_FREQ, -12)) # ~= 220.00 Hz
Equal.AS3 = Equal(Equal.calculate_frequency(Equal.A4_REF_FREQ, -11))# ~= 233.08 Hz
Equal.BB3 = Equal.AS3
Equal.B3 = Equal(Equal.calculate_frequency(Equal.A4_REF_FREQ, -10)) # ~= 246.94 Hz
Equal.C4 = Equal(Equal.calculate_frequency(Equal.A4_REF_FREQ, -9))  # ~= 261.63 Hz
Equal.CS4 = Equal(Equal.calculate_frequency(Equal.A4_REF_FREQ, -8)) # ~= 277.18 Hz
Equal.DB4 = Equal.CS4
Equal.D4 = Equal(Equal.calculate_frequency(Equal.A4_REF_FREQ, -7))  # ~= 293.66 Hz
Equal.DS4 = Equal(Equal.calculate_frequency(Equal.A4_REF_FREQ, -6)) # ~= 311.13 Hz
Equal.EB4 = Equal.DS4
Equal.E4 = Equal(Equal.calculate_frequency(Equal.A4_REF_FREQ, -5))  # ~= 329.63 Hz
Equal.F4 = Equal(Equal.calculate_frequency(Equal.A4_REF_FREQ, -4))  # ~= 349.23 Hz
Equal.FS4 = Equal(Equal.calculate_frequency(Equal.A4_REF_FREQ, -3)) # ~= 369.99 Hz
Equal.GB4 = Equal.FS4
Equal.G4 = Equal(Equal.calculate_frequency(Equal.A4_REF_FREQ, -2))  # ~= 392.00 Hz
Equal.GS4 = Equal(Equal.calculate_frequency(Equal.A4_REF_FREQ, -1)) # ~= 415.30 Hz
Equal.AB4 = Equal.GS4
Equal.A4 = Equal(Equal.calculate_frequency(Equal.A4_REF_FREQ, 0))   #  = 440.00 Hz
Equal.AS4 = Equal(Equal.calculate_frequency(Equal.A4_REF_FREQ, 1))  # ~= 466.16 Hz
Equal.BB4 = Equal.AS4
Equal.B4 = Equal(Equal.calculate_frequency(Equal.A4_REF_FREQ, 2))   # ~= 493.88 Hz
Equal.C5 = Equal(Equal.calculate_frequency(Equal.A4_REF_FREQ, 3))   # ~= 523.25 Hz
Equal.CS5 = Equal(Equal.calculate_frequency(Equal.A4_REF_FREQ, 4))  # ~= 554.37 Hz
Equal.DB5 = Equal.CS5
Equal.D5 = Equal(Equal.calculate_frequency(Equal.A4_REF_FREQ, 5))   # ~= 587.33 Hz
Equal.DS5 = Equal(Equal.calculate_frequency(Equal.A4_REF_FREQ, 6))  # ~= 622.25 Hz
Equal.EB5 = Equal.DS5
Equal.E5 = Equal(Equal.calculate_frequency(Equal.A4_REF_FREQ, 7))   # ~= 659.26 Hz
Equal.F5 = Equal(Equal.calculate_frequency(Equal.A4_REF_FREQ, 8))   # ~= 698.46 Hz
Equal.FS5 = Equal(Equal.calculate_frequency(Equal.A4_REF_FREQ, 9))  # ~= 739.99 Hz
Equal.GB5 = Equal.FS5
Equal.G5 = Equal(Equal.calculate_frequency(Equal.A4_REF_FREQ, 10))  # ~= 783.99 Hz
Equal.GS5 = Equal(Equal.calculate_frequency(Equal.A4_REF_FREQ, 11)) # ~= 830.61 Hz
Equal.AB5 = Equal.GS5
Equal.A5 = Equal(Equal.calculate_frequency(Equal.A4_REF_FREQ, 12))  # ~= 880.00 Hz
Equal.AS5 = Equal(Equal.calculate_frequency(Equal.A4_REF_FREQ, 13)) # ~= 932.33 Hz
Equal.BB5 = Equal.AS5
Equal.B5 = Equal(Equal.calculate_frequency(Equal.A4_REF_FREQ, 14))  # ~= 987.77 Hz

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
    # Initialize PWM with a default valid frequency
    self.main = machine.PWM(pin, freq=1000, duty_u16=0)
    self.quiet()

  def set(self, noteEvent: NoteEvent) -> None:
    if noteEvent.pitch.freq > 0:
      self.main.freq(int(noteEvent.pitch.freq))
      self.main.duty_u16(int(Utils.UINT16_MAX * noteEvent.amplitude))
    else:
      # For quiet notes, just set duty to 0, don't change frequency
      self.main.duty_u16(0)
    
    # The original implementation of `set` was blocking. 
    # For async operation, the sleep should be handled by the caller.
    # Sleep.sync_ms(noteEvent.duration_ms)

  def quiet(self) -> None:
    # Quiet the speaker by setting duty cycle to 0, not by setting freq to 0.
    self.main.duty_u16(0)
    
  def play(self, noteEvents: list[NoteEvent]):
    for noteEvent in noteEvents:
      self.set(noteEvent)
      # This part is blocking and should be used with caution in async code
      Sleep.sync_ms(noteEvent.duration_ms)
      
  def __del__(self):
    self.quiet()
    self.main.deinit()