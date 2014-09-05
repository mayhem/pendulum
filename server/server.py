#!/usr/bin/env python

import sys
import socket
import fcntl
import struct
from flask import Flask, render_template, request
from flask.ext.socketio import SocketIO, emit
from time import sleep

STATIC_PATH = "/static"
STATIC_FOLDER = "static"
TEMPLATE_FOLDER = "template"

def get_ip_address_from_interface(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        return socket.inet_ntoa(fcntl.ioctl(s.fileno(), 0x8915,  
                                struct.pack('256s', ifname[:15]))[20:24])
    except IOError:
        return "[none]"

app = Flask(__name__,
            static_url_path = STATIC_PATH,
            static_folder = STATIC_FOLDER,
            template_folder = TEMPLATE_FOLDER)
socketio = SocketIO(app)

host = get_ip_address_from_interface("eth0")
port = 8000

p_host = "localhost"
p_port = 9000

@app.route('/') 
def index(): 
    return render_template("index", host=host, port=port)

@socketio.on('connect', namespace='/pendulum')
def test_connect():
    print "Client connected"
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((p_host, p_port))
        f = sock.makefile()
        while True:
            line = f.readline()
            emit('data', {'data': line.strip() }) 
    finally:
        sock.close()

@socketio.on('disconnect', namespace='/pendulum')
def test_disconnect():
    print('Client disconnected')

if __name__ == '__main__':
    socketio.run(app, host=host, port=port)

