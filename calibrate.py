#!/usr/bin/env python

import smbus
import time
from pendulum import Pendulum

p = Pendulum()
ret = p.save_calibration()
if ret:
    print ret
else:
    print "Calibration saved."
