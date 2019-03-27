import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.dates import date2num
import matplotlib.finance as mpf
import matplotlib.gridspec as gridspec
import seaborn as sns
import pandas.tseries.offsets as offsets


def mp_style(_dic, **kwargs):
    for k, v in kwargs.items():
        if not k in _dic:
            _dic[k] = v
    return _dic

def set_xticklabels_date(ax, chart, rotation=0):
    from matplotlib.ticker import LinearLocator, FixedLocator
    x_date = chart.index
    num_date = len(x_date)
    num_xticl = num_date+1
    date_period = num_date/4#(num_xticklabels-1)
    xtick = np.arange(0, num_date, date_period)
    np.append(xtick, num_date)
    majorLocator   = FixedLocator(xtick)
    xticklabels = x_date[0::date_period].strftime("%m-%d\n%H:%M:%S")
    np.append(xticklabels, x_date[-1].strftime("%m-%d\n%H:%M:%S"))
    ax.set_xlim(0, num_date)
    ax.xaxis.set_major_locator(majorLocator)
    ax.xaxis.set_ticks(xtick)
    ax.set_xticklabels(xticklabels, rotation=rotation)

def plot_df(ax, x=None, y=None, **kwargs):
    _x = x
    _y = y
    if _x is None:
        _x = np.arange(len(_y.values))
    style = mp_style(kwargs,
                     linestyle='-',
                     linewidth=0.8,
                     color='black',
                     alpha=1,)
    ax_instance= ax.plot(_x, _y, **style)


def plot_hline(ax, y, close, linestyle='-', linewidth=1, color='black', alpha=0.5):
    num = len(close.index)
    _x = np.arange(num)
    _y = np.zeros(num)+y
    ax.plot(_x, _y, linestyle=linestyle, linewidth=linewidth, color=color, alpha=alpha)


def plot_candlesticks(ax, ohlc, width=0.5, colorup='orangered', colordown='royalblue'):
    time_by_num = [float(date2num(d)) for d in ohlc.index]
    np_index = np.arange(len(ohlc.index))
    new_ohlc = pd.DataFrame({'time': time_by_num,
                             'open': [float(v) for v in ohlc.open.values],
                             'high': [float(v) for v in ohlc.high.values],
                             'low':  [float(v) for v in ohlc.low.values],
                             'close':[float(v) for v in ohlc.close.values]},
                             index=np_index)
    mpf.candlestick2_ohlc(ax,
                          new_ohlc['open'],
                          new_ohlc['high'],
                          new_ohlc['low'],
                          new_ohlc['close'],
                          width=width,
                          colorup=colorup,
                          colordown=colordown)

def plot_plusminus(ax, chart, alpha=0.2, crossLine=False):
    ylim = ax.get_ylim()
    c = (ylim[0]+ylim[1])*0.5
    d = ylim[1]-c
    _max = np.max(chart[chart>0])
    _min = np.abs(np.min(chart[chart<0]))
    lim = np.max(_max, _min)
    new_chart = chart/lim*d+c
    _x = new_chart.index
    ax.fill_between(_x, new_chart.values, c, where=new_chart.values>=c, facecolor="tomato", alpha=alpha)
    ax.fill_between(_x, new_chart.values, c, where=new_chart.values<=c, facecolor="royalblue", alpha=alpha)
    if crossLine: ax.axhline(y=c, linewidth=0.2, alpha=alpha)

def plot_plusminus2(ax, chart, crossLine=True, **kwargs):
    ylim = ax.get_ylim()
    print("@plusminus2  {}".format(ylim))
    c = (ylim[0]+ylim[1])*0.5
    d = (ylim[1]-c)*0.5        # 0.5:unaccountable bias
    _max = np.max(chart[chart>=0])
    _min = np.abs(np.min(chart[chart<=0]))
    lim = max(_max, _min)
    new_chart = chart/lim*d+c
    _x = np.arange(len(new_chart.index))
    style = mp_style(kwargs,
                     linestyle='-',
                     linewidth=2.,
                     color='limegreen',
                     marker='o',
                     alpha=0.2,
                     label='test')
    ax.plot(_x, new_chart.values, **style)
    if crossLine:
        plot_hline(ax, c, chart)

