# coding: utf-8
import myenvironment
import sys
sys.path.append(myenvironment.path)
import traceback
from datetime import datetime
import numpy as np
import pandas as pd
try:
    from PyQt4.QtGui import *
    from PyQt4.QtCore import *
except:
    import os
    os.environ['PYQTGRAPH_QT_LIB'] = 'PyQt5'
    from PyQt5.QtWidgets import *
    from PyQt5.QtGui import *
    from PyQt5.QtCore import *
import pyqtgraph as pg
import pyqtgraph.dockarea as pgda
from pyqtgraph.graphicsItems import PlotItem

import myfx.realtime.demo.indicator as fxind
import  myfx.realtime.demo.event_thread as event_thread


class TimeAxisItem(pg.AxisItem):

    def __init__(self, *args, **kwargs):
        super(TimeAxisItem, self).__init__(*args, **kwargs)

    def tickStrings(self, values, scale, spacing):
        if self.logMode:
            return self.logTickStrings(values, scale, spacing)
        return [datetime.fromtimestamp(v).strftime('%m-%d %H-%M') for v in values]


class FXPlot_candle(pg.GraphicsObject):

    def __init__(self, name, indicator=None, *args, **kwargs):
        super(FXPlot_candle, self).__init__(*args, **kwargs)
        self.name_ = name
        self.color = {}
        self.color['up'] = (0,128,0)
        self.color['down'] = (128,0,0)
        self.color['line'] = (128,128,128)
        self.pen = {}
        self.pen['up'] = pg.mkPen(self.color['up'])
        self.pen['down'] = pg.mkPen(self.color['down'])
        self.pen['line'] = pg.mkPen(self.color['line'])
        self.brush = {}
        self.brush['up'] = pg.mkBrush(self.color['up'])
        self.brush['down'] = pg.mkBrush(self.color['down'])

        if indicator is not None:
            self.set_indicator(indicator)

        self.picture = QPicture()
        self.generatePicture()

    def set_indicator(self, indicator):
        self.indicator = indicator

    def get_name(self):
        return self.name_

    def get_ylim(self, xlim=None):
        rate = self.indicator.get_values()
        i0 = self.indicator.time_to_index(xlim[0]) if xlim is not None else 0
        i1 = self.indicator.time_to_index(xlim[1]) if xlim is not None else len(rate)
        maxs = [np.max(x) for x in rate]
        mins = [np.min(x) for x in rate]
        max_ = np.max(maxs)
        min_ = np.min(mins)
        return [min_, max_]

    def generatePicture(self):
        items = self.indicator.get_items()
        data = items['y']
        timeSeries = items['x']
        if len(data) > 2:
            self.p = QPainter(self.picture)
            self.p.setPen(self.pen['line'])
            boxWidth = (timeSeries[-1]-timeSeries[-2])/3
            for (time_,ohlc_) in zip(timeSeries, data):
                self.p.setPen(self.pen['line'])
                if ohlc_[1] != ohlc_[2]:
                    self.p.drawLine(QPointF(time_, ohlc_[2]),
                                    QPointF(time_, ohlc_[1]))
                self.p.setPen(self.pen['up'] if ohlc_[0]>ohlc_[3]\
                                            else self.pen['down'])
                self.p.setBrush(self.brush['up'] if ohlc_[0]>ohlc_[3]\
                                                else self.brush['down'])
                self.p.drawRect(QRectF(time_-boxWidth,
                                            ohlc_[0],
                                            boxWidth*2,
                                            ohlc_[3]-ohlc_[0]))
            self.p.end()

    # QGraphicsObject.paint() is abstract and must be overridden
    def paint(self, p, *args):
        p.drawPicture(0, 0, self.picture)
    # QGraphicsObject.boundingRect() is abstract and must be overridden
    def boundingRect(self):
        return QRectF(self.picture.boundingRect())

    def update_plot(self):
        print('@FXPlot\tupdate_plot')
        self.picture = QPicture()
        self.generatePicture()


