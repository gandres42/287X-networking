import board
from i2ctarget import I2CTarget

regs = [0] * 16
index = 0

with I2CTarget(board.SCL, board.SDA, [0x40]) as device:
    while True:
        r = device.request()
        if not r:
            # Maybe do some housekeeping
            continue
        with r:  # Closes the transfer if necessary by sending a NACK or feeding dummy bytes
            if r.address == 0x40:
                if not r.is_read:  # Main write which is Selected read
                    b = r.read(1)
                    if not b or b[0] > 15:
                        break
                    index = b[0]
                    b = r.read(1)
                    if b:
                        regs[index] = b[0]
                elif r.is_restart:  # Combined transfer: This is the Main read message
                    n = r.write(bytes([regs[index]]))
                #else:
                    # A read transfer is not supported in this example
                    # If the microcontroller tries, it will get 0xff byte(s) by the ctx manager (r.close())
            elif r.address == 0x41:
                if not r.is_read:
                    b = r.read(1)
                    if b and b[0] == 0xde:
                        # do something
                        pass