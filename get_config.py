# -*- coding: utf-8 -*-
"""
__version__ = '1.0'

Created on 2020.11.30
Author xuzehao

Copyright (c) 2020 Star-Net
模块注释:
"""

import json
import subprocess

from log import log, log2file, log2screen
from run_thread import FunThread
from version import start_sf_info


def get_config_from_json():
    audio_coding = {}
    video_coding = {}
    with open('././config.json', 'r', encoding='utf-8') as f:
        config_dict = json.load(f)
        _audio_config = config_dict.get('audio_config')
        for key, val in _audio_config.items():
            audio_coding[int(key)] = val
        _video_coding = config_dict.get('video_config')
        for key, val in _video_coding.items():
            video_coding[int(key)] = val
        begin = config_dict.get("begin")
        max_port = config_dict.get("max")
        next_port = config_dict.get("next_port")
        next_bfcp_port = config_dict.get("next_bfcp_port")
        _video_model = config_dict.get("video_model")
        if _video_model == 'H265':
            video_model = 'h265'
        else:
            video_model = 'h264'
        fps = config_dict.get("fps")
        re_trs = config_dict.get("re_trs")
    log.info('audio_coding:{}\n'
             'video_coding:{}\n'
             'begin:{}\n'
             'next_port:{}\n'
             'next_bfcp_port:{}\n'
             'video_model:{}\n'
             'fps:{}\n'
             're_trs:{}\n'.format(audio_coding, video_coding, begin, next_port, next_bfcp_port, video_model, fps,
                                  re_trs))
    return audio_coding, video_coding, begin, max_port, next_port, next_bfcp_port, video_model, fps, re_trs


def open_file():
    def _open_file():
        subprocess.call(["gedit", './config.json'])
    FunThread(_open_file).start()


def tool_version():
    ver = ' '.join(start_sf_info().values())
    log.info(ver)


log2file()
log2screen()
