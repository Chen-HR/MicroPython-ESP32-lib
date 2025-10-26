from machine import Pin, SPI
from FM638A.mfrc522 import MFRC522

# Define SPI pins (adjust according to your ESP32-S3 and wiring)
# Example for specific pins, replace with your actual connections
# sck_pin = Pin(41)
# mosi_pin = Pin(40)
# miso_pin = Pin(39)

# ss_pin = Pin(42)  # Slave Select
# rst_pin = Pin(37) # Reset

# Initialize SPI
# spi = SPI(1, baudrate=2500000, polarity=0, phase=0, sck=sck_pin, mosi=mosi_pin, miso=miso_pin)

# Initialize MFRC522 reader
# rdr = MFRC522(10, 11, 12, 14, 9)
# print("Place card near the reader...")
# while True:
#     (stat, tag_type) = rdr.request(rdr.REQIDL)
#     if stat == rdr.OK:
#         (stat, raw_uid) = rdr.anticoll()
#         if stat == rdr.OK:
#             print("Card detected!")
#             print("  Type: 0x%02x" % tag_type)
#             print("  UID: 0x%02x%02x%02x%02x" % (raw_uid[0], raw_uid[1], raw_uid[2], raw_uid[3]))
#             # You can add further logic here to read/write data to the card


# # import mfrc522
# from os import uname


# def do_read():
#   rdr = MFRC522(10, 11, 12, 14, 9)

#   print("")
#   print("Place card before reader to read from address 0x08")
#   print("")

#   try:
#     while True:

#       (stat, tag_type) = rdr.request(rdr.REQIDL)

#       if stat == rdr.OK:

#         (stat, raw_uid) = rdr.anticoll()

#         if stat == rdr.OK:
#           print("New card detected")
#           print("  - tag type: 0x%02x" % tag_type)
#           print("  - uid   : 0x%02x%02x%02x%02x" % (raw_uid[0], raw_uid[1], raw_uid[2], raw_uid[3]))
#           print("")

#           if rdr.select_tag(raw_uid) == rdr.OK:

#             key = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]

#             if rdr.auth(rdr.AUTHENT1A, 8, key, raw_uid) == rdr.OK:
#               print("Address 8 data: %s" % rdr.read(8))
#               rdr.stop_crypto1()
#             else:
#               print("Authentication error")
#           else:
#             print("Failed to select tag")

#   except KeyboardInterrupt:
#     print("Bye")

# do_read()