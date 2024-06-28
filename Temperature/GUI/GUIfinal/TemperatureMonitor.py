import csv
import sys
import logging
import time
from datetime import datetime as dt
import serial
import numpy as np
from PyQt5.QtCore import Qt, QThread, pyqtSignal, pyqtSlot, QModelIndex, QObject, QTimer
from PyQt5.QtWidgets import *
from PyQt5.QtGui import * 
import pyqtgraph as pg
from pyqtgraph import PlotWidget, AxisItem
from serial import SerialException

from mainwindow import Ui_MainWindow
from PyQt5.QtSerialPort import QSerialPort, QSerialPortInfo

logging.basicConfig(format="%(message)s", level=logging.INFO)

class DateAxisItem(AxisItem):
    def __init__(self, *args, **kwargs):
        AxisItem.__init__(self, *args, **kwargs)

    def tickStrings(self, values, scale, spacing):
        return [dt.fromtimestamp(value).strftime("%H:%M:%S") for value in values]

class Worker(QThread):
    result = pyqtSignal(str, tuple)

    def __init__(self, port):
        super().__init__()
        self.ser = None
        self.is_running = True
        self.port = port
        logging.info("Serial Start")

    def run(self):
        try:
            self.ser = serial.Serial(self.port, 38400, timeout=5)
            hex_data = [0x01, 0x16, 0x7B, 0x28, 0x48, 0x4C, 0x45, 0x48, 0x54, 0x43, 0x34, 0x30, 0x39, 0x35, 0x67, 0x71, 0x29, 0x7D, 0x7E, 0x04]
            byte_data = bytearray(hex_data)
            while self.is_running:
                self.ser.write(byte_data)
                time.sleep(0.1)
                if self.ser.in_waiting == 37:
                    response = self.ser.readline()
                    if response:
                        temperatures = parse_temp(response)
                        current_time = str(dt.now().strftime('%H:%M:%S'))  
                        logging.info(f"Time: {current_time}, Temperatures: {temperatures}")
                        self.result.emit(current_time, temperatures)
                    else:
                        logging.warning("No response")
        except serial.SerialException as e:
            logging.error(f"Serial error: {e}")
        finally:
            if self.ser:
                self.ser.close()
            logging.info("Serial stop")

    def stop(self):
        self.is_running = False
        if self.ser:
            self.ser.close()
        self.quit()
        self.wait()

def hex_dec(T_hex):
    try:
        T_val = int(T_hex, 16)
        T_max = 18000
        hex_max = 0xFFFF
        if T_val > T_max:
            T = -(hex_max - T_val + 1) / 10
        else:
            T = T_val / 10
        return T
    except ValueError:
        return 'err'

def parse_temp(response):
    response_hex = response.hex()
    if len(response_hex) < 72:
        return tuple('err' for _ in range(8))
    temperatures = []
    for i in range(8):
        hex_str = response_hex[34 + i*4:36 + i*4] + response_hex[32 + i*4:34 + i*4]
        temperatures.append(hex_dec(hex_str))
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
        self.worker = None
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.startStopButton.pressed.connect(self.toggleRun)
        self.ui.clearButton.pressed.connect(self.clearPlot)
        self.ui.LogButton.pressed.connect(self.startLogging)
        self.ui.ConnectButton.pressed.connect(self.applySerialPort)
        self.ui.refreshButton.pressed.connect(self.refreshSerialPorts)
        self.ui.saveDirectoryButton.pressed.connect(self.chooseSaveDirectory)
        self.model = PurifierModel()
        self.initGraph()
        self.filename = None
        self.serialPort = None
        self.saveDirectory = None

    def initFile(self):
        now = dt.now()
        self.filename = "temp_log_" + str(now.strftime('%Y%m%d%H%M')) + ".csv"
        try:
            with open(f"{self.saveDirectory}/{self.filename}", 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(['Time', 'T1', 'T2', 'T3', 'T4', 'T5', 'T6', 'T7', 'T8'])
        except Exception as e:
            logging.error(f"Error opening file: {e}")

    def initGraph(self):
        self.ui.graphWidget.setBackground("w")
        styles = {"color": "red", "font-size": "18px"}
        self.ui.graphWidget.setLabel("left", "Temperature (°C)", **styles)
        self.ui.graphWidget.setLabel("bottom", "Time", **styles)
        self.ui.graphWidget.getAxis('bottom').setStyle(tickTextOffset=10)
        self.ui.graphWidget.setAxisItems({'bottom': DateAxisItem(orientation='bottom')})
        self.time = []
        self.data = [[] for _ in range(8)]
        self.plotLines = []
        self.colors = [(183, 101, 224), (93, 131, 212), (49, 205, 222), (36, 214, 75), (214, 125, 36), (230, 78, 192), (209, 84, 65), (0, 184, 245)]
        for i in range(8):
            plot_line = self.ui.graphWidget.plot(self.time, self.data[i], pen=pg.mkPen(color=self.colors[i], width=2))
            self.plotLines.append(plot_line)

    def toggleRun(self):
        if self.worker is not None:
            self.stopRun()
        else:
            self.startRun()

    def startRun(self):
        if self.serialPort is None:
            QMessageBox.warning(self, "Warning", "Please select serial port")
            return
        try:
            self.worker = Worker(self.serialPort)
            self.worker.result.connect(self.updateData)
            self.worker.start()
            logging.info("Start serial")
        except serial.SerialException as e:
            QMessageBox.critical(self, "Error", f"Could not open serial port: {e}")
            logging.error(f"Could not open serial port: {e}")
            self.worker = None


    def stopRun(self):
        if self.worker:
            self.worker.stop()
            self.worker = None
            logging.info("Stop serial")

    def clearPlot(self):
        self.time = []
        self.data = [[] for _ in range(8)]
        for i in range(8):
            self.plotLines[i].setData(self.time, self.data[i])

    def startLogging(self):
        self.initFile()
        self.ui.fileLabel.setText(f"{self.saveDirectory}/{self.filename}")

    def applySerialPort(self):
        self.serialPort = "/dev/" + self.ui.ComboBox_1.currentText()
        logging.info(f"Connected to: {self.serialPort}")

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

        formattime = dt.strptime(current_time, '%H:%M:%S').timestamp()
        self.time.append(formattime)

        for i in range(8):
            self.data[i].append(temperatures[i])
            if self.ui.checkboxes[i].isChecked():
                self.plotLines[i].setData(self.time, self.data[i])

        if self.filename:
            self.LogData(formattime, temperatures)

    def LogData(self, timestamp, temperatures):
        try:
            with open(f"{self.saveDirectory}/{self.filename}", 'a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([timestamp] + list(temperatures))
        except Exception as e:
            logging.error(f"Error writing to file: {e}")

app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec_()
