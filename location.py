# -*- coding: utf-8 -*-
"""
__version__ = '1.0'

Created on 2021.01.07
Author xuzehao

Copyright (c) 2020 Star-Net
模块注释:
"""

import cv2
import imutils
import numpy as np
from PIL import Image


class GetLocation:

    def __init__(self, image):
        if type(image) is not list:
            print('single pic')
            self.img = image
        else:
            print('pic list')
            self.img = image[0]
        self.lower = np.array([0, 0, 0])
        self.upper = np.array([15, 15, 15])
        self.mouse_callback_x = []
        self.mouse_callback_y = []
        self.mouse_callback_xy = []

    def readimg(self):
        """
        读取图片
        :return: image
        """
        img = cv2.imread(self.img)
        return img

    def get_location_auto(self, _type=1):
        x_list = []
        y_list = []
        xy_list = []
        image = self.readimg()
        shapeMask = cv2.inRange(image, self.lower, self.upper)
        # 在mask中寻找轮廓
        cnts = cv2.findContours(shapeMask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)
        for c in cnts:
            # draw the contour and show it
            cv2.drawContours(image, [c], -1, (0, 255, 0), 2)
            M = cv2.moments(c)  # 计算第一条轮廓的各阶矩,字典形式
            # print(M)
            if M['m00'] == 0:
                continue
            center_x = int(M['m10'] / M['m00']) / 1920
            center_y = int(M['m01'] / M['m00']) / 1080
            print('center_x:', center_x)
            print('center_y:', center_y)
            x_list.append(center_x)
            y_list.append(center_y)
            xy_list.append([center_x, center_y])
            cv2.circle(image, (int(center_x), int(center_y)), 7, 128, -1)  # 绘制中心点
            str1 = '(' + str(center_x) + ',' + str(center_y) + ')'  # 把坐标转化为字符串
            cv2.putText(image, str1, ((int(center_x), int(center_y))), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 1,
                        cv2.LINE_AA)  # 绘制坐标点位
        if _type == 1:
            if len(x_list) != 4:
                return False
            location = ['%.2f' % min(x_list), '%.2f' % min(y_list), '%.2f' % max(x_list), '%.2f' % max(y_list)]
            print(location)
            return location
        if _type == 2:
            if len(x_list) != 8:
                return False
            _x_list1 = []
            _y_list1 = []
            _x_list2 = []
            _y_list2 = []
            _xy_list = sorted(xy_list, key=lambda d: d[0], reverse=False)
            _xy_list1 = xy_list[0:4]
            for xy in _xy_list1:
                _x_list1.append(xy[0])
                _y_list1.append(xy[0])
            _xy_list2 = xy_list[4:]
            for xy in _xy_list2:
                _x_list2.append(xy[0])
                _y_list2.append(xy[0])
            location1 = ['%.2f' % min(_x_list1), '%.2f' % min(_y_list1), '%.2f' % max(_x_list1), '%.2f' % max(_y_list1)]
            location2 = ['%.2f' % min(_x_list2), '%.2f' % min(_y_list2), '%.2f' % max(_x_list2), '%.2f' % max(_y_list2)]
            print(location1, location2)
            return [location1, location2]

    def on_event_button_down(self, event, x, y, flags, param):
        img = self.readimg()
        if event == cv2.EVENT_LBUTTONDOWN:
            xy = "%d,%d" % (x, y)
            cv2.circle(img, (x, y), 1, (255, 0, 0), thickness=-1)
            cv2.putText(img, xy, (x, y), cv2.FONT_HERSHEY_PLAIN,
                        2.0, (0, 0, 0), thickness=2)
            _x = x / 1920
            _y = y / 1080
            print(_x, _y)
            self.mouse_callback_x.append(_x)
            self.mouse_callback_y.append(_y)
            self.mouse_callback_xy.append([_x, _y])
            cv2.imshow("image", img)

    def get_location_manual(self, _type=1):
        img = self.readimg()
        cv2.namedWindow("image")
        cv2.setMouseCallback("image", self.on_event_button_down)

        def _timer_out(_time, text):
            while (1):
                cv2.putText(img, text, (580, 500), cv2.FONT_HERSHEY_PLAIN,
                            3.0, (0, 0, 0), thickness=2)
                cv2.imshow("image", img)
                if cv2.waitKey(1) & 0xFF == ord('q') or len(self.mouse_callback_x) > _time:  # 控制点击数
                    break
            cv2.destroyAllWindows()

        if _type == 1:
            _timer_out(_type, 'Click on two points')
            location = ['%.2f' % min(self.mouse_callback_x), '%.2f' % min(self.mouse_callback_y),
                        '%.2f' % max(self.mouse_callback_x), '%.2f' % max(self.mouse_callback_y)]
            print(location)
            return location
        if _type == 2:
            _timer_out(3, 'Click on four points')
            _x_list1 = []
            _y_list1 = []
            _x_list2 = []
            _y_list2 = []
            _xy_list = sorted(self.mouse_callback_xy, key=lambda d: d[0], reverse=False)
            _xy_list1 = self.mouse_callback_xy[0:2]
            for xy in _xy_list1:
                _x_list1.append(xy[0])
                _y_list1.append(xy[0])
            _xy_list2 = self.mouse_callback_xy[2:]
            for xy in _xy_list2:
                _x_list2.append(xy[0])
                _y_list2.append(xy[0])
            location1 = ['%.2f' % min(_x_list1), '%.2f' % min(_y_list1), '%.2f' % max(_x_list1), '%.2f' % max(_y_list1)]
            location2 = ['%.2f' % min(_x_list2), '%.2f' % min(_y_list2), '%.2f' % max(_x_list2), '%.2f' % max(_y_list2)]
            print(location1, location2)
            return [location1, location2]


