# -*- coding:utf-8 -*-

"""
__version__ = '1.0'

Created on 2020/12
Author xzh
Copyright (c) 2020 Star-Net
"""

import logging.handlers
import os

LOG_LEVEL = logging.DEBUG
LOG_FILE = './log/log.txt'
MAX_FILE_NUM = 10  # 最大回滚日志文件数(根据不同命名的各自回滚)
MAX_FILE_SIZE = 10  # 最大单个日志文件大小
LOG_FORMATTER = '[%(asctime)s:%(msecs)3d][%(levelname)s][%(module)s][%(funcName)s][%(lineno)d]: %(message)s'
# 定义输出格式
formatter = logging.Formatter(LOG_FORMATTER)
# 全局日志
log = logging.getLogger('synthesis')
log.setLevel(level=LOG_LEVEL)


def log2file(filename=LOG_FILE, filesize=MAX_FILE_SIZE, filenum=MAX_FILE_NUM, loglevel=LOG_LEVEL):
    dpath = os.path.abspath(os.path.dirname(filename))
    if not os.path.exists(dpath):
        os.makedirs(dpath)
    rotating = logging.handlers.RotatingFileHandler(
        filename=filename,
        maxBytes=1024 * 1024 * filesize,
        backupCount=filenum,
        encoding="utf-8",
        delay=False
    )
    rotating.setFormatter(formatter)
    log.setLevel(loglevel)
    log.addHandler(rotating)


def log2screen():
    console = logging.StreamHandler()
    console.setFormatter(formatter)
    log.addHandler(console)

