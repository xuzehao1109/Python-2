# -*- coding: utf-8 -*-
"""
__version__ = '1.0'

Created on 2021.01.11
Author xuzehao

Copyright (c) 2020 Star-Net
模块注释:
"""
import os


class PathManage():

    def __init__(self):
        self.__path_date = '././date'
        self.__path_output = '././output'
        self.__path_img = self.__path_date + '/img.png'
        self.__path_excel = self.__path_date + '/format.xlsx'
        self.__freeze_lose_frame = self.__path_output + '/冻帧丢帧'
        self.__delay = self.__path_output + '/延迟'
        self.check_path()

    def set_dir_path(self):
        path = {
            'date': self.__path_date,
            'output': self.__path_output,
            'freeze_lose_frame': self.__freeze_lose_frame,
            'delay': self.__delay
        }
        return path

    def set_file_path(self):
        path = {
            'img': self.__path_img,
            'excel': self.__path_excel
        }
        return path

    def check_path(self):
        for path in self.set_dir_path().values():
            if not os.path.exists(path):
                os.makedirs(path)
        for path in self.set_file_path().values():
            if not os.path.exists(path):
                if path == self.__path_excel:
                    print('缺失excel原始文件')

    def get_img_path(self):
        return self.set_file_path().get('img')

    def get_date_path(self):
        return self.set_dir_path().get('date')

    def get_output_path(self, name):
        return self.set_dir_path().get(name)


pathmanage = PathManage()
