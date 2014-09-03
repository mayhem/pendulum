#!/usr/bin/env python

import smbus
import time
import json
import abc
from Queue import Queue
from threading import Thread, Lock, Event
from struct import unpack

# Maximum readings
# x (-2048, 2047) y (-2048, 2047) z (-1740, 1780)

CALIBRATION_WINDOW = 10
CALIBRATION_FILE = ".pendulum-calibration.json"

class Pendulum(Thread):

    address = 0x1d
    def __init__(self, update_interval):
        Thread.__init__(self)
        self.bus = smbus.SMBus(0)

        self.queue = Queue()
        self.lock = Lock()
        self.event = Event()
        self.exit_now = False

        self.update_interval = update_interval
        self.event_start_t = 0
        self.prog_start_t = time.time()

        # 0x87 = power on, no self test, enable all axis, 40hz data rate
        # 0xD7 = power on, no self test, enable all axis, 160Hz data rate
        self.bus.write_byte_data(self.address, 0x20, 0xD7) 

        x_off = self.bus.read_byte_data(self.address, 0x16)
        y_off = self.bus.read_byte_data(self.address, 0x17)
        z_off = self.bus.read_byte_data(self.address, 0x18)

        self.x_off = unpack("<b", chr(x_off))[0]
        self.y_off = unpack("<b", chr(y_off))[0]
        self.z_off = unpack("<b", chr(z_off))[0]

        self.reset_calibration()

    def _read_data_point(self):
        while True:
            try:
                x_low = self.bus.read_byte_data(self.address, 0x28)
                x_hi = self.bus.read_byte_data(self.address, 0x29)
            except IOError:
                continue
            x = unpack("<h", chr(x_low) + chr(x_hi))[0]

            break

        while True:
            try:
                y_low = self.bus.read_byte_data(self.address, 0x2A)
                y_hi = self.bus.read_byte_data(self.address, 0x2B)
            except IOError:
                continue
            y = unpack("<h", chr(y_low) + chr(y_hi))[0] 

            break

        while True:
            try:
                z_low = self.bus.read_byte_data(self.address, 0x2C)
                z_hi = self.bus.read_byte_data(self.address, 0x2D)
            except IOError:
                continue

            z = unpack("<h", chr(z_low) + chr(z_hi))[0] 

            break

        return (x, y, z)

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

    def get_data_point(self):
        while True:
            if self.queue.empty:
                sleep(.0001)
                continue

            break

        return self.queue.get()

    def clear_current_reading(self):
        '''Remove any samples currently being collected'''

        self.lock.acquire()
        while self.queue.get():  
            pass
        self.lock.release()

    @abc.abstractmethod
    def process_data(self, data):
        '''A deriving class must supply this method!'''
        return

    def process(self):
        '''Main loop for the pendulum class'''
        self.start()

        while True:
            self.event.wait()
            num_points = 0
            start_t = 0
            x_sum = y_sum = z_sum = t_sum = 0.0
            while True:
                self.lock.acquire()
                data = self.queue.get()
                self.lock.release()

                if not start_t:
                    start_t = data['t']

                x_sum += data['x']
                y_sum += data['y']
                z_sum += data['z']
                t_sum += data['t']
                num_points += 1

                if data['t'] - start_t >= self.update_interval:
                    break

            e = dict(t = (float(t_sum) / num_points) - self.prog_start_t, 
                     x = float(x_sum) / num_points,
                     y = float(y_sum) / num_points,
                     z = float(z_sum) / num_points)

            self.process_data(e)

    def exit(self):
        self.exit_now = True

    def run(self):
        # There used to be an overrun check, but it turns out that in anything
        # but the steady state, we can't keep up with a 160Hz sample rate. 
        # shouldn't be a problem.
        while not self.exit_now:
            try:
                status = self.bus.read_byte_data(self.address, 0x27)
            except IOError:
                continue

            # Is a new xyz data point is ready?
            if status & 0x08:
                x, y, z = self._read_data_point()
                t = time.time()
                self.queue.put(dict(t = t, x = x, y = y, z = z))
                if self.event_start_t == 0:
                    self.event_start_t = t

                if t - self.event_start_t >= self.update_interval:
                    self.event_start_t = 0
                    self.event.set()
