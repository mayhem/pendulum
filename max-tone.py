#!/usr/bin/env python

import smbus
import time
from math import sqrt
import pygame.mixer

from pendulum import Pendulum

wavs = [ "wavs/beep.wav", "wavs/boop.wav" ]
sounds = []
channels = []

print "create mixer"
pygame.mixer.init(44100, -16, 1, 1024)

print "loading sounds"
for i, f in enumerate(wavs):
    sounds.append(pygame.mixer.Sound(f))
    channels.append(pygame.mixer.Channel(i + 1))

print "setup pendulum"
p = Pendulum()
ret = p.load_calibration()
if ret:
    print ret

last_m = 0
sign = 0
while True:
    x, y, z = p.calculate_window(20)

    m = sqrt(x * x + y * y + z * z)
    if last_m == 0:
        last_m = m

    print "%4d, %4d %4d |%4d| " % (x, y, z, m),
    if m > last_m and sign <= 0:
        # going up!
        sign = 1
        print "    **",
        channels[0].play(sounds[0])
    else:
        if m < last_m and sign >= 0:
            # going down
            sign = -1
            print "**",
            channels[1].play(sounds[1])

    last_m = m

    print
    time.sleep(.01)

#    print "x (%d, %d) y (%d, %d) z (%d, %d)" % (x_min, x_max, y_min, y_max, z_min, z_max)
#    print "%.4f, %.4f %.4f" % (x, y, z)