class FXPlot_line(pg.PlotDataItem):

    def __init__(self, name, indicator=None, *args, **kwargs):
        if indicator is not None:
            self.set_indicator(indicator)
            super(FXPlot_line, self).__init__(**indicator.get_items())
        else:
            super(FXPlot_line, self).__init__(*args, **kwargs)
        self.name_ = name
        config = self.parse_propaties(**kwargs)
        self.pen = pg.mkPen(**config)

    def set_indicator(self, indicator):
        self.indicator = indicator
    
    def get_name(self):
        return self.name_

    def get_ylim(self, xlim=None):
        return self.indicator.get_ylim(xlim)

    def update_plot(self):
        self.setData(**self.indicator.get_items(), pen=self.pen)
    
    def parse_propaties(self, **prop_raw):
        prop = {}
        for name, value in prop_raw.items():
            p = None
            n = ''
            if name=='color':
                n = 'pen'
                if ',' in value:
                    n = 'color'
                    rgb_str = value.split(',')
                    try:
                        if len(rgb_str) == 3:
                            r = int(rgb_str[0])
                            g = int(rgb_str[1])
                            b = int(rgb_str[2])
                            p = (r,g,b)
                            print(p)
                        elif len(rgb_str) == 4: #alpha
                            r = int(rgb_str[0])
                            g = int(rgb_str[1])
                            b = int(rgb_str[2])
                            a = float(rgb_str[3])
                            p = (r,g,b,a)
                    except ValueError:
                        p = (128,128,128)
                else:
                    p = value
            elif name=='linewidth' or name=='width':
                n = 'width'
                try:
                    p = int(value)
                except ValueError:
                    p = 1
            elif name=='linestyle':
                n = 'style'
                if value=='--':
                    p = Qt.DashLine
                elif value=='.':
                    p = Qt.DotLine
                elif value=='.-' or value=='-.':
                    p = Qt.DashDotLine
                elif value=='-..' or value=='..-':
                    p = Qt.DashDotDotLine
            prop[n] = p
        return prop


class FXChart(pg.PlotWidget):

    def __init__(self, name, *args, **kwargs):
        super(FXChart, self).__init__()#axisItems={'bottom': TimeAxisItem(orientation='bottom')})
        print('self.plotItem:{}'.format(self.plotItem))
        axisitem = PlotItem.PlotItem(axisItems={'bottom': TimeAxisItem(orientation='bottom')})
        self.plotItem = axisitem
        self.name_ = name
        self.plots = {}

    def set_default_propaties(self, hide_XAxis=True):
        self.showGrid(x=True, y=True, alpha=0.75)
        self.showAxis('right')
        self.hideAxis('left')
        self.setAutoVisible(y=True)
        if hide_XAxis:
            self.getPlotItem().getAxis('bottom').setHeight(0)
    
    def get_name(self):
        return self.name_

    def get_ylim(self, xlim=None):
        maxs = []
        mins = []
        for pname in self.plots:
            ylim = self.plots[pname].get_ylim(xlim)
            maxs.append(ylim[1])
            mins.append(ylim[0])
        max_ = np.nanmax(maxs)
        min_ = np.nanmin(mins)
        return [min_, max_]

    def add_plot(self, name, plot):
        self.plots[name] = plot
        self.addItem(plot)

    def update_plot(self):
        for name in self.plots:
            self.plots[name].update_plot()

    def set_xlim(self, xlim):
        self.setXRange(xlim[0],xlim[1])
    
    def set_ylim(self, ylim):
        self.setYRange(ylim[0], ylim[1])

