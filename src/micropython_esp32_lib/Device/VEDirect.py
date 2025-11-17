"""
# file: ./Network/VEDirect.py
- ref: [VictronVEDirectArduino](https://github.com/winginitau/VictronVEDirectArduino), [VeDirectFrameHandler](https://github.com/giacinti/VeDirectFrameHandler), [Victron.Arduino-ESP8266](https://github.com/physee/Victron.Arduino-ESP8266)
"""

import machine
import asyncio

try:
  # Relative imports for the provided project structure
  from ..System import Time
  from ..System import Sleep
  from ..Utils import Logging
  from ..Utils import Utils
except ImportError:
  # Fallback imports for external use
  from micropython_esp32_lib.System import Time
  from micropython_esp32_lib.System import Sleep
  from micropython_esp32_lib.Utils import Logging
  from micropython_esp32_lib.Utils import Utils

# --- Protocol Constants (Derived from VE.DirectFrameHandler.h/cpp) ---
class States:
    """State machine states for the VE.Direct text protocol parser."""
    IDLE = 0
    RECORD_BEGIN = 1
    RECORD_NAME = 2
    RECORD_VALUE = 3
    CHECKSUM = 4
    RECORD_HEX = 5 # Hex frames are not fully supported in this version

CHECKSUM_TAG = "Checksum"
BAUDRATE = 19200

class VEDirectConnector:
  """
  An asynchronous connector to read data from Victron Energy devices
  using the text-based VE.Direct protocol over UART.

  It implements the state machine logic from the official VE.Direct Frame Handler
  to ensure correct frame parsing and checksum validation in a non-blocking way.
  """
  def __init__(self, uart_id: int, baudrate: int = BAUDRATE, 
               tx_pin: int | None = None, rx_pin: int | None = None,
               log_name: str = "VEDirectConnector", log_level: Logging.Level = Logging.LEVEL.INFO):
    """
    Initializes the VE.Direct Connector.

    Args:
      uart_id (int): The ID of the UART peripheral (e.g., 0, 1, 2).
      baudrate (int): The baud rate for the VE.Direct protocol (default: 19200).
      tx_pin (int | None): The TX pin number for the UART.
      rx_pin (int | None): The RX pin number for the UART.
    
    Raises:
      Exception: If UART initialization fails.
    """
    self.logger: Logging.Log = Logging.Log(log_name, log_level)
    self.active: bool = False
    self._read_task: asyncio.Task | None = None
    
    # Internal Protocol State
    self._state: int = States.IDLE
    self._checksum: int = 0
    self._current_name: str = ""
    self._current_value: str = ""
    self._temp_frame_data: dict[str, str] = {} # Buffer for the current frame
    self._pushed_state: int = States.IDLE
    self.data: dict[str, str] = {} # Public storage for the last valid frame

    self.uart_baudrate = baudrate

    try:
      # Use machine.UART with the specified pins. UART must be initialized correctly.
      if tx_pin is not None and rx_pin is not None:
        self.uart = machine.UART(uart_id, baudrate=baudrate, tx=tx_pin, rx=rx_pin)
      else:
        # Rely on default pins for the given ID if not specified
        self.uart = machine.UART(uart_id, baudrate=baudrate)
        
      # Set a low timeout for non-blocking read polling (machine.UART.any() is preferred, but timeout ensures low latency read)
      self.uart.init(baudrate=baudrate, timeout=10) 
      self.logger.info(f"UART{uart_id} initialized at {baudrate} baud.")
    except Exception as e:
      self.logger.error(f"Failed to initialize UART{uart_id}: {e}")
      raise e

  def _text_rx_event(self) -> None:
    """Stores the received name/value pair to the temporary frame buffer."""
    if self._current_name and self._current_value:
        self._temp_frame_data[self._current_name.strip()] = self._current_value.strip()
    # Reset line buffers
    self._current_name = ""
    self._current_value = ""

  def _frame_end_event(self, valid: bool) -> None:
    """Called when the Checksum line is received and the frame is complete."""
    if valid:
        self.logger.debug(f"Frame Validated. Updating public data. ({len(self._temp_frame_data)} fields)")
        # Use .update() for a quick, near-atomic transfer of the frame data
        self.data.update(self._temp_frame_data)
    else:
        self.logger.warning(f"Invalid frame checksum: {self._checksum}. Discarding frame data.")
    
    # Reset for the next frame
    self._temp_frame_data.clear()

  def _rx_data(self, inbyte: int) -> None:
    """
    The VE.Direct State Machine handler, processing one byte at a time.
    """
    try:
      byte_char = chr(inbyte)
    except ValueError:
      self.logger.warning(f"Received non-ASCII byte: {inbyte}. Skipping checksum.")
      return

    # Check for start of hex frame (':')
    if (byte_char == ':') and (self._state != States.CHECKSUM):
        self._pushed_state = self._state
        self._state = States.RECORD_HEX
        # The ':' character itself *must* contribute to the checksum before the state change in C++
        self._checksum = (self._checksum + inbyte) & 0xFF 

    # All bytes except for those in RECORD_HEX contribute to the checksum.
    if self._state != States.RECORD_HEX:
        # Use bitwise AND to ensure the checksum wraps around 256 (like uint8_t in C)
        self._checksum = (self._checksum + inbyte) & 0xFF

    if self._state == States.RECORD_HEX:
        # Simplified: Just wait for the end marker. The C++ code's hex parsing is complex.
        if byte_char == '\n':
            self.logger.warning("Hex frame detected and ignored.")
            self._state = self._pushed_state # Restore previous state
        return
        
    # --- State Transitions (Text Frame) ---
    byte_char_upper = byte_char.upper()

    if self._state == States.IDLE:
        if byte_char == '\n':
            self._state = States.RECORD_BEGIN
        # All other chars skipped while IDLE

    elif self._state == States.RECORD_BEGIN:
        # First character of a name
        self._current_name += byte_char_upper
        self._state = States.RECORD_NAME

    elif self._state == States.RECORD_NAME:
        if byte_char == '\t':
            # End of name, check for Checksum tag
            if self._current_name.strip() == CHECKSUM_TAG:
                self._state = States.CHECKSUM
            else:
                self._state = States.RECORD_VALUE
        elif byte_char in ('\r', '\n'):
            # Protocol Error: CR/LF in the middle of a name. Resync.
            self.logger.warning(f"Protocol Error: Unexpected EOL in name: {self._current_name}")
            self._state = States.IDLE 
            self._current_name = ""
        else:
            self._current_name += byte_char_upper

    elif self._state == States.RECORD_VALUE:
        if byte_char == '\n':
            # End of record
            self._text_rx_event()
            self._state = States.RECORD_BEGIN
        elif byte_char == '\r':
            # Ignore CR
            pass
        else:
            self._current_value += byte_char

    elif self._state == States.CHECKSUM:
        # The CHECKSUM tag has been processed. We are in the value portion of the checksum line.
        if byte_char == '\n':
            # Final line break received. Frame is complete.
            # Checksum should be 0xFF + 1 = 0x00 when wrapped (mChecksum == 0)
            valid = (self._checksum == 0)
            self._frame_end_event(valid)
            self._checksum = 0 # Reset checksum for next frame
            self._state = States.IDLE
        elif byte_char == '\r':
            pass
        # Note: The C++ code doesn't store the checksum value into mValue. We don't need to either.

  async def _read(self) -> None:
    """The main asynchronous loop to read from the UART."""
    self.logger.info("Starting VE.Direct background read task...")
    
    while self.active:
      try:
        if self.uart.any():
          # Read up to 64 bytes at once to reduce calls to .read()
          data_chunk = self.uart.read(64)
          
          if data_chunk:
            # Iterate over the bytearray/bytes object
            for byte in data_chunk:
              # byte is an integer value of the character (0-255)
              self._rx_data(byte)
          
        # Always yield control to the scheduler. Use Sleep.async_ms to allow
        # other tasks to run, which is critical in MicroPython.
        await Sleep.async_ms(5) 

      except Exception as e:
        self.logger.error(f"Error in _read_task: {e}. Recovering in 1s.")
        await Sleep.async_s(1) # Wait before retrying on error

    self.logger.info("VE.Direct background read task stopped.")

  async def activate(self) -> None:
    """Starts the asynchronous reading task."""
    if not self.active:
      self.active = True
      # Re-initialize UART to flush any stale data, critical for robust serial comms
      try:
        self.uart.deinit() 
        self.uart.init(baudrate=self.uart_baudrate, timeout=10) 
      except Exception as e:
        self.logger.error(f"Failed to re-initialize UART: {e}")
        return

      self._read_task = asyncio.create_task(self._read())
      self.logger.info("VEDirectConnector activated.")

  def deactivate(self) -> None:
    """Stops the asynchronous reading task."""
    if self.active:
      self.active = False
      if self._read_task is not None:
        self._read_task.cancel()
        self._read_task = None
      self.logger.info("VEDirectConnector deactivated.")
      
  def get(self, key: str, default=None) -> str | None:
    """Retrieves a value from the last valid frame data."""
    return self.data.get(key.upper(), default)
    
  def getAll(self) -> dict[str, str]:
    """Retrieves all data from the last valid frame."""
    return self.data.copy()

  def __del__(self):
    self.deactivate()
    try:
      self.uart.deinit()
    except AttributeError:
      pass # Already deinit'd or never created

