#!/usr/bin/env python

import smbus
import time
import json
from struct import unpack

# Maximum readings
# x (-2048, 2047) y (-2048, 2047) z (-1740, 1780)

CALIBRATION_WINDOW = 10
CALIBRATION_FILE = ".pendulum-calibration.json"

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

        self.reset_calibration()
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

        return (x, y, z)
#        return (x - self.x_off - self.x_calibration, y - self.y_off - self.y_calibration, z - self.z_off - self.z_calibration)

    def calculate_window(self, window_size):
        values = []
        for i in xrange(window_size):
            values.append((self.get_values()))

        x_avg = y_avg = z_avg = 0

        for x, y, z in values:
            x_avg += x
            y_avg += y
            z_avg += z

        x_avg //= window_size
        y_avg //= window_size
        z_avg //= window_size

        return x_avg, y_avg, z_avg

    def reset_calibration(self):
        self.x_calibration = 0
        self.y_calibration = 0
        self.z_calibration = 0

    def load_calibration(self):

        try:
            f = open(CALIBRATION_FILE, "r")
            data = f.read()
            f.close()
        except IOError, e:
            return "Cannot read calibration file %s: ", (CALIBRATION_FILE, e)

        try:    
            data = json.loads(data)
        except ValueError:
            return "Calibration data file is corrupt."

        self.x_calibration = data['calibration'][0]
        self.y_calibration = data['calibration'][1]
        self.z_calibration = data['calibration'][2]

        print "loaded ", self.x_calibration, self.y_calibration, self.z_calibration

        return ""

    def save_calibration(self):

        self.reset_calibration()
        x_avg, y_avg, z_avg = calculate_window(CALIBRATION_WINDOW)

        try:
            f = open(CALIBRATION_FILE, "w")
            f.write(json.dumps({ 'calibration' : (x_avg, y_avg, z_avg)}))
            f.close()
        except IOError, e:
            return "Cannot write calibration file %s: ", (CALIBRATION_FILE, e)

        return ""
