import csv
import sys, os
import time
import datetime as dt
import serial
import numpy as np
from PyQt5.QtCore import Qt, QThread, pyqtSignal, pyqtSlot, QModelIndex, QObject, QTimer
from PyQt5.QtWidgets import *
from PyQt5.QtGui import * 
import pyqtgraph as pg
from pyqtgraph import PlotWidget, AxisItem, ViewBox
from serial import SerialException
from pathlib import Path

import random
from mainwindow import Ui_MainWindow
from PyQt5.QtSerialPort import QSerialPort, QSerialPortInfo



#https://realpython.com/python-pyqt-qthread/
#https://www.pythonguis.com/tutorials/multithreading-pyqt-applications-qthreadpool/
class DateAxisItem(AxisItem):
    def __init__(self, *args, **kwargs):
        AxisItem.__init__(self, *args, **kwargs)

    def tickStrings(self, values, scale, spacing):
        return [dt.datetime.fromtimestamp(value).strftime("%H:%M:%S\n%Y-%m-%d\n\n") for value in values]

class Hum_Worker(QThread):
    result = pyqtSignal(str, float, float, float)
    def __init__(self):
        super().__init__()
        #self.ser = None
        self.is_running = True
        #self.port = port
        print("Starting Serial")
    def run(self):
        timestamp = 'time'
        HUM = 67.3
        TMP = 7.2
        DEW = 9.8
        while self.is_running:
            self.result.emit(timestamp, HUM, TMP, DEW)
            time.sleep(5)

class Temp_Worker(QThread):
    result = pyqtSignal(str, tuple)
    
    def __init__(self, port, interval, baud):
        super().__init__()
        self.ser = None
        self.is_running = True
        self.port = port
        self.interval = interval
        self.baud = baud
        
        self.READ_BIT_INHEX = 74
        self.READ_BIT = 37
        self.MAX_TEMP = 18000 #1800C to determine negative val
        print("Starting Serial")

    """
    def run(self):
        try:
            self.ser = serial.Serial(self.port, self.baud, timeout=10000)
            hex_data = [0x01, 0x16, 0x7B, 0x28, 0x48, 0x4C, 0x45, 0x48, 0x54, 0x43, 0x34, 0x30, 0x39, 0x35, 0x67, 0x71, 0x29, 0x7D, 0x7E, 0x04]
            byte_data = bytearray(hex_data)
            while self.is_running:
                write_time1 = dt.datetime.now()
                interval_dt = dt.timedelta(seconds = self.interval) 
                write_time2 = write_time1 + interval_dt
                while dt.datetime.now() <= write_time2:
                    pass
                self.ser.write(byte_data)
                time.sleep(0.1)
                if self.ser.in_waiting:
                    response = self.ser.read(self.READ_BIT)
                    if response:
                        temperatures = parse_temp(self,response)
                        now_time = dt.datetime.now()
                        current_time = str(now_time.strftime('%Y%m%dT%H%M%S.%f')[:-3])  
                        print(f"Time: {current_time}, Temperatures: {temperatures}")
                        self.result.emit(current_time, temperatures)
                    else:
                        print("No response")

        except serial.SerialException as e:
            print(f"Serial error: {e}")
        finally:
            if self.ser:
                self.ser.close()
    """
    def run(self):
        while self.is_running:
            temperatures = test_temp()
            current_time = str(dt.datetime.now().strftime('%Y%m%dT%H%M%S.%f'))
            print(f"Time: {current_time}, Temperatures: {temperatures}")
            self.result.emit(current_time, temperatures)
            time.sleep(5)
    def stop(self):
        self.is_running = False
        if self.ser:
            self.ser.close()
        self.quit()
        self.wait()

def hex_dec(self, T_hex):
    try:
        T_val = int(T_hex, 16)
        T_max = self.MAX_TEMP
        hex_max = 0xFFFF
        if T_val > T_max:
            T = -(hex_max - T_val + 1) / 10
        else:
            T = T_val / 10
        return T
    except ValueError:
        return 'err'
def test_temp():
    temperatures = []
    for i in range(8):
        temperatures.append(random.randint(500, 4000))
    return tuple(temperatures)
        
def parse_temp(self, response):
    response_hex = response.hex()
    if len(response_hex) < self.READ_BIT_INHEX:
        return tuple('err' for _ in range(8))
    temperatures = []
    for i in range(8):
        hex_str = response_hex[34 + i*4:36 + i*4] + response_hex[32 + i*4:34 + i*4]
        temperatures.append(hex_dec(self,hex_str))
    return tuple(temperatures)

