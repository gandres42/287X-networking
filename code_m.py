import busio
from board import *
from adafruit_bus_device.i2c_device import I2CDevice
import busio as io

with io.I2C(SCL, SDA) as i2c:
    device = I2CDevice(i2c, 0x01)
    bytes_read = bytearray(4)
    with device:
        device.readinto(bytes_read)
        print(bytes_read)
    # A second transaction
    with device:
        device.write(bytes_read)

# import board
# import busio
    
# REGISTERS = (0, 256)  # Range of registers to read, from the first up to (but
#                         # not including!) the second value.
    
# REGISTER_SIZE = 2     # Number of bytes to read from each register.
    
# # Initialize and lock the I2C bus.
# i2c = busio.I2C(board.SCL, board.SDA)
# while not i2c.try_lock():
#     pass
    
# # Find the first I2C device available.
# devices = i2c.scan()
# while len(devices) < 1:
#     devices = i2c.scan()
# device = devices[0]
# print('Found device with address: {}'.format(hex(device)))
    
# # Scan all the registers and read their byte values.
# result = bytearray(REGISTER_SIZE)
# for register in range(*REGISTERS):
#     try:
#         i2c.writeto(device, bytes([register]))
#         i2c.readfrom_into(device, result)
#     except OSError:
#         continue  # Ignore registers that don't exist!
#     print('Address {0}: {1}'.format(hex(register), ' '.join([hex(x) for x in result])))
    
# # Unlock the I2C bus when finished.  Ideally put this in a try-finally!
# i2c.unlock()