# -*- coding: utf-8 -*-
"""
__version__ = '1.0'

Created on 2021.01.11
Author xuzehao

Copyright (c) 2020 Star-Net
模块注释:
"""
import time

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QMainWindow

from business_logic import BusinessLogic
from config import ConfigManage
from fun_thread import RunThread, FunThread
from message_box import MessageBox
from path_manage import pathmanage
from untitled import Ui_MainWindow
from video_operation import QTimer


class mywindow(QMainWindow, Ui_MainWindow):

    def __init__(self):
        super(mywindow, self).__init__()
        # self.window= self.centralwidget
        self.setupUi(self)
        # self.config_manage=Config_manage()
        self.ui_button(self.freeze_lose_frame)
        self.ui_button(self.delay)
        self.ui_setting(self.setting)
        self.message = MessageBox()
        self.business_logic = BusinessLogic()
        self.location_list = []
        # self.init()
        self._timer = QTimer(self)
        self._timer.start(16)
        self.update()
        # self.message.set_information_box('确认采集卡或摄像头接入')

    def init(self):
        self.business_logic.video_operation.init()
        if self.business_logic.video_operation.video_error_state is False:
            self.message.set_error_box('请检查摄像头')

    def ui_button(self, tab):

        equipment = QtWidgets.QComboBox(tab)
        equipment.setGeometry(QtCore.QRect(70, 40, 221, 31))
        equipment.addItems(ConfigManage.device)

        resolving_power = QtWidgets.QComboBox(tab)
        resolving_power.setGeometry(QtCore.QRect(300, 40, 221, 31))
        resolving_power.addItems(ConfigManage.resolving_power)

        auto = QtWidgets.QRadioButton(tab)
        auto.setGeometry(QtCore.QRect(310, 10, 121, 31))
        auto.setObjectName("auto_2")

        manual = QtWidgets.QRadioButton(tab)
        manual.setGeometry(QtCore.QRect(490, 10, 121, 31))
        manual.setObjectName("radioButton_2")
        manual.setChecked(True)

        label = QtWidgets.QLabel(tab)
        label.setGeometry(QtCore.QRect(70, 10, 181, 31))
        label.setObjectName("label")

        pushButton = QtWidgets.QPushButton(tab)
        pushButton.setGeometry(QtCore.QRect(50, 380, 151, 41))
        pushButton.setObjectName("pushButton")

        pushButton_2 = QtWidgets.QPushButton(tab)
        pushButton_2.setGeometry(QtCore.QRect(480, 380, 151, 41))
        pushButton_2.setObjectName("pushButton_2")

        pushButton_3 = QtWidgets.QPushButton(tab)
        pushButton_3.setGeometry(QtCore.QRect(250, 380, 151, 41))
        pushButton_3.setObjectName("pushButton_3")

        label_2 = QtWidgets.QLabel(tab)
        label_2.setGeometry(QtCore.QRect(50, 80, 571, 261))
        label_2.setObjectName("label_2")
        label_2.mousePressEvent = self.getpos

        _translate = QtCore.QCoreApplication.translate
        manual.setText(_translate("MainWindow", "手动定位"))
        auto.setText(_translate("MainWindow", "自动定位"))
        label.setText(_translate("MainWindow", "自动定位/手动定位"))
        pushButton.setText(_translate("MainWindow", "定位"))
        pushButton_3.setText(_translate("MainWindow", "摄像头"))
        pushButton_2.setText(_translate("MainWindow", "运行"))
        label_2.setText(_translate("MainWindow", "截图定位预览"))

        pushButton.clicked.connect(lambda: self.location(label_2, tab.objectName()))
        pushButton_2.clicked.connect(
            lambda: self.run(pushButton_2, tab.objectName(), equipment.currentText(), resolving_power.currentText()))
        pushButton_3.clicked.connect(lambda: self.play(label_2))

        # 按键关闭
        # pushButton_4.clicked.connect(self.closed)

    def ui_setting(self, tab):
        video = QtWidgets.QLabel(tab)
        video.setGeometry(QtCore.QRect(70, 20, 181, 40))
        video.setObjectName("video")
        video.setText('摄像头:')

        set_video = QtWidgets.QLineEdit(tab)
        set_video.setGeometry(QtCore.QRect(150, 23, 50, 30))
        set_video.setText(str(ConfigManage.video))

        frameFrequency = QtWidgets.QLabel(tab)
        frameFrequency.setGeometry(QtCore.QRect(70, 90, 181, 31))
        frameFrequency.setObjectName("frameFrequency")
        frameFrequency.setText('检测时间:')

        set_frameFrequency = QtWidgets.QLineEdit(tab)
        set_frameFrequency.setGeometry(QtCore.QRect(150, 93, 50, 30))
        set_frameFrequency.setText(str(ConfigManage.frameFrequency))

        number_of_sheets = QtWidgets.QLabel(tab)
        number_of_sheets.setGeometry(QtCore.QRect(70, 160, 181, 31))
        number_of_sheets.setObjectName("number_of_sheets")
        number_of_sheets.setText('检测数')

        set_number_of_sheets = QtWidgets.QLineEdit(tab)
        set_number_of_sheets.setGeometry(QtCore.QRect(150, 163, 50, 30))
        set_number_of_sheets.setText(str(ConfigManage.number_of_sheets))

        _translate = QtCore.QCoreApplication.translate
        pushButton = QtWidgets.QPushButton(tab)
        pushButton.setGeometry(QtCore.QRect(200, 400, 151, 41))
        pushButton.setObjectName("pushButton")
        pushButton.setText(_translate("MainWindow", "确定"))
        pushButton.clicked.connect(
            lambda: self.send_change_config(set_video.text(), set_frameFrequency.text(),
                                            set_number_of_sheets.text()))


    def closed(self):
        self.close()

    def send_change_config(self, video, frameFrequency, number_of_sheets):
        self.business_logic.change_config(video, frameFrequency, number_of_sheets)
        self.message.set_information_box(
            '修改成功,请确认修改\nvideo:{}\n检测时间{}ms\n检测数量{}张\n'.format(video, frameFrequency, number_of_sheets))

    def getpos(self, event):
        x = event.pos().x()
        y = event.pos().y()
        if self.tabWidget.tabText(self.tabWidget.currentIndex()) == '视频冻帧丢帧测试':
            if len(self.location_list) > 1:
                return
            self.location_list.append((x, y))
        if self.tabWidget.tabText(self.tabWidget.currentIndex()) == '视频延迟测试':
            if len(self.location_list) > 3:
                return
            self.location_list.append((x, y))
        print(self.location_list)

    def open_image(self, label):
        label.setPixmap(QPixmap(""))
        print(pathmanage.get_img_path())
        label.setPixmap(QPixmap(pathmanage.get_img_path()).scaledToWidth(600))

    def play(self, label=None):
        if label is None:
            return
        label.setPixmap(QPixmap(""))
        self._timer.timeout.connect(lambda: self.business_logic.video_operation.set_pic(label))
        # self._timer.timeout.connect()

    def location(self, label, tab_name):
        if tab_name == '视频冻帧丢帧测试':
            self.business_logic.get_pic_of_set_location(self.location_list)
        elif tab_name == '视频延迟测试':
            self.business_logic.get_pic_of_set_location(self.location_list)
        # self.location_list.clear()
        self.message.set_information_box('定位完成')

    def run(self, pushButton, tab, test_name, test):
        # self._timer.stop()
        # label.setPixmap(QPixmap(pathmanage.get_img_path()).scaledToWidth(600))
        # label.setText('程序运行中')
        #pushButton.setText('运行中')
        run_thread = RunThread(lambda: self.business_logic.run_main_make_excel(tab, test_name, test))
        run_thread.start()
        run_thread.exec()
        # self.business_logic.run_main_make_excel(tab, test_name, test)
        #self.message.set_information_box('运行完成')
        #pushButton.setText('运行')
