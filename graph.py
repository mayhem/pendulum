#!/usr/bin/env python

from flask import Flask, render_template
from flask_sockets import Sockets
from pendulum import Pendulum

STATIC_PATH = "/static"
STATIC_FOLDER = "static"
TEMPLATE_FOLDER = "template"

app = Flask(__name__,
            static_url_path = STATIC_PATH,
            static_folder = STATIC_FOLDER,
            template_folder = TEMPLATE_FOLDER)
#sockets = Sockets(app)

class GraphPendulum(Pendulum):

    def __init__(self, update_interval, num_points):
        Pendulum.__init__(self, update_interval)
        self.data = []
        self.num_points = num_points

    def process_data(self, data):
#        print "%.03f: %.4f, %.4f, %.4f" % (data['t'], data['x'], data['y'], data['z'])
        self.data.append(data)
        if len(self.data) > self.num_points:
            self.exit()

    def graph_data(self, k):
        fmt = []
        for d in self.data:
            fmt.append('%.3f' % d[k])

        data =  ",".join(fmt)
        return data


@app.route('/') 
def hello(): 
    return render_template("index")

#p = GraphPendulum(.5, 20)
#p.load_calibration()
#try:
#    p.process()
#except KeyboardInterrupt:
#    p.exit()
#    print

#print html % (p.graph_data('t'), p.graph_data('x'), p.graph_data('y'), p.graph_data('z'))

app.run(debug=True, host="0.0.0.0", port=8080)

