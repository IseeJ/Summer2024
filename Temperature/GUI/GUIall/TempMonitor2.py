import csv
import sys
import logging
import time
from datetime import datetime as dt
import serial
import numpy as np
from PyQt5.QtCore import Qt, QThread, pyqtSignal, pyqtSlot, QModelIndex, QObject
import time
#from PyQt5.QtWidgets import (QApplication,QCheckBox,QLabel,QMainWindow,QPushButton,QVBoxLayout,QHBoxLayout,QWidget)

from PyQt5.QtWidgets import *
from PyQt5.QtGui import * 
import pyqtgraph as pg
from pyqtgraph import PlotWidget

from mainwindow import Ui_MainWindow


from PyQt5.QtSerialPort import QSerialPort, QSerialPortInfo

logging.basicConfig(format="%(message)s", level=logging.INFO)

#https://realpython.com/python-pyqt-qthread/
#https://www.pythonguis.com/tutorials/multithreading-pyqt-applications-qthreadpool/

class Worker(QThread):
    result = pyqtSignal(float, tuple)

    #start serial com
    def __init__(self, port):
        super().__init__()
        self.ser = serial.Serial(port, 38400, timeout=10)
        self.is_running = True
        logging.info("Serial Start")
        #self.start_time = None
    
    def run(self):
        try:
            hex_data = [0x01, 0x16, 0x7B, 0x28, 0x48, 0x4C, 0x45, 0x48, 0x54, 0x43, 0x34, 0x30, 0x39, 0x35, 0x67, 0x71, 0x29, 0x7D, 0x7E, 0x04]
            byte_data = bytearray(hex_data)
            #self.start_time = datetime.now()
            while self.is_running:
                self.ser.write(byte_data)
                time.sleep(0.1)
                #if signal recieved (ser.in_waiting should be 37 bits), read it
                if self.ser.in_waiting ==37:
                    response = self.ser.readline()
                    if response:
                        response_hex = response.hex()
                        temperatures = parse_temp(response)

                        #Unixtime
                        current_time = time.time()
                        #datetime
                        #current_time = dt.now()
                        logging.info(f"Time: {current_time}, Temperatures: {temperatures}")
                        self.result.emit(current_time, temperatures)
                    else:
                        logging.warning("No response")
        except serial.SerialException as e:
            logging.error("Error")
        finally:
            self.ser.close()
            logging.info("Serial stop")

    def stop(self):
        self.is_running = False
        self.ser.close()
        self.quit()
        self.wait()
def hex_dec(T_hex):
    try:
        T_val = int(T_hex, 16)
        T_max = 18000  # 1800C is max (from Omega data sheet), use as threshold to check that the hex is neg
        hex_max = 0xFFFF  # FFFF max
        if T_val > T_max:
            T = -(hex_max - T_val + 1) / 10  # handling negative value
        else:
            T = T_val / 10
        return T
    except ValueError:
        return 'err'
def parse_temp(response):
    response_hex = response.hex()
    temperatures = []
    for i in range(8):
        hex_str = response_hex[34+i*4:36+i*4] + response_hex[32+i*4:34+i*4]
        temperatures.append(hex_dec(hex_str))
    return tuple(temperatures)

