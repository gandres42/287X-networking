# import board
# from i2ctarget import I2CTarget

# # I2CTarget(board.SCL, board.SDA, (0x40,))

# # while True:
# #     pass
# with I2CTarget(board.SCL, board.SDA, (0x01,)) as device:
#     while True:
#         r = device.request()
#         # r.read(-1)
#         if not r:
#             # Maybe do some housekeeping
#             continue
#         with r:  # Closes the transfer if necessary by sending a NACK or feeding dummy bytes
#             if r.address == int(0x01):
#                 if not r.is_read:  # Main write which is Selected read
#                     b = r.read(1)
#                     if not b or b[0] > 15:
#                         break
#                     index = b[0]
#                     b = r.read(1)
#                     if b:
#                         regs[index] = b[0]
#                 elif r.is_restart:  # Combined transfer: This is the Main read message
#                     n = r.write(bytes([regs[index]]))
#                 else:
#                     # A read transfer is not supported in this example
#                     # If the microcontroller tries, it will get 0xff byte(s) by the ctx manager (r.close())
#                     pass

import i2cperipheral
import board

i2c = i2cperipheral.I2CPeripheral(bus=0, sclPin=board.SCL, sdaPin=board.sda, address=0x01)
data = bytearray(4)
while True:
    regAddressBuff = bytearray(1)

    # First thing master should send is register address.
    # Poll to see if it has been received yet.
    if not i2c.have_recv_req():
        continue
    i2c.recv(regAddressBuff, timeout=0)

    # Wait for master to send either the read or write.
    while (not i2c.have_recv_req()) and (not i2c.have_send_req()):
        pass

    # Only support read/write requests for register 0x01.
    regAddress = regAddressBuff[0]
    if regAddress != 0x01:
        # Handle invalid address.
        continue

    # Handle the master read/write request.
    if i2c.have_recv_req():
        i2c.recv(data, timeout=1000)
    else:
        i2c.send(data, timeout=1000)