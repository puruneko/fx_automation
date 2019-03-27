import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.dates import date2num
import matplotlib.finance as mpf
import matplotlib.gridspec as gridspec
import seaborn as sns
import pandas.tseries.offsets as offsets
from matplotlib.ticker import LinearLocator, FixedLocator

class ChartParameter():

    def __init__(self, title, ind_all, ylim=(None,None)):
        self.title = title
        self.ind_all = ind_all
        self.indicator = [{},{}]
        self.forTransactionMarker = [{},{}]
        self.ylim = ylim

    def get_title(self):
        return self.title

    def set_indicator(self, axis, name, coef, forTransactionMarker=False, **param):
        self.indicator[axis][name] = {}
        self.indicator[axis][name]['param'] = param
        self.indicator[axis][name]['coef']  = coef
        self.forTransactionMarker[axis][name] = forTransactionMarker

    def get_ylim(self, axis):
        return self.ylim[axis]

    def get_names(self, axis, exceptTransactionMarker=True):
        if self.indicator[axis] != {}:
            names = list(self.indicator[axis].keys())
            if exceptTransactionMarker:
                rem = []
                for nm in names:
                    if self.forTransactionMarker[axis][nm]:
                        rem.append(nm)
                for r in rem:
                    names.remove(r)
        else:
            names = []
        return names

    def get_parameters(self, axis):
        param = {}
        for nm in self.indicator[axis].keys():
            param[nm] = self.indicator[axis][nm]['param']
        return param

    def get_parameter(self, axis, name):
        return self.indicator[axis][name]['param']

    def get_coefs(self, axis):
        coef = {}
        for nm in self.indicator[axis].keys():
            coef[nm] = self.indicator[axis][nm]['coef']
        return coef

    def get_coef(self, axis, name):
        return self.indicator[axis][name]['coef']

