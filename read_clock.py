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

import pytesseract
from PIL import Image
from baiduapi import BaiduApi
import numpy as np


class ReadClock():

    def __init__(self):
        pass

    def __read_time(self, image):
        _time = ''
        print('===========正在读取文字==============')
        command = 'tesseract -l video  {} -psm 7  stdout rule '.format(
            image)
        b = os.popen(command).read().replace(' ', '').replace('\n', '')
        if b is not None and b != '' and b != '\n':
            try:
                _time = datetime.datetime.strptime(b, '%M:%S.%f')
            except:
                _time = 'X'
        else:
            _time = 'X'
        print(image, _time)
        return _time

    def read_time(self, pic_list):
        data_list = []
        for i in range(len(pic_list)):
            data_dict = {}
            data = self.__read_time(pic_list[i])
            data_dict['number'] = i
            data_dict['name'] = pic_list[i]
            data_dict['value'] = data
            data_list.append(data_dict)
            print(data_dict)
        return data_list

    def calculate_time_difference(self, data_list):
        time_difference = []
        pic_name =[]
        for i in range(len(data_list)):
            print('===========正在计算时间==============')
            if i < len(data_list) - 1:
                print(i, len(data_list) - 1)
                if data_list[i + 1]['value'] == 'X' or data_list[i]['value'] == 'X':
                    continue
                print(data_list[i + 1]['value'], data_list[i]['value'])
                _time = (data_list[i + 1]['value'] - data_list[i]['value']).total_seconds()
                time_difference.append(_time)
                pic_name.append(data_list[i+1]['name'])
        print(time_difference)
        return time_difference,pic_name

    def deal_data(self, data_list):
        data_list_ = []
        avg_ = np.mean(data_list)
        print('平均时间间隔{}'.format(avg_))
        print('===========正在计算结果==============')
        for i in range(len(data_list)):
            if i < len(data_list) - 1:
                if data_list[i] == 0:
                    data_list_.append(data_list[i])
                    print('冻帧', i, data_list[i])
                    continue
                if data_list[i + 1] - data_list[i] >= avg_:
                    data_list_.append(data_list[i])
                    print('丢帧', i, data_list[i])
                if data_list[i] < 0:
                    continue
                else:
                    data_list_.append(data_list[i])
        return data_list_

    def original_equipment_time(self, original_time, equipment_time):
        time_diff_list = []
        __original_time = []
        __equipment_time = []
        range_time = min(len(original_time), len(equipment_time))
        for i in range(range_time):
            if original_time[i]['value'] == 'X' or equipment_time[i]['value'] == 'X':
                continue
            _time = (original_time[i]['value'] - equipment_time[i]['value']).total_seconds()
            if _time < 0 or _time > 0.5:
                continue
            time_diff_list.append(_time)
            __original_time.append(original_time[i]['value'])
            __equipment_time.append(equipment_time[i]['value'])
        print(time_diff_list)
        print(np.mean(time_diff_list))
        return [__original_time, __equipment_time, time_diff_list]
