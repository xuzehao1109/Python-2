# -*- coding: utf-8 -*-
"""
__version__ = '1.0'

Created on 2021.03.10
Author xuzehao

Copyright (c) 2020 Star-Net
模块注释:
"""


class Config_manage():
    device = ['VT50V1', 'VT50V2', 'VT50V3', 'VT40V2', 'C21V1', 'C21V2', 'C21V3', 'VT30V2']
    resolving_power = ['误差统计','4K', '1080P60', '1080P30', '720P']
    video = 0
    frameFrequency = 100
    number_of_sheets = 1000


ConfigManage = Config_manage()

if __name__ == '__main__':
    print(Config_manage.frameFrequency)
    Config_manage.frameFrequency = 60
    b = Config_manage.frameFrequency
    print(b)
    print(100 / 1000)