class RealtimeChart():

    def __init__(self, row_all, col_all, pips, title_main, title_window, standarddate, dt_second, timediff_ticks):
        self.pips = pips
        self.main = title_main
        self.title_window = title_window
        self.standarddate = standarddate
        self.dt_second = pd.tseries.offsets.Second(dt_second)
        self.timediff_second = pd.tseries.offsets.Second(timediff_ticks*dt_second)
        self.fig = plt.figure(figsize=(21,12))
        self.fig.canvas.set_window_title(self.title_window)
        self.gs = gridspec.GridSpec(row_all+1,col_all+1)
        self.gs_row = 0
        self.gs_col = 0
        self.ax = {}
        self.line = {}
        self.ax_profit_bar = self.fig.add_subplot(self.gs[:row_all,col_all:col_all+1])
        self.line['profit_bar'] = self.ax_profit_bar.bar([0], [0], tick_label=['profit'], linewidth=0)

    def add_chart(self, row_rel, col_rel, cp):
        title = cp.get_title()
        xaxis = self.ax[self.main][0] if title != self.main else None
        self.ax[title] = [None, None]
        self.ax[title][0] = self.fig.add_subplot(
                                self.gs[self.gs_row:self.gs_row + row_rel,
                                        0:self.gs_col-1 + col_rel],# '1' as profit space
                                sharex=xaxis)
        if cp.get_names(1) != []:
            self.ax[title][1] = self.ax[title][0].twinx()
        self.gs_row += row_rel
        self.gs_col += col_rel
        for axis in (0,1):
            self._update_line(self.ax[title][axis], [0,0], None,
                                cp.get_names(axis), cp.get_coefs(axis),
                                **cp.get_parameters(axis))

    def update_chart(self, xlim, ind_all, cp_all):
        cp_list = cp_all.values() if type(cp_all) == dict else cp_all
        for cp in cp_list:
            title = cp.get_title()
            #if title == 'profit':
            #    continue
            axis_list = (0,1) if cp.get_names(1) != [] else (0,)
            for axis in axis_list:
                self._del_lines(self.ax[title][axis])
                ylim = cp.get_ylim(axis)
                ylim = ylim if ylim is not None else self.calc_ylim(ind_all,
                                                                    cp.get_names(axis),
                                                                    cp.get_coefs(axis),
                                                                    xlim)
                self._update_line(self.ax[title][axis], xlim, ind_all,
                                  cp.get_names(axis, exceptTransactionMarker=False),
                                  cp.get_coefs(axis),
                                  **cp.get_parameters(axis))
                self._update_display(self.ax[title][axis], title, xlim, ylim)
        self._set_xticklabels(self.ax[self.main][0], xlim)

        progress_name = ('spread','win','lose','profit')
        progress_color = ('darkviolet','seagreen','royalblue','dimgray')
        self.ax_profit_bar.cla()
        bardata = []
        for nm in progress_name:
            bardata.append(ind_all[nm].newest()/self.pips)
        self.line['profit_bar'] = self.ax_profit_bar.bar([0,2,4,6], bardata,
                                                         tick_label=progress_name,
                                                         color=progress_color,
                                                         width=0.5, linewidth=0)
        self.ax_profit_bar.set_xlim(-1, 7)

    def show(self, s=0.01):
        self.gs.tight_layout(self.fig)
        plt.pause(s)

    def get_ax(self, title, axis):
        return self.ax[title][axis]

    def calc_ylim(self, IND, ind_name, coef, xlim):
        max_ = []
        min_ = []
        for nm in ind_name:
            try:
                max_.append(np.nanmax(np.array(IND[nm][xlim[0]:xlim[1]])*coef[nm]))
                min_.append(np.nanmin(np.array(IND[nm][xlim[0]:xlim[1]])*coef[nm]))
            except:
                print(nm)
                print(IND[nm][xlim[0]:xlim[1]])
                print(xlim[0])
                print(xlim[1])
                import traceback
                traceback.print_exc()
                raise ValueError
        max_ = np.max(max_) if max_ != [] else None
        min_ = np.min(min_) if min_ != [] else None
        return [min_,max_]

    def _del_chart(self, ax):
        for _ax in self.fig.get_axes():
            if _ax == ax:
                self.fig.delaxes(ax)

    def _del_lines(self, ax):
        for i in range(len(ax.lines)):
            del ax.lines[0]

    def _update_line(self, ax, xlim, ind, ind_name, coef, **param):
        x = np.arange(xlim[0],xlim[1])
        ind = ind if ind is not None else {k:[] for k in ind_name}
        for nm in ind_name:
            self.line[nm] = ax.plot(x, np.array(ind[nm][xlim[0]:xlim[1]])*coef[nm],
                                    label=nm, **param[nm])

    def _update_display(self, ax, title, xlim, ylim):
        ax.set_title(title)
        ax.set_xlim(xlim)
        ax.set_ylim(ylim)
        ax.grid(True)
        #ax.legend(loc='upper left')

    def _set_xticklabels(self, ax, xlim):
        date_period = self.timediff_second.delta/self.dt_second.delta
        xtick = np.arange(xlim[0], xlim[-1], date_period)
        np.append(xtick, xlim[-1])
        x_date = [self.standarddate+self.dt_second.delta*i\
                    for i in range(xlim[0],xlim[-1])]
        x_date.append(self.standarddate+self.dt_second.delta*xlim[-1])
        x_date = pd.to_datetime(x_date)
        xticklabels = x_date[0::date_period].strftime('%m-%d\n%H:%M:%S')
        np.append(xticklabels, x_date[-1].strftime("%m-%d\n%H:%M:%S"))
        ax.xaxis.set_major_locator(FixedLocator(xtick))
        ax.xaxis.set_ticks(xtick)
        ax.set_xticklabels(xticklabels)


def set_default_transaction_marker(cp_all, chart_name, ticket, pos_type, markersize, alpha):
    for nm in ticket.keys():
        if pos_type[0] in nm:
            trancolor = 'coral'
            tranmarker = '^'
        else:
            trancolor = 'slateblue'
            tranmarker = 'v'
        cp_all[chart_name].set_indicator(0,nm+'_entry',1,   forTransactionMarker=True,
                                                            linewidth=0,
                                                            color=trancolor,
                                                            marker=tranmarker,
                                                            markersize=markersize,
                                                            alpha=alpha)
        cp_all[chart_name].set_indicator(0,nm+'_exit',1,    forTransactionMarker=True,
                                                            linewidth=0,
                                                            color=trancolor,
                                                            marker='s',
                                                            markersize=markersize*0.75,
                                                            alpha=alpha)
        cp_all[chart_name].set_indicator(0,nm+'_stoploss',1,forTransactionMarker=True,
                                                            linewidth=0,
                                                            color='purple',
                                                            marker='s',
                                                            markersize=markersize*0.75,
                                                            alpha=alpha)
        cp_all[chart_name].set_indicator(0,nm+'_takeprof',1,forTransactionMarker=True,
                                                            linewidth=0,
                                                            color='seagreen',
                                                            marker='s',
                                                            markersize=markersize*0.75,
                                                            alpha=alpha)
        cp_all[chart_name].set_indicator(0,nm+'_illegal',1, forTransactionMarker=True,
                                                            linewidth=0,
                                                            color='red',
                                                            marker='*',
                                                            markersize=markersize*1.5,
                                                            alpha=alpha)
