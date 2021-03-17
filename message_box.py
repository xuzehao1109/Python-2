# -*- coding: utf-8 -*-
"""
__version__ = '1.0'

Created on 2020.03.11
Author wry

Copyright (c) 2020 Star-Net

弹窗功能模块
"""

from PyQt5.QtWidgets import QWidget, QMessageBox


class MessageBox(QWidget):

    def __init__(self):
        super(MessageBox, self).__init__()
        self.message = QMessageBox()

    def show(self):
        reply = self.message.exec_()
        return reply

    def set_information_box(self, content):
        self.message.setIcon(QMessageBox.Information)
        self.message.setWindowTitle("提示")
        self.message.setText(content)
        reply = self.show()
        return reply

    def set_question_box(self, content):
        self.message.setIcon(QMessageBox.Question)
        self.message.setWindowTitle("提示")
        self.message.setText(content)
        self.message.addButton("YES", QMessageBox.AcceptRole)
        msg_no = self.message.addButton("NO", QMessageBox.NoRole)
        self.message.setDefaultButton(msg_no)  # 设置默认按钮焦点
        reply = self.show()
        return reply

    def set_error_box(self, content):
        self.message.setIcon(QMessageBox.Information)
        self.message.setWindowTitle("错误")
        self.message.setText(content)
        reply = self.show()
        return reply

    def set_custom_box(self, title, content):
        self.message.setWindowTitle(title)
        self.message.setText(content)
        self.show()

    def quit(self):
        self.message.close()

