# -*- coding: utf-8 -*-
"""
__version__ = '1.0'

Created on 2020.06.04
Author cmr

Copyright (c) 2020 Star-Net
"""

from PyQt5.QtCore import QThread
import threading

class RunThread(QThread):

    def __init__(self, fun, *args, **kwargs):
        super(RunThread, self).__init__()
        self.fun = fun
        self.args = args
        self.kwargs = kwargs

    def run(self):
        self.fun(*self.args, **self.kwargs)

class FunThread(threading.Thread):
    """
    把函数放线程里执行
    """

    def __init__(self, fun, *args, **kwargs):
        """
        :param fun: 函数名 fun
        :param args: 函数参数 a,b,c...
        :param kwargs: 函数参数 x1=y1,x2=yx...
        """
        super(FunThread, self).__init__()
        self.fun = fun
        self.args = args
        self.kwargs = kwargs

    def run(self):
        self.fun(*self.args, **self.kwargs)