class PurifierModel(QObject):
    def __init__(self, parent=None):
        super(PurifierModel, self).__init__(parent)
        self.data = []  # to hold tuple
        
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

    dataChanged = pyqtSignal()

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.worker = None
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        #connect buttons to functions
        self.ui.startStopButton.pressed.connect(self.toggleRun)
        self.ui.clearButton.pressed.connect(self.clearPlot)
        
        #self.ui.actionSave.triggered.connect(self.savefile)

        self.ui.LogButton.pressed.connect(self.startLogging)

        self.ui.ConnectButton.pressed.connect(self.applySerialPort)
        self.ui.refreshButton.pressed.connect(self.refreshSerialPorts)

        self.ui.saveDirectoryButton.pressed.connect(self.chooseSaveDirectory)

        
        self.model = PurifierModel()
        self.initGraph()
        #self.initFile()

        self.filename = None
        self.serialPort = None
        self.saveDirectory = None
    #log file while running
    def initFile(self):
        now = dt.now()
        self.filename = "temp_log_" + str(now.strftime('%Y%m%d%H%M')) + ".csv"
        with open(f"{self.saveDirectory}/{self.filename}", 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Time', 'T1', 'T2', 'T3', 'T4', 'T5', 'T6', 'T7', 'T8'])

    def initGraph(self):
        #set up plots
        self.ui.graphWidget.setBackground("w")
        styles = {"color": "red", "font-size": "18px"}
        self.ui.graphWidget.setLabel("left", "Temperature (°C)", **styles)
        self.ui.graphWidget.setLabel("bottom", "Unix Time", **styles)
        
        self.time = []
        self.data = [[] for _ in range(8)]
        self.plotLines = []

        self.colors = [(183, 101, 224), (93, 131, 212), (49, 205, 222), (36, 214, 75), (214, 125, 36) ,(230, 78, 192), (209, 84, 65), (0, 184, 245)]
        for i in range(8):
            plot_line = self.ui.graphWidget.plot(self.time, self.data[i], pen=pg.mkPen(color=self.colors[i], width=2))
            self.plotLines.append(plot_line)

    def toggleRun(self):
        if self.worker is not None:
            self.stopRun()
        else:
            self.startRun()
    def startRun(self):
        self.worker = Worker(self.serialPort)
        self.worker.result.connect(self.updateData)
        self.worker.start()
        print("Start serial")
    def stopRun(self):
        if self.worker:
            self.worker.stop()
            self.worker = None
    #**need fixing
    def clearPlot(self):
        #self.model.reset()
        #self.plotLines = []
        self.time = []
        self.data = [[] for _ in range(8)]
        for i in range(8):
            self.plotLines[i].setData(self.time, self.data[i])

    """
    def savefile(self):
        now = dt.now()
        self.filename = "temp_log_"+str(now.strftime('%Y%m%d%H%M'))+".csv"
        print(f"Saved to {self.filename}")
    """

    def startLogging(self):
        self.initFile()
        """
        self.saveDirectory = QFileDialog.getExistingDirectory(self, "Choose Save Directory")
        if self.saveDirectory:
            self.ui.fileLabel.setText(f"Writing to: {self.saveDirectory}/{self.filename}")
        """
        self.ui.fileLabel.setText(f"{self.saveDirectory}/{self.filename}")
    #get serial Port
    def applySerialPort(self):
        self.serialPort = self.ui.ComboBox_1.currentText()
        print(f"Connected to: {self.serialPort}")

    def refreshSerialPorts(self):
        self.ui.ComboBox_1.clear()
        ports = QSerialPortInfo.availablePorts()
        for port in ports:
            self.ui.ComboBox_1.addItem(port.portName())


    def chooseSaveDirectory(self):
        self.saveDirectory = QFileDialog.getExistingDirectory(self, "Save Directory")
        if self.saveDirectory:
            self.ui.fileLabel.setText(f"{self.saveDirectory}")
            
    #slot: to get from signal where time and temperatures are (float, tuple) types must match
    """
    @pyqtSlot(float, tuple)
    def updateData(self, current_time, temperatures):
        formattime = dt.fromtimestamp(current_time)
        time_str = formattime.strftime('%H:%M:%S')
        # update temp on one that is checked
        for i in range(8):
            if self.ui.checkboxes[i].isChecked():
                if temperatures[i] != 'err':
                    self.ui.labels[i].setText(f"T{i + 1}: {temperatures[i]:.1f}")
                else:
                    self.ui.labels[i].setText(f"T{i + 1}: {temperatures[i]:.1f}")
            else:
                self.ui.labels[i].setText(f"T{i + 1}: --")
       
        #need fixing, separate data storage from plotting? in case we need to save data still but doesn't need to show plots
        #store data to PurifierModel only for checked boxes, for inactive channels, just put nan so nothing is being append to the model (not saving those data)
        active_ch = tuple(temperatures[i] if self.ui.checkboxes[i].isChecked() else np.nan for i in range(8))
        self.model.appendData(current_time, *active_ch)

        #active_ch = tuple(temperatures[i] for i in range(8))
        #self.model.appendData(current_time, *active_ch) 
        #add plots...using data stored in PurifierModel
        self.time.append(current_time)
        
        for i in range(8):
            #plot the active channels
            if self.ui.checkboxes[i].isChecked():
                self.data[i].append(temperatures[i])
                self.plotLines[i].setData(self.time, self.data[i])
            else:
                #self.data[i].append(np.nan) #remove this, unless no data is stored
                self.data[i].append(temperatures[i]) #store data but just not showing plot


        self.LogData(current_time, temperatures)
    """
    @pyqtSlot(float, tuple)
    def updateData(self, current_time, temperatures):
        #formattime to hr:mm:ss
        formattime = dt.fromtimestamp(float(current_time)).strftime('%H:%M:%S')

        for i in range(8):
            if temperatures[i] != 'err':
                self.ui.labels[i].setText(f"T{i + 1}: {temperatures[i]:.1f}")
            else:
                self.ui.labels[i].setText(f"T{i + 1}: err")

        self.model.appendData(formattime, *temperatures)
        self.time.append(formattime)
        for i in range(8):
            if self.ui.checkboxes[i].isChecked():
                self.data[i].append(temperatures[i])
            else:
                self.data[i].append(np.nan)
            self.plotLines[i].setData(self.time, self.data[i] if self.ui.checkboxes[i].isChecked() else [])

        #refresh view
        self.ui.graphWidget.setXRange(self.time[0], self.time[-1], padding=0.1)

    def LogData(self, current_time, temperatures):
        with open(self.filename, 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([current_time] + list(temperatures))

app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec_()
