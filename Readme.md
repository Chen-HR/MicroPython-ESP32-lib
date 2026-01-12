# MicroPython ESP32 Library

![Version](https://img.shields.io/badge/version-0.2.2-blue.svg)
![MicroPython](https://img.shields.io/badge/MicroPython-ESP32-green.svg)
![License](https://img.shields.io/badge/license-MIT-lightgrey.svg)

**MicroPython-ESP32-lib** is a comprehensive, modular, and asynchronous-first utility library designed for ESP32 microcontrollers running MicroPython. It simplifies complex hardware interactions, network management, and system tasks by providing high-level abstractions and robust event-driven patterns.

## 🌟 Key Features

* **Asynchronous Core**: Built with `uasyncio` at its heart, enabling non-blocking operations for WiFi connections, sensors, and state management.
* **Robust Networking**:
  * Advanced WiFi `Connector` with auto-reconnect logic, static IP support, and multi-configuration handling.
  * Integrated tools for NTP time synchronization, MQTT, and socket abstraction.
* **Advanced Device Drivers**:
  * **Buttons**: Interrupt-driven, state-machine-based debouncing with support for press, release, and holding events.
  * **LEDs**: PWM-based control for single LEDs, RGB LEDs, and NeoPixels (WS2812).
  * **Sensors**: Drivers for DHT11/22, Light Sensors (LDR/TEMT6000), and VE.Direct protocol.
  * **Audio**: Tone generation and musical note abstraction using PWM.
* **System Utilities**:
  * Unified `Time` module handling RTC, NTP, and high-precision timestamps.
  * Custom `Logging` module supporting levels (INFO, DEBUG, ERROR) and stream/file handlers.
  * Event-driven `ListenerHandler` pattern for decoupled application logic.

## 📂 Project Structure

The library is organized into four main directories under `src/micropython_esp32_lib`:

| Module | Description |
| :--- | :--- |
| **`System`** | Core system functions. Includes `Digital` (Pin modes), `Time` (NTP, RTC, Sleep), and thread `Lock` implementations. |
| **`Network`** | Networking stack. Includes `WiFi` (Manager), `IP` (Address parsing), `MQTT` (Client wrapper), `Socket`, and `NTP`. |
| **`Device`** | Hardware drivers. Includes `Button`, `LED`, `DHT` (Temp/Hum), `LightSensor`, `Speaker`, and `VEDirect`. |
| **`Utils`** | Utility helpers. Includes `Logging`, `Flag`, `ListenerHandler`, and math/mapping functions. |

## 🚀 Installation

### Prerequisites

* ESP32 board with MicroPython firmware installed.
* Python 3.11+ (for development/tools).

### Uploading to ESP32

You can use tools like `mpremote`, `ampy`, or `rshell` to upload the library.

**Using `mpremote` (Recommended):**

```bash
# Copy the library folder to the device's lib directory
mpremote cp -r src/micropython_esp32_lib :lib/micropython_esp32_lib
```

**Using VS Code (Pymakr):**
Simply place the `src/micropython_esp32_lib` folder into your project's root directory and upload the project.

## 📖 Usage Examples

### 1. Connecting to WiFi (Async)

The library separates configuration from the connection logic, allowing for easy management of multiple networks.

```python
import asyncio
from micropython_esp32_lib.Network import WiFi
from micropython_esp32_lib.Utils import Logging

# Configure Logging
Logging.config_stream(level=Logging.Level.INFO)

async def main():
    # Define Network Configurations
    home_net = WiFi.Config(ssid="MyHomeWiFi", password="securepassword")
    
    # Initialize Async Connector
    connector = WiFi.AsyncConnector(interface=WiFi.Mode.STA)
    
    # Attempt to connect
    success = await connector.tryConnect([home_net])
    
    if success:
        Logging.info(f"Connected! IP: {connector.getHostIP()}")
    else:
        Logging.error("Failed to connect to WiFi.")

asyncio.run(main())
```

### 2. Advanced Button Handling

Use the `InterruptDrivenStateDebounceButton` for jitter-free button inputs without blocking the main loop.

```python
import asyncio
from machine import Pin
from micropython_esp32_lib.Device import Button
from micropython_esp32_lib.System import Digital
from micropython_esp32_lib.Utils import Logging, ListenerHandler

# Define a custom handler for button press
class MyButtonHandler(ListenerHandler.SyncHandler):
    def handle(self, obj=None, *args, **kwargs):
        Logging.info("Button Pressed!")

async def main():
    # Setup Button on GPIO 0 (Boot button on many ESP32s)
    pin = Pin(0, Pin.IN, Pin.PULL_UP)
    
    # Initialize Button with Debounce
    btn = Button.InterruptDrivenStateDebounceButton(pin, Digital.Signal.HIGH)
    await btn.activate()

    # Attach a listener for the "Pressed" event
    listener = Button.OnPressedListener(btn)
    handler_wrapper = ListenerHandler.AsyncListenerSyncHandler(listener, MyButtonHandler())
    await handler_wrapper.activate()

    # Keep the loop running
    while True:
        await asyncio.sleep(1)

asyncio.run(main())
```

### 3. Controlling an RGB LED

Fade an RGB LED smoothly using the `RGBLED` class.

```python
import time
from machine import Pin
from micropython_esp32_lib.Device import LED

# Initialize pins
r_pin = LED.LED(Pin(18, Pin.OUT))
g_pin = LED.LED(Pin(19, Pin.OUT))
b_pin = LED.LED(Pin(21, Pin.OUT))

# Initialize RGB Control
rgb = LED.RGBLED(r_pin, g_pin, b_pin)

# Set Color (Red, Green, Blue) - values 0-255
rgb.set_color(255, 0, 0) # Red
time.sleep(1)
rgb.set_color(0, 255, 0) # Green
time.sleep(1)
rgb.set_color(0, 0, 255) # Blue
```

### 4. Logging and Time

Use the standardized logging system with precise timestamping.

```python
from micropython_esp32_lib.Utils import Logging
from micropython_esp32_lib.System import Time

# Set global timezone (e.g., UTC+8)
Time.setTimezone(8)

# Configure Logger
logger = Logging.getLogger("MyApp")
logger.setLevel(Logging.Level.DEBUG)
logger.addHandler(Logging.StreamHandler())

logger.info("System initialized at %s", Time.Time())
logger.debug("Current timestamp (ms): %d", Time.current_ms())
```

## 🛠 Dependencies

This library requires the standard MicroPython firmware.
Some modules (like `Device.DHT` or `Network.MQTT`) rely on built-in MicroPython drivers (`dht`, `umqtt.robust`) which are typically included in standard ESP32 builds.

## 📦 Build

This project uses `uv` for build management (defined in `pyproject.toml`).

```bash
# Build the package
uv build
```

## 📄 License

This project is open-source. Please refer to the license badge or file for details.

---

**Authors**: HRChen  
**Version**: 0.2.2
