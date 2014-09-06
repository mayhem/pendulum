#!/usr/bin/env python

import sys
import SocketServer
from pendulum import Pendulum

HOST, PORT = "localhost", 9000

class StreamHandler(SocketServer.BaseRequestHandler):
    def handle(self):
        while True:
            p.get_event().wait()    
            data = p.get_data()
            p.get_event().clear()    
            if data:
               s = "%.4f,%.4f,%.4f,%.4f\n" % (data['t'], data['x'], data['y'], data['z'])
               self.request.sendall(s)

p = Pendulum(.05)
p.load_calibration()
p.start()

server = SocketServer.TCPServer((HOST, PORT), StreamHandler)
try:
    server.serve_forever()
except KeyboardInterrupt:
    print "Stoping thread!"
    p.exit()
    raise