class GetLocationNEW(object):
    def __init__(self):
        pass

    def math_the_location_by_one(self, location_list):
        location_1_x = '%.2f' % (location_list[0][0] / 571)
        location_1_y = '%.2f' % (location_list[0][1] / 261)
        location_2_x = '%.2f' % (location_list[1][0] / 571)
        location_2_y = '%.2f' % (location_list[1][1] / 261)
        print(location_1_x, location_1_y, location_2_x, location_2_y)
        return [float(location_1_x), float(location_1_y), float(location_2_x), float(location_2_y)]

    def math_the_location_by_two(self, location_list):
        location_1_x = '%.2f' % (location_list[0][0] / 571)
        location_1_y = '%.2f' % (location_list[0][1] / 261)
        location_2_x = '%.2f' % (location_list[1][0] / 571)
        location_2_y = '%.2f' % (location_list[1][1] / 261)
        location_3_x = '%.2f' % (location_list[2][0] / 571)
        location_3_y = '%.2f' % (location_list[2][1] / 261)
        location_4_x = '%.2f' % (location_list[3][0] / 571)
        location_4_y = '%.2f' % (location_list[3][1] / 261)
        print(location_1_x, location_1_y, location_2_x, location_2_y)
        return [[float(location_1_x), float(location_1_y), float(location_2_x), float(location_2_y)],
                [float(location_3_x), float(location_3_y), float(location_4_x), float(location_4_y)]]


if __name__ == '__main__':
    pic = './date/c1.png'
    test_list = [(18, 14), (22, 245), (550, 20), (538, 226)]
    print(len(test_list))
    print(GetLocationNEW().math_the_location_by_two(test_list))
    # import cv2
    # import numpy as np
    # import pandas as pd
    #
    # img1 = cv2.imread('./date/c1.png')
    # img2 = cv2.imread('./date/c1.png')
    # #gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
    # #gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
    # # ====使用numpy的数组矩阵合并concatenate======
    #
    # #image = np.concatenate((img1, img2))
    # image = np.vstack((img1, img2))
    # #image = np.concatenate((img1, img2))
    #
    # # image = np.array(df)  # dataframe to ndarray
    #
    # # =============
    # cv2.imwrite('./date/img.png_3.png', image)
    # cv2.imshow('image', image)
