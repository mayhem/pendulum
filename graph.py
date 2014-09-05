#!/usr/bin/env python

import sys
import socket
import fcntl
import struct
from Queue import Queue
from threading import Thread, Event
from flask import Flask, render_template, request
from flask_sockets import Sockets
from pendulum import Pendulum

STATIC_PATH = "/static"
STATIC_FOLDER = "static"
TEMPLATE_FOLDER = "template"

p = None

app = Flask(__name__,
            static_url_path = STATIC_PATH,
            static_folder = STATIC_FOLDER,
            template_folder = TEMPLATE_FOLDER)
sockets = Sockets(app)

class GraphPendulum(Pendulum):

    def __init__(self, update_interval, num_points):
        Pendulum.__init__(self, update_interval)
        self.data = []
        self.num_points = num_points
        self.ws_queue = Queue()
        self.ws_event = Event()

    def process_data(self, data):
        self.data = "%.4f,%.4f,%.4f,%.4f" % (data['t'], data['x'], data['y'], data['z'])
        self.ws_event.set()

class Background(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.pendulum = None

    def run(self):
        self.pendulum = GraphPendulum(.1, 20)
        self.pendulum.load_calibration()
        self.pendulum.process()

def get_ip_address_from_interface(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        return socket.inet_ntoa(fcntl.ioctl(s.fileno(), 0x8915,  
                                struct.pack('256s', ifname[:15]))[20:24])
    except IOError:
        return "[none]"

host = get_ip_address_from_interface("eth0")
port = 8000

@app.route('/') 
def hello(): 
    return render_template("index", host=host, port=port)

p = Background()
@sockets.route('/pendulum') 
def pendulum_socket(ws): 
    print "Socket connected!"
    while True: 
        p.pendulum.ws_event.wait()    
        ws.send(p.data)

p.start()

if __name__ == '__main__':
    app.run(debug=True, host=host, port=port)
