from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QPixmap, QPainter, QColor, QFont, QImage

class DiagramWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.image = QImage("diagram.png")
        self.image = self.image.scaled(250, 565, QtCore.Qt.KeepAspectRatio)  # Fixed size for the image
        self.labels = [(50, 50, "Label1"), (150, 150, "Label2"), (100, 300, "Label3")]  # Example coordinates and labels
        self.colors = [(183, 101, 224), (93, 131, 212), (49, 205, 222), (36, 214, 75), 
                       (214, 125, 36), (230, 78, 192), (209, 84, 65), (0, 184, 245)]

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawImage(QPoint(0, 0), self.image)
        for i, (x, y, text) in enumerate(self.labels):
            painter.setPen(QColor(*self.colors[i % len(self.colors)]))
            painter.setFont(QFont("Arial", 12, QFont.Bold))
            painter.drawText(x, y, text)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1197, 565)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")

        self.DiagramWidget = DiagramWidget(self.centralwidget)
        self.DiagramWidget.setMaximumSize(QtCore.QSize(250, 565))
        self.DiagramWidget.setObjectName("DiagramWidget")
        self.horizontalLayout.addWidget(self.DiagramWidget)
        
        self.graphWidget = QtWidgets.QWidget(self.centralwidget)  # Placeholder widget
        self.graphWidget.setMinimumSize(QtCore.QSize(348, 0))
        self.graphWidget.setObjectName("PlotWidget")
        self.horizontalLayout.addWidget(self.graphWidget)

        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.checkboxes = []

        self.colors = [(183, 101, 224), (93, 131, 212), (49, 205, 222), (36, 214, 75), 
                       (214, 125, 36), (230, 78, 192), (209, 84, 65), (0, 184, 245)]
        for i in range(8):
            self.checkBox = QtWidgets.QCheckBox(self.centralwidget)
            self.checkBox.setMaximumSize(QtCore.QSize(100, 20))
            self.checkBox.setObjectName(f"T{i+1}")
            self.checkBox.setChecked(True)
            self.verticalLayout_2.addWidget(self.checkBox)
            self.checkBox.setStyleSheet(f"color: white; background-color: rgb{self.colors[i]}; border: 1px solid black;")
            self.checkboxes.append(self.checkBox)

        self.startStopButton = QtWidgets.QPushButton(self.centralwidget)
        self.startStopButton.setMaximumSize(QtCore.QSize(100, 16777215))
        self.startStopButton.setObjectName("startStopButton")
        self.verticalLayout_2.addWidget(self.startStopButton)
        self.clearButton = QtWidgets.QPushButton(self.centralwidget)
        self.clearButton.setMaximumSize(QtCore.QSize(100, 16777215))
        self.clearButton.setObjectName("clearButton")
        self.verticalLayout_2.addWidget(self.clearButton)

        self.labels = []
        self.verticalLayout_4 = QtWidgets.QVBoxLayout()
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        for i in range(8):
            self.label = QtWidgets.QLabel(self.centralwidget)
            self.label.setGeometry(QtCore.QRect(30, 150, 60, 16))
            self.label.setObjectName(f"T{i+1}")
            self.verticalLayout_4.addWidget(self.label)
            self.labels.append(self.label)
            self.label.setStyleSheet(f"color: white; background-color: rgb{self.colors[i]}; border: 1px solid black;")

        self.verticalLayout_2.addLayout(self.verticalLayout_4)
        self.horizontalLayout.addLayout(self.verticalLayout_2)
        self.verticalLayout.addLayout(self.horizontalLayout)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1197, 24))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.actionSave = QtWidgets.QAction(MainWindow)
        self.actionSave.setObjectName("actionSave")
        self.menuFile.addAction(self.actionSave)
        self.menubar.addAction(self.menuFile.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Todo"))

        for i in range(8):
            self.checkboxes[i].setText(_translate("MainWindow", f"T{i+1}"))
            self.labels[i].setText(_translate("MainWindow", f"T{i+1}"))

        self.startStopButton.setText(_translate("MainWindow", "Start/Stop"))
        self.clearButton.setText(_translate("MainWindow", "Clear"))

        self.menuFile.setTitle(_translate("MainWindow", "File"))
        self.actionSave.setText(_translate("MainWindow", "Save"))

    @QtCore.pyqtSlot(float, tuple)
    def updateData(self, current_time, temperatures):
        for i in range(8):
            if self.checkboxes[i].isChecked():
                if temperatures[i] != 'err':
                    self.labels[i].setText(f"T{i + 1}: {temperatures[i]:.1f}")
                else:
                    self.labels[i].setText(f"T{i + 1}: --")
            else:
                self.labels[i].setText(f"T{i + 1}: --")

        active_ch = tuple(temperatures[i] if self.checkboxes[i].isChecked() else np.nan for i in range(8))
        self.model.appendData(current_time, *active_ch)
        self.time.append(current_time)
        for i in range(8):
            if self.checkboxes[i].isChecked():
                self.data[i].append(temperatures[i])
                self.plotLines[i].setData(self.time, self.data[i])
            else:
                self.data[i].append(np.nan)

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
