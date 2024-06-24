import sys
import logging
import time
from datetime import datetime as dt
import serial
import numpy as np
from PyQt5.QtCore import Qt, QThread, pyqtSignal, pyqtSlot, QModelIndex, QObject

from PyQt5.QtWidgets import *
from PyQt5.QtGui import * 
import pyqtgraph as pg
from pyqtgraph import PlotWidget

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
        hex_str = response_hex[34+i*4:36+i*4] + response_hex[32+i*4:34+i*4]
        temperatures.append(hex_dec(hex_str))
    return tuple(temperatures)
        
#Worker, model, same as before
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
        self.quit()
        self.wait()

class PurifierModel(QObject):
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

    dataChanged = pyqtSignal()


#add image to the plot
class Window(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.worker = None
        self.setupUi()

    def setupUi(self):
        self.setWindowTitle("Temperature")
        self.resize(600,500)
        self.centralWidget = QWidget()
        self.setCentralWidget(self.centralWidget)

        layout = QVBoxLayout(self.centralWidget)

        #****
        self.imageLabel = QLabel()
        pixmap = QPixmap("diagram.png")
        pixmap = pixmap.scaled(400, 300, Qt.KeepAspectRatio)
        self.imageLabel.setPixmap(pixmap)
        self.imageLabel.setScaledContents(True)
        layout.addWidget(self.imageLabel)

        self.overlayWidget = QWidget(self.imageLabel)
        self.overlayWidget.setGeometry(0, 0, 400, 300)
        self.labels = []
        self.label_coordinates = [(50, 50), (150, 50), (250, 50), (350, 50), (50, 150), (150, 150), (250, 150), (350, 150)]

        for i in range(8):
            label = QLabel(f"T{i + 1}: --", self.overlayWidget)
            label.setFont(QFont("Arial", 12, QFont.Bold))
            label.setStyleSheet("color: white;")
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
        for i in range(8):
            if temperatures[i] != 'err':
                self.labels[i].setText(f"T{i + 1}: {temperatures[i]:.1f}")
            else:
                self.labels[i].setText(f"T{i + 1}: --")
app = QApplication(sys.argv)
window = Window()
window.show()
sys.exit(app.exec_())
