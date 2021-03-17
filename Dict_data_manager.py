# -*- coding: utf-8 -*-
"""
__version__ = '1.0'

Created on 2020.11.30
Author xuzehao

Copyright (c) 2020 Star-Net
模块注释:扫描出来的端口等数据管理
"""


class Deal_dict(object):
    def __init__(self, dict):
        self.dict = dict
        self._type = self.dict.get('port_type')
        if self.dict.get('port_type') != 'H264':
            self.audio_src_port = self.dict.get('dst').get('port')
            self.audio_dst_port = self.dict.get('src').get('port')
            self.video_src_port = None
            self.video_dst_port = None
        elif self.dict.get('port_type') == 'H264':
            self.audio_dst_port = None
            self.audio_src_port = None
            self.video_src_port = self.dict.get('dst').get('port')
            self.video_dst_port = self.dict.get('src').get('port')
        self.dst_ip = self.dict.get('dst').get('ip')
        self.src_ip = self.dict.get('src').get('ip')