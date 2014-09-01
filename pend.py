#!/usr/bin/env python

import smbus
import time
from struct import unpack

# Maximum readings
# x (-2048, 2047) y (-2048, 2047) z (-1740, 1780)

class Pendulum(object):

    address = 0x1d
    def __init__(self):
        self.bus = smbus.SMBus(0)

        # 0x87 = power on, no self test, enable all axis, 40hz data rate
        self.bus.write_byte_data(self.address, 0x20, 0x87) 

        x_off = self.bus.read_byte_data(self.address, 0x16)
        y_off = self.bus.read_byte_data(self.address, 0x17)
        z_off = self.bus.read_byte_data(self.address, 0x18)

        self.x_off = unpack("<b", chr(x_off))[0]
        self.y_off = unpack("<b", chr(y_off))[0]
        self.z_off = unpack("<b", chr(z_off))[0]

        self.reset_min_max()

    def reset_min_max(self):
        self.x_min = 5000 
        self.x_max = -5000 
        self.y_min = 5000
        self.y_max = -5000
        self.z_min = 5000
        self.z_max = -5000 

    def get_min_values(self):
        return (x_min, y_min, z_min)

    def get_max_values(self):
        return (x_max, y_max, z_max)

    def get_values(self, track_min_max=False):
        while True:
            try:
                x_low = self.bus.read_byte_data(self.address, 0x28)
                x_hi = self.bus.read_byte_data(self.address, 0x29)
            except IOError:
                continue
            x = unpack("<h", chr(x_low) + chr(x_hi))[0]

            if x < self.x_min:
                self.x_min = x
            if x > self.x_max:
                self.x_max = x

            break

        while True:
            try:
                y_low = self.bus.read_byte_data(self.address, 0x2A)
                y_hi = self.bus.read_byte_data(self.address, 0x2B)
            except IOError:
                continue
            y = unpack("<h", chr(y_low) + chr(y_hi))[0] 

            if y < self.y_min:
                self.y_min = y
            if y > self.y_max:
                self.y_max = y

            break

        while True:
            try:
                z_low = self.bus.read_byte_data(self.address, 0x2C)
                z_hi = self.bus.read_byte_data(self.address, 0x2D)
            except IOError:
                continue

            z = unpack("<h", chr(z_low) + chr(z_hi))[0] 
            if z < self.z_min:
                self.z_min = z
            if z > self.z_max:
                self.z_max = z

            break

        return (x - self.x_off, y - self.y_off, z - self.z_off)

if __name__ == "__main__":    
    p = Pendulum()
    while True:
        x, y, z = p.get_values()
        print "%d, %d %d" % (x, y, z)
        time.sleep(.01)

#    print "x (%d, %d) y (%d, %d) z (%d, %d)" % (x_min, x_max, y_min, y_max, z_min, z_max)
#    print "%.4f, %.4f %.4f" % (x, y, z)