def plot_plusminus_fill(ax, chart, crossLine=True, **kwargs):
    ylim = ax.get_ylim()
    c = (ylim[0]+ylim[1])*0.5
    d = (ylim[1]-c)*0.5        # 0.5:unaccountable bias
    _max = np.max(chart[chart>=0])
    _min = np.abs(np.min(chart[chart<=0]))
    lim = max(_max, _min)
    new_chart = chart/lim*d+c

    _x = np.arange(len(new_chart.index))
    up_style = mp_style(kwargs,
                     linestyle='-',
                     linewidth=2.,
                     color='tomato',
                     alpha=0.2,
                     label='above')
    ax.fill_between(_x, new_chart.values, c, where=new_chart>=c, **up_style)
    down_style = mp_style(kwargs,
                     linestyle='-',
                     linewidth=2.,
                     color='royalblue',
                     alpha=0.2,
                     label='below')
    ax.fill_between(_x, new_chart.values, c, where=new_chart<=c, **down_style)
    if crossLine:
        plot_hline(ax, c, chart)


def plot_plusminus_binary(ax, chart, crossLine=True, **kwargs):
    ylim = ax.get_ylim()
    c = (ylim[0]+ylim[1])*0.5
    d = (ylim[1]-c)*0.5        # 0.5:unaccountable bias
    _max = np.max(chart[chart>=0])
    _min = np.abs(np.min(chart[chart<=0]))
    lim = max(_max, _min)
    new_chart = chart/lim*d+c
    binary_upper = np.zeros(len(new_chart))
    binary_lower= np.zeros(len(new_chart))
    for i in range(len(new_chart)):
        binary_upper[i] = ylim[1] if new_chart[i] > 0 else c
        binary_lower[i] = ylim[0] if new_chart[i] <= 0 else c
    pd_binary_upper = pd.Series(binary_upper, index=new_chart)
    pd_binary_lower = pd.Series(binary_lower, index=new_chart)

    _x = np.arange(len(new_chart.index))
    down_style = mp_style(kwargs,
                     linestyle='-',
                     linewidth=2.,
                     color='royalblue',
                     alpha=0.2,
                     label='below')
    up_style = mp_style(kwargs,
                     linestyle='-',
                     linewidth=2.,
                     color='tomato',
                     alpha=0.2,
                     label='above')
    ax.fill_between(_x, pd_binary_lower.values, c, where=pd_binary_lower<=c, **down_style)
    ax.fill_between(_x, pd_binary_upper.values, c, where=pd_binary_upper>c, **up_style)
    if crossLine:
        plot_hline(ax, c, chart)

def fillzero_his_trade(his_trade):
    zero = his_trade.copy()
    for c in zero.columns:
        for i in zero[c].index:
            if np.isnan(zero[c][i]):
                continue
            zero[c][i] = 0.0
    return zero

def plot_df_bar(ax, y, **kwargs):
    _y = y.values
    _x = np.arange(len(y.values))
    _min = min(_y)
    _max = max(_y)
    style = mp_style(kwargs,
                     linestyle='-',
                     linewidth=0.0,
                     color='black',
                     alpha=0.3,
                     width=1.0)
    ax.set_ylim(_min,_max+(_max-_min))
    ax_instance= ax.bar(_x, _y, **style)


def time2number_in_index(time,specIndex):
    num = [0]*len(time)
    i = j = 0
    while(i < len(specIndex)):
        if j >= len(time):
            break
        if specIndex[i] == time[j]:
            num[j] = i
            j += 1
            i -= 1
        i += 1
    return num

def plot_transaction(ax, tranMarker, tranLine, spec, appearanceOffset=0):
    colMarker = ('long','short','settle_long', 'settle_short', 'losscut')
    colLine = ('long','short')
    marker = {'long':'^','short':'v','settle_long':'s','settle_short':'s','losscut':'s'}
    markersize = {'long':30,'short':30,'settle_long':20,'settle_short':20,'losscut':20}
    markercolor = {'long':'tomato','short':'royalblue',
                   'settle_long':'tomato','settle_short':'royalblue','losscut':'limegreen'}
    linecolor = {'long':'tomato', 'short':'royalblue'}

    for c in colMarker:
        style = mp_style({},
                         alpha=0.8,
                         linewidth=0,
                         marker=marker[c],
                         markersize=markersize[c],
                         color=markercolor[c])
        _x = time2number_in_index(tranMarker[c].index, spec.index)
        ax.plot(_x,tranMarker[c],**style)
    for c in colLine:
        style = mp_style({},
                         linestyle='--',
                         linewidth=2.,
                         color=linecolor[c])
        _x = time2number_in_index(tranLine[c].index, spec.index)
        ax.plot(_x, tranLine[c], **style)