if __name__ == '__main__':
    # --- Example Usage (Requires physical UART connection) ---
    # This block is for testing purposes on a device (e.g., ESP32)
    # where you can connect the VE.Direct device's TX pin to the 
    # specified RX_PIN. 

    # Configuration for an ESP32 (adjust pins as necessary for your board)
    UART_ID = 2
    RX_PIN_NUM = 17 # Connect VE.Direct TX here

    # To run this, uncomment the asyncio.run call and ensure the UART pins are available.

    async def main_vedirect_test():
      logger_main = Logging.Log("VEDirectTest", Logging.LEVEL.INFO)
      logger_main.info("Starting VEDirectConnector Test. Connect VE.Direct TX to pin 17.")
      
      try:
        # TX pin is set to None as we only need to receive data
        connector = VEDirectConnector(UART_ID, tx_pin=None, rx_pin=RX_PIN_NUM, log_level=Logging.LEVEL.DEBUG)
        await connector.activate()
        
        start_time = Time.current_s()
        while Time.current_s() < start_time + 10: # Run for 10 seconds
          await Sleep.async_s(1)
          data = connector.getAll()
          if data:
            logger_main.info("--- VE.Direct Data Update ---")
            # Example specific field access
            soc = connector.get('SOC', 'N/A')
            voltage = connector.get('V', 'N/A')
            logger_main.info(f"SOC: {soc}, Voltage: {voltage}")
            logger_main.debug(f"Full Frame: {data}")
          else:
            logger_main.info("Waiting for first valid frame...")
            
      except Exception as e:
        logger_main.error(f"Test run failed: {e}")
      finally:
        if 'connector' in locals(): connector.deactivate() # type: ignore
        logger_main.info("VEDirectConnector Test Ended.")

    asyncio.run(main_vedirect_test())
    pass