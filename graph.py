#!/usr/bin/env python

from pendulum import Pendulum

html = '''
<html>
   <head>
       <title>Pendulum graph</title>
   </head>
   <body>
   <canvas id="chart" width="800" height="500"></canvas>
   <script type="text/javascript" src="jquery-1.10.2.min.js"></script>
   <script type="text/javascript" src="Chart.min.js"></script>
<script>
var data = {
   labels: [ %s ],
   datasets: [
       {
         label: "X",
         strokeColor: "rgba(120,220,220,1)",
         data: [%s]
       },
       {
         label: "Y",
         strokeColor: "rgba(220,120,220,1)",
         data: [%s]
       },
       {
         label: "Z",
         strokeColor: "rgba(220,220,120,1)",
         data: [%s]
       }
   ]
};
'''
otherHTMLGuff = '''
var options = 
{
    scaleShowGridLines : true,
    scaleGridLineColor : "rgba(0,0,0,.05)",
    scaleGridLineWidth : 1,
    bezierCurve : true,
    bezierCurveTension : 0.4,
    pointDot : false,
    pointDotRadius : 4,
    pointDotStrokeWidth : 1,
    pointHitDetectionRadius : 20,
    datasetStroke : true,
    datasetStrokeWidth : 2,
    datasetFill : false,
};
Chart.defaults.global = {
    animation: true,
    animationSteps: 60,
    animationEasing: "easeOutQuart",
    showScale: true,
    scaleOverride: true,
    scaleSteps: 15,
    scaleStepWidth: 10,
    scaleStartValue: -30,
    scaleLineColor: "rgba(0,0,0,.1)",
    scaleLineWidth: 1,
    scaleShowLabels: true,
    scaleLabel: "<%=value%>",
    scaleIntegersOnly: true,
    scaleBeginAtZero: false,
    scaleFontFamily: "'Helvetica Neue', 'Helvetica', 'Arial', sans-serif",
    scaleFontSize: 12,
    scaleFontStyle: "normal",
    scaleFontColor: "#666",
    responsive: false,
    maintainAspectRatio: true,
    showTooltips: true,
    tooltipEvents: ["mousemove", "touchstart", "touchmove"],
    tooltipFillColor: "rgba(0,0,0,0.8)",
    tooltipFontFamily: "'Helvetica Neue', 'Helvetica', 'Arial', sans-serif",
    tooltipFontSize: 14,
    tooltipFontStyle: "normal",
    tooltipFontColor: "#fff",
    tooltipTitleFontFamily: "'Helvetica Neue', 'Helvetica', 'Arial', sans-serif",
    tooltipTitleFontSize: 14,
    tooltipTitleFontStyle: "bold",
    tooltipTitleFontColor: "#fff",
    tooltipYPadding: 6,
    tooltipXPadding: 6,
    tooltipCaretSize: 8,
    tooltipCornerRadius: 6,
    tooltipXOffset: 10,
    tooltipTemplate: "<%if (label){%><%=label%>: <%}%><%= value %>",
    multiTooltipTemplate: "<%= value %>",
    onAnimationProgress: function(){},
    onAnimationComplete: function(){}
};
var ctx = $("#chart").get(0).getContext("2d");
var chart = new Chart(ctx).Line(data, options)
</script>
</body>
</html>
'''

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

p = GraphPendulum(.5, 20)
p.load_calibration()
try:
    p.process()
except KeyboardInterrupt:
    p.exit()
    print

print html % (p.graph_data('t'), p.graph_data('x'), p.graph_data('y'), p.graph_data('z'))
print otherHTMLGuff
