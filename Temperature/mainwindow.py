from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtGui import * 


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        self.setWindowTitle("Temperature")
        self.resize(500, 800)
        self.centralWidget = QWidget()
        self.setCentralWidget(self.centralWidget)

        self.labels = []
        self.checkboxes = []
        self.plotWidget = PlotWidget()
        self.plotWidget.setBackground('w')
        #model
        self.model = PurifierModel()
        layout = QVBoxLayout()
        #colors for each channels
        colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255), (0, 255, 255), (128, 0, 0), (0, 128, 0)]
        
        #checkboxes for 8 channels
    
        for i in range(8):
            h_layout = QHBoxLayout()
            checkbox = QCheckBox()
            checkbox.setChecked(True)
            self.checkboxes.append(checkbox)
            label = QLabel(f"T{i + 1}: --")
            label.setStyleSheet(f"background-color: rgb{colors[i]}; border: 1px solid black;")
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

        #set up plots
        styles = {"color": "red", "font-size": "18px"}
        self.plotWidget.setLabel("left", "Temperature (°C)", **styles)
        self.plotWidget.setLabel("bottom", "Unix Time", **styles)

        
        self.time = []
        self.data = [[] for _ in range(8)]
        self.plotLines = []
        for i in range(8):
            plot_line = self.plotWidget.plot(self.time, self.data[i], pen=pg.mkPen(color=colors[i], width=2))
            self.plotLines.append(plot_line)

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())B
