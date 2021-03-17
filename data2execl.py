# -*- coding: utf-8 -*-
"""
__version__ = '1.0'

Created on 2021.01.15
Author xuzehao

Copyright (c) 2020 Star-Net
模块注释:
"""

import datetime
import os
import xlwt
import numpy as np

from path_manage import PathManage

test_lable = {
    '冻帧': 'freeze_lose_frame',
    '延迟': 'delay',
    '丢帧': 'freeze_lose_frame'
}


class Data2Excel:

    def __init__(self, test_name):
        for key, val in test_lable.items():
            if key in test_name:
                self.title_name = test_name
                self.__test_name = val
        self.workbook = xlwt.Workbook(encoding='utf-8')
        self.worksheet = self.workbook.add_sheet(self.title_name)
        self.set_font_style()

    def set_color(self, color):
        """
        设置窗格颜色
        :param color:
        :return:
        """
        pattern_prj = xlwt.Pattern()
        pattern_prj.pattern = xlwt.Pattern.SOLID_PATTERN
        pattern_prj.pattern_fore_colour = color
        return pattern_prj

    def set_borders(self, style):
        """
        居中和字体 边框
        :param style: xlwt.XFStyle()
        :return:
        """
        style.alignment.horz = 0x02
        style.alignment.vert = 0x01
        style.font.name = u'宋体'
        style.borders.left = 1
        style.borders.right = 1
        style.borders.bottom = 1
        style.borders.top = 1

    def set_font_style(self):
        """
        初始化格式
        :return:
        """
        self.style_middle = xlwt.XFStyle()
        self.style_middle.font.height = 220
        self.set_borders(self.style_middle)
        self.style_middle.pattern = self.set_color(11)

    def set_style_middle_color(self, color):
        """
        提供窗格的调用，可以传入颜色
        :param color: 颜色
        :return:
        """
        self.style_middle.pattern = self.set_color(color)
        return self.style_middle

    def __write_merge(self, x1, y1, x2, y2, text, style):
        """
        合并单元格写法
        :param x1: 开始行
        :param y1: 结束行
        :param x2: 开始列
        :param y2: 结束列
        :param text: 文本
        :param style:style
        :return:
        """
        self.worksheet.write_merge(x1, y1, x2, y2, text, style)

    def save_excel(self):
        self.workbook.save('{}/{}-{}.xls'.format(PathManage().get_output_path(self.__test_name),
                                                 os.path.split(str(datetime.datetime.now()))[1][:-7].replace(' ', '-'),
                                                 self.title_name))

    def write_default_format(self, text1, text2):
        self.__write_merge(0, 3, 0, 10, self.title_name, self.set_style_middle_color(11))
        self.__write_merge(4, 4, 0, 10, text1, self.set_style_middle_color(51))
        self.__write_merge(5, 5, 0, 10, text2, self.set_style_middle_color(15))
        if self.__test_name == 'delay':
            self.__write_merge(6, 6, 0, 0, '实际时间', self.set_style_middle_color(51))
            self.__write_merge(6, 6, 1, 1, '显示时间', self.set_style_middle_color(52))
            self.__write_merge(6, 6, 2, 2, '时间差值', self.set_style_middle_color(47))
        elif self.__test_name == 'freeze_lose_frame':
            self.__write_merge(6, 6, 0, 0, '组别', self.set_style_middle_color(3))
            self.__write_merge(6, 6, 1, 2, '时间差值', self.set_style_middle_color(52))
            self.__write_merge(6, 6, 3, 10, '图片名', self.set_style_middle_color(52))


    def write_data(self, _data,pic_name):
        if self.__test_name == 'delay':
            data = _data
            for k in range(len(data)):
                for i in range(len(data[k])):
                    self.__write_merge(7 + i, 7 + i, k, k, data[k][i], self.set_style_middle_color(1))
            self.__write_merge(len(data[0]) + 7, len(data[0]) + 7, 0, 1, '平均延迟', self.set_style_middle_color(26))
            self.__write_merge(len(data[0]) + 7, len(data[0]) + 7, 2, 2, np.mean(data[2]),
                               self.set_style_middle_color(26))
        if self.__test_name == 'freeze_lose_frame':
            # data = _data[99:]
            data = _data
            for i in range(len(data)):
                self.__write_merge(7 + i, 7 + i, 0, 0, i + 1, self.set_style_middle_color(1))
                self.__write_merge(7 + i, 7 + i, 1, 2, data[i], self.set_style_middle_color(1))
                self.__write_merge(7 + i, 7 + i, 3, 10, pic_name[i], self.set_style_middle_color(1))

    def test(self, text1, text2, data):
        pass


if __name__ == '__main__':
    pass

