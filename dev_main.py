# -*- coding: utf-8 -*-
"""
__version__ = '1.0'

Created on 2021.01.11
Author xuzehao

Copyright (c) 2020 Star-Net
模块注释:
"""

import sys

from PyQt5.QtWidgets import QApplication
from fun_thread import FunThread
from main_ui import mywindow
from time_clock import Timeclock


def time_clock():
    Timeclock().root_run()


FunThread(time_clock).start()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = mywindow()
    window.show()
    sys.exit(app.exec_())
