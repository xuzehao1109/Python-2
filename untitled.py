# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'untitled.ui'
#
# Created by: PyQt5 UI code generator 5.15.0
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QWidget


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.tabWidget.setGeometry(QtCore.QRect(40, 40, 681, 501))
        self.tabWidget.setObjectName("tabWidget")

        self.freeze_lose_frame = QWidget()
        self.freeze_lose_frame.setObjectName("视频冻帧丢帧测试")
        #
        # self.auto = QtWidgets.QRadioButton(self.freeze_lose_frame)
        # self.auto.setGeometry(QtCore.QRect(310, 40, 121, 31))
        # self.auto.setObjectName("auto_2")
        #
        #
        # self.manual = QtWidgets.QRadioButton(self.freeze_lose_frame)
        # self.manual.setGeometry(QtCore.QRect(490, 40, 121, 31))
        # self.manual.setObjectName("radioButton_2")
        # self.manual.setChecked(True)
        #
        # self.label = QtWidgets.QLabel(self.freeze_lose_frame)
        # self.label.setGeometry(QtCore.QRect(70, 40, 181, 31))
        # self.label.setObjectName("label")
        #
        # self.pushButton = QtWidgets.QPushButton(self.freeze_lose_frame)
        # self.pushButton.setGeometry(QtCore.QRect(90, 380, 151, 41))
        # self.pushButton.setObjectName("pushButton")
        #
        #
        # self.pushButton_2 = QtWidgets.QPushButton(self.freeze_lose_frame)
        # self.pushButton_2.setGeometry(QtCore.QRect(380, 380, 151, 41))
        # self.pushButton_2.setObjectName("pushButton_2")
        #
        # self.label_2 = QtWidgets.QLabel(self.freeze_lose_frame)
        # self.label_2.setGeometry(QtCore.QRect(50, 80, 571, 261))
        # self.label_2.setObjectName("label_2")
        self.tabWidget.addTab(self.freeze_lose_frame, "")

        self.delay = QWidget()
        self.delay.setObjectName("视频延迟测试")
        self.tabWidget.addTab(self.delay, "")
        self.more = QtWidgets.QWidget()
        self.more.setObjectName("待补充")
        self.tabWidget.addTab(self.more, "")
        self.setting = QtWidgets.QWidget()
        self.setting.setObjectName("设置")
        self.tabWidget.addTab(self.setting, "")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 28))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        # MainWindow.setTabOrder(self.tabWidget, self.auto)
        # MainWindow.setTabOrder(self.auto, self.manual)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "视频质量化测试工具@copyright-2021-自动化小组"))
        # self.auto.setText(_translate("MainWindow", "手动定位"))
        # self.manual.setText(_translate("MainWindow", "自动定位"))
        # self.label.setText(_translate("MainWindow", "自动定位/手动定位"))
        # self.pushButton.setText(_translate("MainWindow", "定位"))
        # self.pushButton_2.setText(_translate("MainWindow", "运行"))
        # self.label_2.setText(_translate("MainWindow", "截图定位预览"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.freeze_lose_frame), _translate("MainWindow", "视频冻帧丢帧测试"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.delay), _translate("MainWindow", "视频延迟测试"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.more), _translate("MainWindow", "待补充"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.setting), _translate("MainWindow", "设置"))






