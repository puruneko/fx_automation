# coding: utf-8
import myenvironment
import sys
import traceback
from datetime import datetime
import numpy as np
import pandas as pd
import threading as th
try:
    from PyQt4.QtGui import *
    from PyQt4.QtCore import *
    print('PyQt4')
except:
    import os
    os.environ['PYQTGRAPH_QT_LIB'] = 'PyQt5'
    from PyQt5.QtWidgets import *
    from PyQt5.QtGui import *
    from PyQt5.QtCore import *
    print('PyQt5')
import pyqtgraph as pg
import pyqtgraph.dockarea as pgda
import myfx.realtime.demo.indicator as fxind
import myfx.realtime.demo.visual as fxvis


class WindowThread():

    def __init__(self, fxevents, charts=None):
        self.fxevents = fxevents
        # pyqt5を使えるように設定する
        self.app = self.pyqt5_setup()
        # ウィンドウを作成
        self.win = fxvis.FXWindow(fxevents=fxevents, title_='FX CHART', geo_=((500, 200, 800, 600)))
        # ウィンドウにウィジェットを登録
        if charts is not None:
            self.add_charts(charts)
    
    def refresh(self):
        self.win.refresh()
    
    def add_charts(self, charts):
        self.win.add_charts(charts)
    
    def ready_for_show(self):
        self.win.show_window()
    
    def get_app(self):
        return self.app

    def pyqt5_setup(self):
        # Dockのタイトルバーみたいなやつの色を変える
        # pyqtgraph.dockarea.Dock.DockLabelのupdateStyleを上書き
        from pyqtgraph.dockarea.Dock import DockLabel
        def updateStyle(self):
            self.setStyleSheet("DockLabel { color: #AAC; background-color: #444; }")
        setattr(DockLabel, 'updateStyle', updateStyle)

        style = """
            QWidget { color: #AAA; background-color: #333; border: 0px; padding: 0px; }
            QWidget:item:selected { background-color: #666; }
            QMenuBar::item { background: transparent; }
            QMenuBar::item:selected { background: transparent; border: 1px solid #666; }
        """
        app = QApplication(sys.argv)
        app.setStyleSheet(style)
        print('Application start!')
        return app
