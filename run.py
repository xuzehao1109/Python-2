# -*- coding: utf-8 -*-
"""
__version__ = '1.0'

Created on 2020.11.30
Author xuzehao

Copyright (c) 2020 Star-Net
模块注释:
"""

import re
import sys, os

from log import log
from get_config import tool_version
from mkdir import mkdir
from synthesis1 import Ui_Form
from PyQt5.QtWidgets import QFileDialog, QMessageBox
from pcap_tools import PcapTools
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import *
import subprocess
from run_thread import RunThread, FunThread

cwd = os.getcwd()


class mywindow(Ui_Form, QWidget):  # 这个窗口继承了用QtDesignner 绘制的窗口
    get_the_pcap_info_signal = pyqtSignal(list)

    def __init__(self):
        super(mywindow, self).__init__()
        self.setupUi(self)
        self.state = {'but1': self.pushButton_3,
                      'but2': self.pushButton_4,
                      'but3': self.pushButton_9,
                      'but4': self.pushButton_8,
                      'but5': self.pushButton_5,
                      'but6': self.pushButton_7,
                      'but7': self.pushButton_2,
                      'but8': self.pushButton}
        self.label_state = {
            'lab1': self.label_2,
            'lab2': self.label_6,
            'lab3': self.label_13,
            'lab4': self.label_14,
            'lab5': self.label_9,
            'lab6': self.label_10}
        self.comboBox.currentTextChanged.connect(self.change_ip)
        self.get_the_pcap_info_signal.connect(self.set_info)
        self.state_change('but7', False)

    def set_info(self, ip):
        self.comboBox.addItems(ip)
        self.state_change('but7', True)
        self.state_change('but8', True)
        for key in self.label_state:
            self.lable_text_change(key, "             解析完毕，请点击合成                  ")

    def change_ip(self):
        global src
        global dst
        global pcap_port_info
        ip1 = self.comboBox.currentText()
        self.state_change('but7', True)
        try:
            ip_set = re.findall('(.*)====', ip1)[0]
        except:
            return
        ip_set2 = re.findall('====>(.*\))', ip1)[0]
        type_ = re.findall('====>(.*)', ip1)[0]
        log.info('ip_set2:{}\nip_set:{}'.format(ip_set2, ip_set))
        self.comboBox_2.clear()
        self.comboBox_2.addItem(ip_set2 + '====>' + ip_set)
        if '10.10.10.108' not in self.comboBox_2.currentText() and '10.10.10.107' not in self.comboBox_2.currentText():
            if ',' not in ip_set2 and ',' not in ip_set:
                pcap_port_info = {'dst': {'video_port': int(re.findall('\((.*)\)', ip_set2)[0]),
                                          'src': re.findall('(.*)\(', ip_set2)[0], },
                                  'src': {'video_port': int(re.findall('\((.*)\)', ip_set)[0]),
                                          'src': re.findall('(.*)\(', ip_set)[0], }}
            else:
                pcap_port_info = {'dst': {'video_port': int(re.findall('\((.*),', ip_set2)[0]),
                                          'src': re.findall('(.*)\(', ip_set2)[0],
                                          'audio_port': int(re.findall(',(.*)\)', ip_set2)[0])},
                                  'audio_type': re.findall('\)(.*)', type_)[0],
                                  'src': {'video_port': int(re.findall('\((.*),', ip_set)[0]),
                                          'src': re.findall('(.*)\(', ip_set)[0],
                                          'audio_port': int(re.findall(',(.*)\)', ip_set)[0])}}
                log.info(pcap_port_info)
                return
        if '没有视频流' in self.comboBox.currentText():
            pcap_port_info = {'dst': {'audio_port': int(re.findall('\((.*)\)', ip_set2)[0]),
                                      'src': re.findall('(.*)\(', ip_set2)[0], },
                              'audio_type': re.findall('\)(.*)没有视频流', type_)[0],
                              'src': {'audio_port': int(re.findall('\((.*)\)', ip_set)[0]),
                                      'src': re.findall('(.*)\(', ip_set)[0], }}
        else:
            pcap_port_info = {'dst': {'video_port': int(re.findall('\((.*)\)', ip_set2)[0]),
                                      'src': re.findall('(.*)\(', ip_set2)[0], },
                              'src': {'video_port': int(re.findall('\((.*)\)', ip_set)[0]),
                                      'src': re.findall('(.*)\(', ip_set)[0], }}
        log.info(pcap_port_info)

    def state_change(self, but, state=False):
        button = self.state[but]
        button.setEnabled(state)

    def lable_text_change(self, lab, text=''):
        lab = self.label_state[lab]
        lab.setText(text)

    def setup(self):
        self.state_change('but7', False)
        for key in self.state:
            self.state_change(key, False)
        for key in self.label_state:
            self.lable_text_change(key, "请选择报文再进行合成，支持pcap/cap/pcapng格式")
        self.comboBox.clear()
        self.comboBox_2.clear()

    def file_check(self):
        global filelist
        filelist = []
        for dir, sec_dir, file in os.walk('./video_data'):
            for i in file:
                filelist.append(i)
        log.info(filelist)

    def open_pcap_file(self):
        global pcap_file  # 在这里设置全局变量以便在线程中使用
        global src
        global video_ip
        ip = []
        ip2 = []
        # 过滤条件
        self.setup()
        self.state_change('but7', False)
        pcap_file, videoType = QFileDialog.getOpenFileName(self, '选择文件', cwd, options=QFileDialog.DontUseNativeDialog)
        log.info("pcap文件：".format(pcap_file))
        if '.pcap' in pcap_file or '.cap' in pcap_file:
            self.label.setText(pcap_file)

            def get_info():
                for key in self.label_state:
                    self.lable_text_change(key, "                      报文解析过程中，请稍等...")
                self.state_change('but8', False)
                video_ip = PcapTools(pcap_file, cwd).get_the_ip()
                for ip_ in video_ip:
                    if len(ip_) == 7:
                        ip.append(ip_[0] + '(' + str(ip_[1]) + ',' + str(ip_[2]) + ')' + '====>' + ip_[3] + '(' + str(
                            ip_[4]) + ',' + str(ip_[5]) + ')' + ip_[6])
                    if len(ip_) == 4:
                        ip.append(ip_[0] + '(' + str(ip_[1]) + ')' + '====>' + ip_[2] + '(' + str(
                            ip_[3]) + ')' + '没有音频流')
                    if len(ip_) == 5:
                        ip.append(ip_[0] + '(' + str(ip_[1]) + ')' + '====>' + ip_[2] + '(' + str(
                            ip_[3]) + ')' + str(ip_[4]) + '没有视频流')
                for i in ip:
                    if i not in ip2:
                        ip2.append(i)
                self.get_the_pcap_info_signal.emit(ip2)

            run_thread = RunThread(
                get_info
            )
            run_thread.start()
            run_thread.exec()
        else:
            self.state_change('but8', True)
            QMessageBox.warning(self, "告警", '请传入pcap文件', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

    def synthesis_video(self):
        for key in self.label_state:
            self.lable_text_change(key, "                      音视频合成过程中，请稍等...")
        for key in self.state:
            self.state_change(key, False)
        th = Thread(self)
        th.outvideo.connect(self.message)
        th.start()

    def message(self, info):
        if info == "False":
            self.label_2.setText("解析失败")
            QMessageBox.information(self, '导出失败', "请重新操作 ", QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
            self.state_change('but8', True)
        else:
            info = eval(info)
            mp4name, wavname = PcapTools(pcap_file, cwd).get_all_name()
            global video1, video2, no_video1, no_video2, wav1, wav2
            try:
                video1 = './video_data/' + info[0]
                video2 = './video_data/' + info[1]
                no_video1 = './video_data/' + mp4name[0]
                no_video2 = './video_data/' + mp4name[1]
                wav1 = './video_data/' + wavname[0]
                wav2 = './video_data/' + wavname[1]
            except Exception as e:
                log.error('无双路视频{}'.format(e))
            self.file_check()
            self.state_change('but8', True)
            if info[0] not in filelist:
                self.label_2.setText('此路没有传输视频流')
            else:
                self.label_2.setText(info[0])
                self.state_change('but1', True)
                window.pushButton_3.clicked.connect(lambda: window.play_video(video1))
            if info[1] not in filelist:
                self.label_6.setText('此路没有传输视频流')
            else:
                self.label_6.setText(info[1])
                self.state_change('but2', True)
                window.pushButton_4.clicked.connect(lambda: window.play_video(video2))
            try:
                if mp4name[0] not in filelist:
                    self.label_13.setText('此路没有传输视频流')
                else:
                    self.label_13.setText(mp4name[0])
                    self.state_change('but3', True)
                    window.pushButton_9.clicked.connect(lambda: window.play_video(no_video1))
            except:
                self.label_13.setText('此路没有传输视频流')
            try:
                if mp4name[1] not in filelist:
                    self.label_14.setText('此路没有传输视频流')
                else:
                    self.label_14.setText(mp4name[1])
                    self.state_change('but4', True)
                    window.pushButton_8.clicked.connect(lambda: window.play_video(no_video2))
            except:
                self.label_14.setText('此路没有传输视频流')
            try:
                if wavname[0] not in filelist:
                    self.label_9.setText('此路没有传输音频流')
                else:
                    self.label_9.setText(wavname[0])
                    self.state_change('but5', True)
                    window.pushButton_5.clicked.connect(lambda: window.play_video(wav1))
                if wavname[1] not in filelist:
                    self.label_10.setText('此路没有传输音频流')
                else:
                    self.label_10.setText(wavname[1])
                    self.state_change('but6', True)
                    window.pushButton_7.clicked.connect(lambda: window.play_video(wav2))
            except:
                self.label_9.setText('此路没有传输音频流')
                self.label_10.setText('此路没有传输音频流')
            is_open = QMessageBox.information(self, '导出成功', "可查看video_data文件", QMessageBox.Yes | QMessageBox.No,
                                              QMessageBox.Yes)
            if is_open == 16384:
                def open_file():
                    subprocess.call(["nautilus", '././video_data'])
                FunThread(open_file).start()

    def play_video(self, path):
        th = Thread_play(path)
        th.start()
        th.exec()


class Video(object):
    def __init__(self, path):
        self.path = path

    def play(self):
        subprocess.call(["xdg-open", self.path])


class Movie_MP4(Video):
    def __init__(self, path):
        super().__init__(path)

    type = 'MP4'


class Thread_play(QThread):
    def __init__(self, path):
        super().__init__()
        self.path = path

    def run(self):
        try:
            video = Movie_MP4(self.path)
            video.play()
        except BaseException as e:
            log.info('error{}'.format(e))


class Thread(QThread):
    outvideo = pyqtSignal(str)

    def run(self):
        try:
            video_name = PcapTools(pcap_file, cwd).out_audio_and_video_to_mp4(pcap_port_info)
            self.outvideo.emit(str(video_name))
        except:
            self.outvideo.emit("False")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = mywindow()
    window.pushButton.clicked.connect(window.open_pcap_file)
    window.pushButton_2.clicked.connect(window.synthesis_video)
    window.show()
    tool_version()
    mkdir()
    sys.exit(app.exec_())
