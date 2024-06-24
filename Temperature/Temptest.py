import sys
import logging
import time
from datetime import datetime as dt
import serial
import numpy as np
from PyQt5.QtCore import Qt, QThread, pyqtSignal, pyqtSlot, QObject
from PyQt5.QtWidgets import *
from PyQt5.QtGui import * 
import pyqtgraph as pg
from pyqtgraph import PlotWidget

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

class Worker(QThread):
    result = pyqtSignal(float, tuple)

    def __init__(self):
        super().__init__()
        self.ser = serial.Serial('/dev/cu.usbserial-110', 38400, timeout=2)
        self.is_running = True
        logging.info("Serial Start")
        self.start_time = None
        
    def run(self):
        try:
            hex_data = [0x01, 0x16, 0x7B, 0x28, 0x48, 0x4C, 0x45, 0x48, 0x54, 0x43, 0x34, 0x30, 0x39, 0x35, 0x67, 0x71, 0x29, 0x7D, 0x7E, 0x04]
            byte_data = bytearray(hex_data)
            while self.is_running:
                self.ser.write(byte_data)
                time.sleep(0.1)
                if self.ser.in_waiting == 37:
                    response = self.ser.readline()
                    if response:
                        temperatures = parse_temp(response)
                        current_time = time.time()
                        logging.info(f"Time: {current_time}, Temperatures: {temperatures}")
                        self.result.emit(current_time, temperatures)
                    else:
                        logging.warning("No response")
        except serial.SerialException as e:
            logging.error(f"Error: {e}")
        finally:
            self.ser.close()
            logging.info("Serial stop")
        
    def stop(self):
        self.is_running = False
        self.quit()
        self.wait()

def hex_dec(T_hex):
    try:
        T_val = int(T_hex, 16)
        T_max = 18000  # 1800C is max, use as threshold to check that the hex is neg
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
        hex_str = response_hex[34 + i * 4:36 + i * 4] + response_hex[32 + i * 4:34 + i * 4]
        temperatures.append(hex_dec(hex_str))
    return tuple(temperatures)

class MplCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)

class Window(QMainWindow):
    def __init__(self, parent=None):
        super(Window, self).__init__(parent)
        self.worker = None
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Temperature Monitoring")
        self.resize(800, 600)
        self.centralWidget = QWidget()
        self.setCentralWidget(self.centralWidget)
        layout = QVBoxLayout(self.centralWidget)

        self.imageLabel = QLabel()
        pixmap = QPixmap("diagram.png")
        pixmap = pixmap.scaled(800, 600, Qt.KeepAspectRatio)
        self.imageLabel.setPixmap(pixmap)
        self.imageLabel.setScaledContents(True)
        layout.addWidget(self.imageLabel)

        self.overlayWidget = QWidget(self.imageLabel)
        self.overlayWidget.setGeometry(0, 0, 800, 600)
        self.labels = []

        self.label_coordinates = [(430, 420), (450, 780), (470, 1170), (300, 1470), (1600, 730), (1500, 1270), (1140, 1470)]
        colors = [(255, 0, 0), (146, 224, 20), (0, 0, 255), (245, 136, 27), (105, 46, 35), (0, 184, 245), (128, 0, 0), (0, 128, 0)]

        for i in range(7):
            label = QLabel(f"CH{i + 1}: --", self.overlayWidget)
            label.setFont(QFont("Arial", 12, QFont.Bold))
            label.setStyleSheet(f"color: {colors[i]}; background-color: white; border: 1px solid black;")
            label.setAlignment(Qt.AlignCenter)
            label.move(*self.label_coordinates[i])
            self.labels.append(label)

        buttonLayout = QHBoxLayout()

        self.startBtn = QPushButton("Start")
        self.startBtn.clicked.connect(self.startTask)
        buttonLayout.addWidget(self.startBtn)

        self.stopBtn = QPushButton("Stop")
        self.stopBtn.clicked.connect(self.stopTask)
        self.stopBtn.setEnabled(False)
        buttonLayout.addWidget(self.stopBtn)
        layout.addLayout(buttonLayout)

    def startTask(self):
        self.worker = Worker()
        self.worker.result.connect(self.updateData)
        self.worker.start()
        self.startBtn.setEnabled(False)
        self.stopBtn.setEnabled(True)

    def stopTask(self):
        if self.worker:
            self.worker.stop()
            self.worker = None
        self.startBtn.setEnabled(True)
        self.stopBtn.setEnabled(False)

    @pyqtSlot(float, tuple)
    def updateData(self, current_time, temperatures):
        for i in range(7):
            if temperatures[i] != 'err':
                self.labels[i].setText(f"CH{i + 1}: {temperatures[i]:.1f} °C")
            else:
                self.labels[i].setText(f"CH{i + 1}: --")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec_())