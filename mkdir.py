# -*- coding: utf-8 -*-
"""
__version__ = '1.0'

Created on 2020.11.30
Author xuzehao

Copyright (c) 2020 Star-Net
模块注释:
"""

import os

from log import log


CUR_PATH = os.path.dirname(os.path.abspath(__file__))
PCAP_PATH = os.path.join(CUR_PATH, "upload")
DUMP_PATH = os.path.join(CUR_PATH, "mp4_tools")
VIDEO_PATH = os.path.join(CUR_PATH, "video_data")


def __mkdir(path):
    if not os.path.exists(path):
        os.mkdir(path)
        log.info('mkdir{}'.format(path))


def mkdir():
    __mkdir(PCAP_PATH)
    __mkdir(DUMP_PATH)
    __mkdir(VIDEO_PATH)
