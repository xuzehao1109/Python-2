# -*- coding: utf-8 -*-
"""
__version__ = '1.0'

Created on 2020.10.19
Author xuzehao

Copyright (c) 2020 Star-Net
模块注释:
"""
import os

from aip import AipOcr
import pytesseract


class BaiduApi(object):
    config = {
        'appId': '10922847',  # 10922847
        'apiKey': 'hPtiWTvTxV6tzuhMcSamSwun',  # hPtiWTvTxV6tzuhMcSamSwun
        'secretKey': 'EF8aQH2ffFPnUlIGwDturQehtBBvgDqx '  # EF8aQH2ffFPnUlIGwDturQehtBBvgDqx
    }

    # 'appId': '22896250',  # 10922847
    # 'apiKey': 'gbjZhNPa3W5QdScAE2HHGiCM',  # hPtiWTvTxV6tzuhMcSamSwun
    # 'secretKey': 'hsYGa7l0WUCx2TOkOZSoWftaWSRm9Mgf '  # EF8aQH2ffFPnUlIGwDturQehtBBvgDqx

    def __init__(self):
        self.client = AipOcr(**self.config)
        self.client.setConnectionTimeoutInMillis(5000)
        self.client.setSocketTimeoutInMillis(5000)

    def __get_text_by_img(self, image, basic=False):
        """
        通过百度获取图片的文本信息
        :param image:
        :param basic: True: 基础识别 False: 高精度识别
        :return:
        """
        client = self.client
        options = {}
        if basic:
            """基础识别"""
            options["language_type"] = "ENG"
            options["detect_direction"] = "true"
            options["detect_language"] = "true"
            options["probability"] = "true"
            result = client.basicGeneral(image, options)
        else:
            """带位置的高精度识别"""
            options["language_type"] = "CHN_ENG"
            options["detect_direction"] = "true"
            options["detect_language"] = "true"
            options["probability"] = "true"
            options["recognize_granularity"] = "big"
            options["vertexes_location"] = "true"
            result = client.general(image, options)

        return result

    def get_text_by_img_basic(self, image):
        return self.__get_text_by_img(image, basic=True)

    def get_text_by_img_high(self, image):
        return self.__get_text_by_img(image, basic=False)


if __name__ == '__main__':
    from PIL import Image

    image = "2021.png"
    # with open(image,'rb') as f
    #     a=BaiduApi().get_text_by_img_high(f)
    #     print(a)
    # # import cv2
    # # import numpy as np
    # # import sys
    # # #import image
    # im1 = Image.open(image)
    # im2 = im1.point(lambda p: p * 2)
    # #
    # im2.show()
    # im2.save("./temp/2020-10-29 15:18:30.347557=帧数*张数=1*10/angelababy2.jpg")

    # I = cv2.imread(image, cv2.IMREAD_GRAYSCALE)
    # # 图像归一化
    # fI = I / 255.0
    # # 伽马变换
    # gamma = 0.3
    # O = np.power(fI, gamma)
    # # 显示原图和伽马变换
    # cv2.imwrite(r"./temp/2020-10-29 15:18:30.347557=帧数*张数=1*10/1.jpg", O)
    # cv2.imwrite(r"./temp/2020-10-29 15:18:30.347557=帧数*张数=1*10/2.jpg", I)
    # cv2.waitKey()
    # cv2.destroyAllWindows()

    #
    rootdir = '/home/xuzehao/PycharmProjects/video_quality/date/2021-03-17-14:16:25.805973'
    list = os.listdir(rootdir)  # 列出文件夹下所有的目录与文件
    for i in range(0, len(list)):
        path = os.path.join(rootdir, list[i])
        with open(path, 'rb') as fp:
            fp = fp.read()
            # print('aaaa',fp)
            a = BaiduApi().get_text_by_img_basic(fp)
        print(a)

    # ima=Image.open(image)
    # con=str(pytesseract.image_to_string(im2))
    # print(con)