class FXCharts(pgda.DockArea):

    plot_gen = {'line':FXPlot_line, 'candle':FXPlot_candle}

    def __init__(self, inds=None, self_sec=3600, prop=None, xlim=None, ylim=None, temporary=False, home=None):
        super(FXCharts, self).__init__(temporary, home)
        self.inds = inds
        self.plot_sec = self_sec #[s]=1hour
        self.xlim = None
        self.ylim = None
        self.charts = {}
        if inds is not None and prop is not None:
            self.parse_propaties(inds, prop)
    
    def __getitem__(self, name):
        return self.charts[name]

    def add_chart(self, name, chart=None, size=(20,20), bottom_chart=False):
        if chart is None:
            chart = FXChart(name)
            chart.set_default_propaties(hide_XAxis=not bottom_chart)
        self.charts[name] = chart
        self.addDock(pgda.Dock(name, widget=chart, size=size))
    
    def get_chart(self, name):
        return self.charts[name]

    def set_plot_sec(self, sec):
        self.plot_sec = sec
    
    def set_xlim(self, xlim):
        self.xlim = xlim

    def set_ylim(self, ylim):
        self.yim = ylim
    
    def refresh(self):
        self.update_plot()
    
    def update_plot(self):
        '''
        xlim = (Xstart, Xend)
        '''
        for name in self.charts:
            xlim = self.xlim
            if xlim is None:
                t = self.inds.newest_time()
                xlim = [t-self.plot_sec, t]
            ylim = self.ylim
            if ylim is None:
                ylim = self.charts[name].get_ylim(xlim)
            self.charts[name].set_xlim(xlim)
            if not None in ylim and not np.nan in ylim:
                self.charts[name].set_ylim(ylim)
            self.charts[name].update_plot()
    
    def parse_propaties(self, inds, prop):
        # チャート幅のセット
        if 'width' in prop:
            self.width = float(prop['width'])
        else:
            self.width = 100
        # チャート幅の単位のセット
        if 'unit' in prop:
            self.unit = prop['unit']
        else:
            self.unit = 'ticks'
        # configを基にチャートを作成・インジケータのセット
        for cname in prop['structure']:
            # 名前[cname]のチャートを作成
            self.add_chart(cname)
            for pname in prop['structure'][cname]:
                # コンフィグの抜き出し
                pconfig = prop['structure'][cname][pname]
                # typeを退避
                plot_type = pconfig['type']
                # typeを削除
                pconfig.pop('type')
                # plotの作成
                plot = FXCharts.plot_gen[plot_type](name=pname, indicator=inds[pname], **pconfig)
                # chartにplotを追加
                self.get_chart(cname).add_plot(pname, plot)
                print('@charts {}::{} added.\n{}'.format(cname, pname, plot))

class FXWidget(QMainWindow):

    def __init__(self, charts=None):
        super(FXWidget, self).__init__()
        if charts is not None:
            self.add_charts(charts)

    def add_charts(self, charts):
        self.charts = charts
        self.setCentralWidget(charts)
    
    def refresh(self):
        self.charts.refresh()
        self.update()



class FXWindow(QMainWindow):

    def __init__(self, fxevents, title_, geo_, *args, **kwargs):
        super(FXWindow, self).__init__(*args, **kwargs)
        self.fxevents = fxevents
        self.setWindowTitle(title_)
        self.init_ui(geo_)

    def add_widget(self, widget):
        self.setCentralWidget(widget)

    def add_charts(self, charts):
        self.widget = FXWidget(charts)
        self.add_widget(self.widget)

    def show_window(self):
        self.show()
    
    def refresh(self):
        self.widget.refresh()
        self.update()


    def init_ui(self, geo):
        self.setGeometry(*geo)
        # 特に何もしないけどメニューバーとツールバーとステータスバーをつくる
        menubar = self.menuBar()
        menu = menubar.addMenu('test_menu')
        menu.addAction('menu_item1')
        menu.addAction('menu_item2')
        menu.triggered[QAction].connect(self.menubar_action)

        toolbar = self.addToolBar('tool')
        toolbar.addAction('&Exit', QApplication.instance().quit)
        toolbar.addAction('redraw', self.toolbar_action)
        toolbar.addAction('B', self.toolbar_action)

        satusbar = self.statusBar()
        satusbar.showMessage('statusbar')

    def menubar_action(self, a):
        txt = a.text()
        # コンソールに表示
        print('menubar_action', txt)
        # ステータスバーにtxtの内容を表示
        self.statusBar().showMessage(txt)
        if txt == 'redraw':
            self.fxevents.put(event_thread.EventContainer(name='refresh',value=[]))

    def toolbar_action(self):
        txt = self.sender().text()
        # コンソールに表示
        print('toolbar_action', txt)
        # ステータスバーにtxtの内容を表示
        self.statusBar().showMessage(txt)