class PurifierModel(QObject):
    dataChanged = pyqtSignal()

    def __init__(self, parent=None):
        super(PurifierModel, self).__init__(parent)
        self.data = []

    def lenData(self, parent=QModelIndex()):
        return len(self.data)

    def appendData(self, time, *temps):
        self.data.append((time,) + temps)
        self.dataChanged.emit()

    def clearData(self):
        self.data = []
        self.dataChanged.emit()

    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            row = index.row()
            return self.data[row]

    def reset(self):
        self.data = []
        return None

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowIcon(QIcon('logo.png'))
        self.worker1 = None
        self.worker2 = None
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.startStopButton.pressed.connect(self.toggleRun)
        self.ui.clearButton.pressed.connect(self.clearPlot)
        self.ui.LogButton.pressed.connect(self.startLogging)
        self.ui.refreshButton.pressed.connect(self.refreshSerialPorts)
        self.ui.saveDirectoryButton.pressed.connect(self.chooseSaveDirectory)

        self.model = PurifierModel()
        self.initGraph()
        self.filename = None
        self.serialPort = None
        self.saveDirectory = None
        self.interval = 2 #2 sec default
        self.baud = 38400 #38400 default
        
    def initFile(self):
        now = dt.datetime.now()
        self.filename = "temp_log_" + str(now.strftime('%Y%m%dT%H%M%S')) + ".csv"
        try:
            with open(f"{self.saveDirectory}/{self.filename}", 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(['Time', 'T1', 'T2', 'T3', 'T4', 'T5', 'T6', 'T7', 'T8'])
        except Exception as e:
            print(f"Error opening file: {e}")

    def initGraph(self):
        self.ui.graphWidget.setBackground("w")
        styles = {"color": "black", "font-size": "18px"}
        self.ui.graphWidget.setLabel("left", "Temperature (°C)", **styles)
        self.ui.graphWidget.setLabel("bottom", "Time", **styles)
        self.ui.graphWidget.getAxis('bottom').setStyle(tickTextOffset=10)
        self.ui.graphWidget.setAxisItems({'bottom': DateAxisItem(orientation='bottom')})
        self.ui.graphWidget.showGrid(x=True, y=True, alpha=0.4)
        self.time = []
        self.data = [[] for _ in range(8)]
        self.plotLines = []
        self.colors = [(183, 101, 224), (93, 131, 212), (49, 205, 222), (36, 214, 75), (214, 125, 36), (230, 78, 192), (209, 84, 65), (0, 184, 245)]
        for i in range(8):
            plot_line = self.ui.graphWidget.plot(self.time, self.data[i], pen=pg.mkPen(color=self.colors[i], width=2))
            self.plotLines.append(plot_line)

    def toggleRun(self):
        if self.worker1 is not None:
            self.stopRun()
        else:
            self.startRun()

    def startRun(self):
        self.serialPort = self.ui.ComboBox_1.currentText()
        self.baud = int(self.ui.ComboBox_2.currentText())
        """
        if 'COM' not in self.serialPort:
            self.serialPort = "/dev/" + self.ui.ComboBox_1.currentText()
        """
        print(f"Connected to: {self.serialPort}")
        print(f"Set baud rate to: {self.baud}")
        
        if self.serialPort is None:
            print(self, "No port selected")
            return
            
        try:
            self.interval = int(self.ui.intervalInput.text())
            print(f"Using input interval: {self.interval} seconds")
        except ValueError:
            print("Using default interval: 2 seconds")
            self.interval = 2

        try:
            self.worker1 = Temp_Worker(self.serialPort, self.interval, self.baud)
            self.worker1.result.connect(self.updateData)
            self.worker1.start()
            print("Starting Temp_Worker")

            self.worker2 = Hum_Worker()
            self.worker2.result.connect(self.updateHum)
            self.worker2.start()
            
        except serial.SerialException as e:
            print(f"Could not open serial port: {e}")
            self.worker1 = None

    def stopRun(self):
        if self.worker1:
            self.worker1.stop()
            self.worker1 = None
            print("Stopping Serial")

    def clearPlot(self):
        self.time = []
        self.data = [[] for _ in range(8)]
        for i in range(8):
            self.plotLines[i].setData(self.time, self.data[i])

    def startLogging(self):
        self.initFile()
        self.ui.fileLabel.setText(f"{self.saveDirectory}/{self.filename}")
 
    def refreshSerialPorts(self):
        self.ui.ComboBox_1.clear()
        ports = QSerialPortInfo.availablePorts()
        for port in ports:
            self.ui.ComboBox_1.addItem(port.portName())

    def chooseSaveDirectory(self):
        self.saveDirectory = QFileDialog.getExistingDirectory(self, "Save Directory")
        if self.saveDirectory:
            self.ui.fileLabel.setText(f"{self.saveDirectory}")

    @pyqtSlot(str, tuple)
    def updateData(self, current_time, temperatures):
        for i in range(8):
            if temperatures[i] != 'err':
                self.ui.labels[i].setText(f"T{i + 1}: {temperatures[i]:.1f}")
            else:
                self.ui.labels[i].setText(f"T{i + 1}: err")

        active_ch = tuple(temperatures[i] if self.ui.checkboxes[i].isChecked() else np.nan for i in range(8))
        self.model.appendData(current_time, *active_ch)

        formattime = dt.datetime.strptime(current_time, '%Y%m%dT%H%M%S.%f').timestamp()
        self.time.append(formattime)

        for i in range(8):
            self.data[i].append(temperatures[i])
            if self.ui.checkboxes[i].isChecked():
                self.plotLines[i].setData(self.time, self.data[i])

        if self.filename:
            self.LogData(current_time, temperatures)


    def LogData(self, timestamp, temperatures):
        try:
            with open(f"{self.saveDirectory}/{self.filename}", 'a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([timestamp] + list(temperatures))
        except Exception as e:
            print(f"Error writing to file: {e}")

    @pyqtSlot(str, float, float, float)
    def updateHum(self,timestamp, HUM, TMP, DEW):
        print(timestamp,HUM,TMP,DEW)
    
app = QApplication(sys.argv)
path = os.path.join(os.path.dirname(sys.modules[__name__].__file__), 'logo.png')
app.setWindowIcon(QIcon(path))
window = MainWindow()
window.show()
app.exec_()
