# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'mainwindow.ui'
#
# Created by: PyQt5 UI code generator 5.15.10
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


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
        self.DiagramWidget = QtWidgets.QWidget(self.centralwidget)
        self.DiagramWidget.setMinimumSize(QtCore.QSize(175, 426))
        self.DiagramWidget.setMaximumSize(QtCore.QSize(175, 426))
        self.DiagramWidget.setObjectName("DiagramWidget")
        self.horizontalLayout.addWidget(self.DiagramWidget)
        self.PlotWidget = QtWidgets.QWidget(self.centralwidget)
        self.PlotWidget.setMinimumSize(QtCore.QSize(348, 0))
        self.PlotWidget.setObjectName("PlotWidget")
        self.horizontalLayout.addWidget(self.PlotWidget)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.checkBox = QtWidgets.QCheckBox(self.centralwidget)
        self.checkBox.setMaximumSize(QtCore.QSize(258, 20))
        self.checkBox.setObjectName("checkBox")
        self.verticalLayout_2.addWidget(self.checkBox)
        self.checkBox_2 = QtWidgets.QCheckBox(self.centralwidget)
        self.checkBox_2.setMaximumSize(QtCore.QSize(258, 20))
        self.checkBox_2.setObjectName("checkBox_2")
        self.verticalLayout_2.addWidget(self.checkBox_2)
        self.checkBox_3 = QtWidgets.QCheckBox(self.centralwidget)
        self.checkBox_3.setMaximumSize(QtCore.QSize(258, 20))
        self.checkBox_3.setObjectName("checkBox_3")
        self.verticalLayout_2.addWidget(self.checkBox_3)
        self.checkBox_4 = QtWidgets.QCheckBox(self.centralwidget)
        self.checkBox_4.setMaximumSize(QtCore.QSize(258, 20))
        self.checkBox_4.setObjectName("checkBox_4")
        self.verticalLayout_2.addWidget(self.checkBox_4)
        self.checkBox_5 = QtWidgets.QCheckBox(self.centralwidget)
        self.checkBox_5.setMaximumSize(QtCore.QSize(258, 20))
        self.checkBox_5.setObjectName("checkBox_5")
        self.verticalLayout_2.addWidget(self.checkBox_5)
        self.checkBox_6 = QtWidgets.QCheckBox(self.centralwidget)
        self.checkBox_6.setMaximumSize(QtCore.QSize(258, 20))
        self.checkBox_6.setObjectName("checkBox_6")
        self.verticalLayout_2.addWidget(self.checkBox_6)
        self.checkBox_7 = QtWidgets.QCheckBox(self.centralwidget)
        self.checkBox_7.setMaximumSize(QtCore.QSize(258, 20))
        self.checkBox_7.setObjectName("checkBox_7")
        self.verticalLayout_2.addWidget(self.checkBox_7)
        self.checkBox_8 = QtWidgets.QCheckBox(self.centralwidget)
        self.checkBox_8.setMaximumSize(QtCore.QSize(258, 20))
        self.checkBox_8.setObjectName("checkBox_8")
        self.verticalLayout_2.addWidget(self.checkBox_8)
        self.startStopButton = QtWidgets.QPushButton(self.centralwidget)
        self.startStopButton.setMaximumSize(QtCore.QSize(188, 16777215))
        self.startStopButton.setObjectName("startStopButton")
        self.verticalLayout_2.addWidget(self.startStopButton)
        self.clearButton = QtWidgets.QPushButton(self.centralwidget)
        self.clearButton.setMaximumSize(QtCore.QSize(188, 16777215))
        self.clearButton.setObjectName("clearButton")
        self.verticalLayout_2.addWidget(self.clearButton)
        self.verticalLayout_4 = QtWidgets.QVBoxLayout()
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.T1 = QtWidgets.QLabel(self.centralwidget)
        self.T1.setObjectName("T1")
        self.verticalLayout_4.addWidget(self.T1)
        self.T2 = QtWidgets.QLabel(self.centralwidget)
        self.T2.setObjectName("T2")
        self.verticalLayout_4.addWidget(self.T2)
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
        self.checkBox.setText(_translate("MainWindow", "T1"))
        self.checkBox_2.setText(_translate("MainWindow", "T2"))
        self.checkBox_3.setText(_translate("MainWindow", "T3"))
        self.checkBox_4.setText(_translate("MainWindow", "T4"))
        self.checkBox_5.setText(_translate("MainWindow", "T5"))
        self.checkBox_6.setText(_translate("MainWindow", "T6"))
        self.checkBox_7.setText(_translate("MainWindow", "T7"))
        self.checkBox_8.setText(_translate("MainWindow", "T8"))
        self.startStopButton.setText(_translate("MainWindow", "Start/Stop serial comms"))
        self.clearButton.setText(_translate("MainWindow", "Clear"))
        self.T1.setText(_translate("MainWindow", "T1: --"))
        self.T2.setText(_translate("MainWindow", "T2: --"))
        self.menuFile.setTitle(_translate("MainWindow", "File"))
        self.actionSave.setText(_translate("MainWindow", "Save"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
