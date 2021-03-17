# -*- coding: utf-8 -*-
"""
__version__ = '1.0'

Created on 2021.01.11
Author xuzehao

Copyright (c) 2020 Star-Net
模块注释:
"""

import numpy as np
from config import ConfigManage
from data2execl import Data2Excel
from fun_thread import FunThread

from location import GetLocationNEW
from read_clock import ReadClock
from video_operation import VideoOperation


class BusinessLogic():

    def __init__(self):
        self.video_operation = VideoOperation()
        self.read_clock = ReadClock()
        self.get_location = GetLocationNEW()
        self.location = []

    def get_change_pic_4_second(self):
        print('正在定位')
        pic = self.video_operation.register_face(frameFrequency=1, number_of_sheets=1)

    # def get_pic_of_set_location(self,model,_type):
    #     pic = self.video_operation.register_face(frameFrequency=1,number_of_sheets=1)
    #     obj=GetLocation(pic)
    #     if model == 'auto' :
    #         self.location = obj.get_location_auto(int(_type))
    #         return self.video_operation.tailoring(pic,self.location)
    #     elif model == 'manual' :
    #         self.location =  obj.get_location_manual(int(_type))
    #         return self.video_operation.tailoring(pic,self.location)

    def get_pic_of_set_location(self, location_list):
        if len(location_list) == 2:
            self.location = self.get_location.math_the_location_by_one(location_list)
            print(self.location)
        elif len(location_list) == 4:
            self.location = self.get_location.math_the_location_by_two(location_list)
            print(self.location)
        else:
            print('点击次数不足')
            return False

    def get_num_of_pic(self):
        new_data = []
        new_pic = []
        def __get_num(location):
            return self.read_clock.read_time(self.video_operation.tailoring(
                self.video_operation.register_face(ConfigManage.frameFrequency, ConfigManage.number_of_sheets),
                location))

        if self.location == []:
            print('没有定位成功，请重新定位')
        elif len(self.location) == 4:
            data,pic_name= self.read_clock.calculate_time_difference(__get_num(self.location))
            for i in range(len(data)):
                if data[i] >= 0:
                    new_data.append(data[i])
                    new_pic.append(pic_name[i])
            return new_data,new_pic
        elif len(self.location) == 2:
            self.original_time = __get_num(self.location[0])
            self.equipment_time = __get_num(self.location[1])
            original_time, equipment_time, time_diff_list = self.read_clock.original_equipment_time(self.original_time,
                                                                                                    self.equipment_time)
            for i in time_diff_list:
                if i >= 0:
                    new_data.append(i)
            return [original_time, equipment_time, new_data]

    def run_main_make_excel(self, tab, test_name, test):
        excel = Data2Excel('{}-{}-{}'.format(test_name, test, tab))
        excel.write_default_format(test_name, test)
        data,pic_name=self.get_num_of_pic()
        excel.write_data(data,pic_name)
        excel.save_excel()
        # FunThread(self.video_operation.tailoring(
        #     self.video_operation.register_face(ConfigManage.frameFrequency, ConfigManage.number_of_sheets), self.location)).start()
        # self.video_operation.tailoring(
        #     self.video_operation.register_face(ConfigManage.frameFrequency, ConfigManage.number_of_sheets),
        #     self.location)

    def change_config(self, set_video, set_frameFrequency, set_number_of_sheets):
        ConfigManage.video = int(set_video)
        ConfigManage.frameFrequency = int(set_frameFrequency)
        ConfigManage.number_of_sheets = int(set_number_of_sheets)


if __name__ == '__main__':
    BusinessLogic().get_change_pic_4_second()
