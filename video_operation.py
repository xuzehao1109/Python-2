# -*- coding: utf-8 -*-
"""
__version__ = '1.0'

Created on 2021.01.11
Author xuzehao

Copyright (c) 2020 Star-Net
模块注释:
"""
import datetime
import os
import time
import sys
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import cv2
from PIL import Image
import numpy as np

from config import ConfigManage
from fun_thread import FunThread
from tool import mkdir
from path_manage import pathmanage


class VideoOperation():

    def __init__(self):
        self.cap = cv2.VideoCapture(ConfigManage.video)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)  # 4096×2160
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
        self.currentFrame = np.array([])
        #self.video_error_state = False

    def init(self):
        self.ret, self.read = self.cap.read()
        if self.ret is False:
            self.video_error_state = False
            #self.cap.release()
        else:
            self.video_error_state = True
            #self.cap.release()

    def register_face(self, frameFrequency=60, number_of_sheets=100):
        """
        截图
        :param frameFrequency: 多少帧截图一张
        :param number_of_sheets: 多少张
        :return:
        """
        i = 1
        times = 0
        number = 0
        pic_list = []
        cur_time1 = datetime.datetime.now()
        if number_of_sheets == 1:
            dir = '{}'.format(pathmanage.get_img_path())
        else:
            global dir
            dir = mkdir('{}/{}'.format(pathmanage.get_date_path(), os.path.split(str(cur_time1).replace(' ', '-'))[1]))
        # 提取视频的频率，默认每30帧提取一个,截取30张图片
        if os.path.exists(pathmanage.get_img_path()):
            os.remove(pathmanage.get_img_path())
        while i < int(frameFrequency) * int(number_of_sheets) + 1:  # 读取30张图片
            times += 1
            if self.ret is False:
                print('ret is False')
                return
            cur_time = datetime.datetime.now()
            if times % int(frameFrequency) == 0:
                number += 1
                print('===========正在截取第{}张图片，还有{}张=============='
                      .format(number, int(number_of_sheets) - number))
                if number_of_sheets == 1:
                    path = ''
                else:
                    path = '/' + os.path.split(str(cur_time).replace(' ', '-'))[1].replace(' ', '-') + "_" + str(
                        number) + ".png"

                def write(path):
                    cv2.imwrite('{}{}'.format(dir, path), self.read)

                FunThread(write, path).start()
                if number_of_sheets != 1:
                    pic_list.append('{}{}'.format(dir, path))
                else:
                    pic_list.append('{}'.format(dir))
                time.sleep(frameFrequency / 1000)
            i = i + 1
        cv2.destroyAllWindows()
        i = 1
        print(sorted(pic_list))
        return sorted(pic_list)

    def tailoring(self, pic_list, position):
        """
        分割
        :param pic_list:
        :param position:
        :return:
        """
        _pic_list = []
        _pic_list2 = []

        def _tor(_img, _h, _w, _position):
            x1 = _position[0]
            y1 = _position[1]
            x2 = _position[2]
            y2 = _position[3]
            crop1 = _img[int(float(y1) * _h):int(float(y2) * _h), int(float(x1) * _w):int(float(x2) * _w)]
            return crop1

        print('===========正在分割图片==============')
        for pic in pic_list:
            im = Image.open(pic)  # 返回一个Image对象
            img = cv2.imread(pic)
            w = im.size[0]
            h = im.size[1]
            if len(position) == 4:
                cv2.imwrite('{}'.format(pic), _tor(img, h, w, position))
                _pic_list.append('{}'.format(pic))
            elif len(position) == 2:
                cv2.imwrite('{}'.format('{}_1.png'.format(pic)), _tor(img, h, w, position[0]))
                cv2.imwrite('{}'.format('{}_2.png'.format(pic)), _tor(img, h, w, position[1]))
                _pic_list.append('{}'.format('{}_1.png'.format(pic)))
                _pic_list2.append('{}'.format('{}_2.png'.format(pic)))
        print(_pic_list)
        if len(position) == 4:
            return _pic_list
        elif len(position) == 2:
            return [_pic_list, _pic_list2]

    def concatenate(self, img1, img2):
        _img1 = cv2.imread(img1)
        _img2 = cv2.imread(img2)
        image = np.vstack((_img1, _img2))
        cv2.imwrite(pathmanage.get_img_path(), image)

    def captureFrame(self):
        ret, readFrame = self.ret, self.read
        return readFrame

    def captureNextFrame(self):
        self.ret, self.read = self.cap.read()
        if (self.ret == True):
            self.video_error_state = True
            self.currentFrame = cv2.cvtColor(self.read, cv2.COLOR_BGR2RGB)
        else:
            # MESSAGEBOX.set_error_box('请检查摄像头是否接入')
            print('请检查摄像头是否接入')

    def convertFrame(self):
        try:
            height, width = self.currentFrame.shape[:2]
            img = QImage(self.currentFrame, width, height, QImage.Format_RGB888)
            img = QPixmap.fromImage(img)
            self.previousFrame = self.currentFrame
            return img
        except Exception as e:
            #MESSAGEBOX.set_error_box('请检查摄像头是否能读取')
            raise ValueError(e)

    def set_pic(self, label):
        try:
            self.captureNextFrame()
            label.setPixmap(self.convertFrame())
            label.setScaledContents(True)
        except:
            print('No Frame')
            self.video_error_state = False
