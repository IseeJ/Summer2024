import sys
import logging
import time
from datetime import datetime
import serial
import numpy as np
from PyQt5.QtCore import Qt, QThread, pyqtSignal, pyqtSlot, QModelIndex, QObject
from PyQt5.QtWidgets import (
    QApplication,
    QCheckBox,
    QLabel,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
)

import pyqtgraph as pg
from pyqtgraph import PlotWidget


logging.basicConfig(format="%(message)s", level=logging.INFO)


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
            self.start_time = datetime.now()
            while self.is_running:
                self.ser.write(byte_data)
                time.sleep(2)
                response = self.ser.readline()
                if response:
                    response_hex = response.hex()
                    current_time = (datetime.now() - self.start_time).seconds / 60
                    temperatures = parse_temp(response)
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


class Window(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.worker = None
        self.setupUi()

    def setupUi(self):
        self.setWindowTitle("Temperature")
        self.resize(400, 300)
        self.centralWidget = QWidget()
        self.setCentralWidget(self.centralWidget)

        self.labels = []
        self.checkboxes = []
        self.plotWidget = PlotWidget()
        self.model = PurifierModel()

        layout = QVBoxLayout()

        # checkboxes for 8 channels                                                                                              
        for i in range(8):
            h_layout = QHBoxLayout()
            checkbox = QCheckBox()
            checkbox.setChecked(True)
            self.checkboxes.append(checkbox)
            label = QLabel(f"T{i + 1}: --")
            label.setAlignment(Qt.AlignCenter)
            self.labels.append(label)
            h_layout.addWidget(checkbox)
            h_layout.addWidget(label)
            layout.addLayout(h_layout)

        layout.addWidget(self.plotWidget)
        self.startBtn = QPushButton("Start")
        self.startBtn.clicked.connect(self.startTask)
        layout.addWidget(self.startBtn)

        self.stopBtn = QPushButton("Stop")
        self.stopBtn.clicked.connect(self.stopTask)
        self.stopBtn.setEnabled(False)
        layout.addWidget(self.stopBtn)

        self.centralWidget.setLayout(layout)

        # set up plots                                                                                                           
        self.time = []
        self.data = [[] for _ in range(8)]
        self.plotLines = []

        colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0),
                  (255, 0, 255), (0, 255, 255), (128, 0, 0), (0, 128, 0)]

        for i in range(8):
            plot_line = self.plotWidget.plot(self.time, self.data[i], pen=pg.mkPen(color=colors[i], width=2))
            self.plotLines.append(plot_line)

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

    def clearPlot(self):
        self.model.reset()
        self.plotData()

    @pyqtSlot(float, tuple)
    def updateData(self, current_time, temperatures):
        # update temp on one that is checked                                                                                     
        for i in range(8):
            if self.checkboxes[i].isChecked():
                if temperatures[i] != 'err':
                    self.labels[i].setText(f"T{i + 1}: {temperatures[i]:.1f}")
                else:
                    self.labels[i].setText(f"T{i + 1}: --")
            else:
                self.labels[i].setText(f"T{i + 1}: --")

        # store data to PurifierModel only for checked boxes                                                                     
        active_ch = tuple(temperatures[i] if self.checkboxes[i].isChecked() else 'err' for i in range(8))
        self.model.appendData(current_time, *active_ch)

        # add plots...using data stored in PurifierModel                                                                         
        self.time.append(current_time)
        for i in range(8):
            if self.checkboxes[i].isChecked():
                self.data[i].append(temperatures[i])
                self.plotLines[i].setData(self.time, self.data[i])


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec_())
