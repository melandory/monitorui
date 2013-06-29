from PyQt4.QtCore import *
from PyQt4.Qt import QColor, QPalette
import PyQt4.QtGui as QtGui
import PyQt4.Qwt5 as Qwt
from PyQt4.Qwt5 import QwtDial
from multiprocessing import Process, Queue
from datastream import DataStream
import collections
import sys
from monitor_ui import Ui_MainWindow
from datetime import datetime

#PING PACKET ID=27 TAG=00:11:C5:49 RDR=00:11:C5:45 T=28.02 Lqi=213
HOST="localhost"
PORT=1111
TAGS = 5
MAX_ITEMS_FOR_TAG = 100

COLORS =  collections.deque(((QtGui.QColor('green'), QtGui.QColor('white'), QtGui.QColor('yellow'),\
                              QtGui.QColor('red'), QtGui.QColor('blue'), QtGui.QColor('cyan'))))

class LqiDial(Qwt.QwtDial):
    def __init__(self, *args):
        Qwt.QwtDial.__init__(self, *args)
        self.__label = 'lqi'
        self.setWrapping(False)
        self.setReadOnly(True)

        self.setOrigin(135.0)
        self.setScaleArc(0.0, 270.0)
        self.setRange(0.0, 240.0)
        self.setScale(-1, 2, 20)

        self.setNeedle(Qwt.QwtDialSimpleNeedle(
            Qwt.QwtDialSimpleNeedle.Arrow,
            True,
            QColor(Qt.red),
            QColor(Qt.gray).light(130)))

        self.setScaleOptions(QwtDial.ScaleTicks | QwtDial.ScaleLabel)
        self.setScaleTicks(0, 4, 8)

    def setLabel(self, text):
        self.__label = text
        self.update()

    def label(self):
        return self.__label

    def drawScaleContents(self, painter, center, radius):
        rect = QRect(0, 0, 2 * radius, 2 * radius - 10)
        rect.moveCenter(center)
        painter.setPen(self.palette().color(QPalette.Text))
        painter.drawText(
            rect, Qt.AlignBottom | Qt.AlignHCenter, self.__label)

class TagDataCurve:
    def __init__(self, name, plot, layout, N):
        self.name = name
        self.time = collections.deque()
        self.temp = collections.deque()

        self.curve = Qwt.QwtPlotCurve('')
        self.curve.setStyle(Qwt.QwtPlotCurve.Dots)
        pen = QtGui.QPen(COLORS.pop())
        pen.setWidth(7)
        self.curve.setPen(pen)
        self.curve.attach(plot)
        self.Dial = LqiDial()
        layout.addWidget(self.Dial, 0, N)

    def append(self, time, temp, lqi):
        global MAX_ITEMS_FOR_TAG
        if len(self.temp) > MAX_ITEMS_FOR_TAG:
            print "Pop"
            self.pop()
        self.time.append(time)
        self.temp.append(temp)
        self.Dial.setValue(lqi)

    def update(self):
        self.curve.setData(list(self.time), list(self.temp))

    def pop(self):
        self.time.popleft()
        self.temp.popleft()

class DataMonitor(Ui_MainWindow, QtGui.QMainWindow):
    def __init__(self, parent=None):
        QtGui.QMainWindow.__init__(self)
        Ui_MainWindow.__init__ (self)

        self.monitor_active = False
        self.tags = collections.defaultdict()

        self.timer = QTimer()

        self.queue = Queue()
        self.datastream = DataStream(self.queue, HOST, PORT)
        self.datastreamProcess = Process(target=self.datastream.serve)
        self.datastreamProcess.start()
        self.new_data = []
        self.start_time = datetime.now()

    def __del__(self):
        self.datastreamProcess.terminate()

    def setupUi(self, MainWindow):
        super(DataMonitor, self).setupUi(MainWindow)
        global TAGS
        #setup thermo
        self.Thermo.setFillColor(Qt.green)
        self.Thermo.setAlarmColor(Qt.red)
        #setup plot
        self.qwtPlot.setCanvasBackground(Qt.black)
        self.qwtPlot.setAxisTitle(Qwt.QwtPlot.xBottom, 'Time')
        self.qwtPlot.setAxisScale(Qwt.QwtPlot.xBottom, 0, 10, 1)
        self.qwtPlot.setAxisTitle(Qwt.QwtPlot.yLeft, 'Temperature')
        self.qwtPlot.setAxisScale(Qwt.QwtPlot.yLeft, 0, 30, 15)
        self.qwtPlot.replot()
        MainWindow.connect(self.actionStart_plotting, SIGNAL("triggered()"), self.on_start)
        MainWindow.connect(self.actionStop_plotting, SIGNAL("triggered()"), self.on_stop)
        MainWindow.connect(self.actionExit, SIGNAL("triggered()"), MainWindow.close)

    def set_actions_enable_state(self):
        start_enable = not self.monitor_active
        stop_enable = self.monitor_active

        self.actionStart_plotting.setEnabled(start_enable)
        self.actionStop_plotting.setEnabled(stop_enable)

    def on_stop(self):
        self.monitor_active = False
        self.timer.stop()
        self.set_actions_enable_state()

    def on_start(self):
        self.monitor_active = True
        self.set_actions_enable_state()

        self.timer = QTimer()
        self.connect(self.timer, SIGNAL('timeout()'), self.plot_new_data)
        self.timer.start(7000)

    def plot_new_data(self):
        new_data = []
        while not self.queue.empty():
            item = self.queue.get_nowait()
            new_data.append(item)
        if new_data:
            for item in new_data:
                if item['TAG'] not in self.tags.keys():
                    self.tags[item['TAG']] = TagDataCurve(item['TAG'], 
                                                          self.qwtPlot, 
                                                          self.lqiLayout, 
                                                          len(self.tags.keys()))
                self.tags[item['TAG']].append((datetime.strptime(item['TIME'], "%Y-%m-%d %H:%M:%S.%f") - self.start_time).total_seconds(), 
                                              float(item['T']), int(item['LQI']))
            self.max_temp=0
            self.min_time=sys.maxint
            self.max_time=0.
            for t in self.tags.keys():
                self.min_time = min(self.min_time, min(self.tags[t].time))
                self.max_time = max(self.max_time, max(self.tags[t].time))
                self.max_temp = max(self.max_temp, max(self.tags[t].temp))
                self.tags[t].update()
            print self.min_time, self.max_time
            self.qwtPlot.setAxisScale(Qwt.QwtPlot.xBottom, self.min_time, self.max_time)
            self.qwtPlot.replot()

            self.Thermo.setValue(self.max_temp)

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    form = DataMonitor()
    form.setupUi(form)
    form.show()
    sys.exit(app.exec_())

