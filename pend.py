#!/usr/bin/env python

from pendulum import Pendulum

class TestPendulum(Pendulum):

    def __init__(self, update_interval):
        Pendulum.__init__(self, update_interval)

    def process_data(self, data):
        print "%.03f: %.4f, %.4f, %.4f" % (data['t'], data['x'], data['y'], data['z'])

p = Pendulum(.1)
p.process()
