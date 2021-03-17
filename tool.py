# -*- coding: utf-8 -*-
"""
__version__ = '1.0'

Created on 2021.01.11
Author xuzehao

Copyright (c) 2020 Star-Net
模块注释:
"""

import os


def mkdir(path):
    # 引入模块
    path = path.strip()
    path = path.rstrip("\\")
    isExists = os.path.exists(path)
    if not isExists:
        os.makedirs(path)
        print(path + ' 创建成功')
        return path
    else:
        print(path + ' 目录已存在')
        return path
