# -*- coding: utf-8 -*-
"""
__version__ = '1.0'

Created on 2021.03.11
Author xuzehao

Copyright (c) 2020 Star-Net
模块注释:
"""
import datetime
import os

import pytesseract
from PIL import Image


class ReadFromTesseract():

    def __init__(self):
        self.config = "-psm 9"
        self.suee = 0

    def read_num(self, image):
        img = Image.open(image)
        return pytesseract.image_to_string(img, config=self.config, lang='eng', nice=10, timeout=5000)

    def get_num_by_shell(self, path):
        command = 'tesseract -l video  {} -psm 7  stdout rule '.format(
            path)
        b = os.popen(command).read().replace(' ', '').replace('\n', '')
        if b is not None and b != '' and b != '\n':
            try:
                _time = datetime.datetime.strptime(b, '%M:%S.%f')
            except:
                _time = 'X'
        else:
            _time ='X'
        print(_time)



if __name__ == '__main__':
    a = ReadFromTesseract()
    rootdir = '/home/xuzehao/PycharmProjects/video_quality/date/2021-03-17-14:16:25.805973'
    list = os.listdir(rootdir)  # 列出文件夹下所有的目录与文件
    for i in range(0, len(list)):
        path = os.path.join(rootdir, list[i])
        a.get_num_by_shell(path)
