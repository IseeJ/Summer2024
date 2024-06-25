import time
import sys
import serial
import json
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtCore import Qt

#from pyqtgraph import PlotWidget, plot
import pyqtgraph as pg

from mainwinui import Ui_MainWindow

import random

class PurifierModel(QtCore.QAbstractListModel):
    def __init__(self, *args, **kwargs):
        super(PurifierModel, self).__init__(*args, **kwargs)

    xdata = []
    ydata = []
        
    def lenData(self):
        return len(self.ydata)

    def appendData(self, x, y):
        self.xdata.append(x)
        self.ydata.append(y)

    def reset(self):
        self.xdata = []
        self.ydata = []

        
class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        # setup user interface from Designer
        # see: https://www.riverbankcomputing.com/static/Docs/PyQt5/designer.html
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        
        self.model = PurifierModel()

        # prepare for serial communication (this should live elsewhere...)
        # i.e. make a class for serial comm to thermocouple device...
        self.ser = None # serial connection (for data retrieval)
        self.port = '/dev/tty.usbmodem1101' # this can be obtained from the GUI
        self.baud = 9600
        self.timeout = 2
        
        # initialize the graphs
        self.initGraph()

        # connect signals/slots
        self.ui.startStopButton.pressed.connect(self.toggleRun)
        self.ui.clearButton.pressed.connect(self.clearPlot)

        self.timer = QtCore.QTimer()
        self.timer.setInterval(1000) # ms
        self.timer.timeout.connect(self.getData)
        
    def initGraph(self):
        #self.ui.graphWidget.setBackground("w")

        # define color for line on graph
        pen = pg.mkPen(color=(255, 0, 0))
        
        self.line = self.ui.graphWidget.getPlotItem().plot(pen=pen)
        self.plotData()

        self.ui.graphWidget.setLabel("left", "y-values [arb.]")
        self.ui.graphWidget.setLabel("bottom", "Time [arb.]")

    def clearPlot(self):
        self.model.reset()
        self.plotData()
        
    def toggleRun(self):
        if self.ser is not None:
            self.stopRun()
        else:
            self.startRun()

    def startRun(self):
        print('starting serial comm')
        # open serial connection
        self.serialOpen()
        # start timer for serial transmission
        self.timer.start()
        
    def stopRun(self):
        print('ending serial comm')
        self.serialClose()
        # stop the timer for serial transmission
        self.timer.stop()

    def serialOpen(self):
        self.ser = serial.Serial(self.port, self.baud, timeout=self.timeout)
        time.sleep(1) # [seconds] necessary only because opening the port reboots the arduino! not needed for actual operation with thermocouple readout

    def serialClose(self):
        self.ser.close()
        self.ser = None
        
    def addPoint(self, xx, yy):
        self.model.appendData(xx, yy)


    def plotData(self):
        self.line.setData(self.model.xdata, self.model.ydata)

    def getData(self):
        # request data from a serial device
        val = random.randint(0,100)
        out = str(val).encode('UTF-8')
        self.ser.write(out)
        self.ser.flush()
        
        # receive response
        time.sleep(1) # may not be needed...
        print('\n')
        print('tx: ',end='')
        print(out)
        rec = self.ser.readline()
        print('rx: ',end='')
        print(rec)
        yy = float(rec.decode('UTF-8'))
        xx = self.model.lenData()
        self.addPoint(xx, yy)
        self.plotData()
        
        
app = QtWidgets.QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec_()


