import os
import sys
from dateutil.parser import parse
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.gridspec as gridspec
import mpl_finance
import datetime
import re

#### 固定
osc_postfix = '*'
disable_postfix = '-'

#### 可変
pips = 0.0001
SHOW_START = 0
SHOW_END = 1000#-1
main_rows = 4
sub_rows = 1

###############################################################
def loadCSV(filePath):
  # 読み込み
  df = pd.read_csv(filePath, header=0, parse_dates=['date'])#, index_col='date')
  df.drop(['blank'], axis=1, inplace=True)
  df = df[SHOW_START:SHOW_END]
  ohlc = df[['date','open','high','low','close']]
  df.drop(['open','high','low','close','volume'], axis=1, inplace=True)
  return ohlc, df

def match_dict_string(match_obj, key):
  if match_obj is None:
    return ''
  return match_obj.groupdict()[key]

def get_params(key):
  title = ''
  stg = {}
  cmpl_brkt = re.compile(r"^(?P<title>.+?)[{](?P<bracket>.*?)[}].*?")
  m_brkt = cmpl_brkt.match(key)
  if m_brkt is not None:
    title = m_brkt.groupdict()['title']
    bracket = m_brkt.groupdict()['bracket']
    for d in bracket.split(','):
      if d != "":
        key = d.split(':')[0]
        value = d.split(':')[1]
        stg[key] = value
  return (title, stg)

def graph(ohlc, df):
  osc_cmpl = re.compile(r'^.+?[{](?P<osc>[' + osc_postfix + r']+?)[}].*?$')
  # レイアウトの設定
  sub_plot_num = max([int(get_params(key)[1]['position']) if 'position' in get_params(key)[1] else 0 for key in df.keys()])
  grid_rows = main_rows + sub_plot_num*sub_rows
  gs = gridspec.GridSpec(nrows=grid_rows,ncols=1,hspace=0.4,wspace=0.1)
  gs.update(left=0.1,right=0.9,top=0.965,bottom=0.03,wspace=0.3,hspace=0.09)
  # プロッターの設定
  fig = plt.figure(figsize=(9,4))
  display_legend_main = []
  display_legend_sub = []
  for i in range(sub_plot_num):
    display_legend_sub.append([])
  ax_main = None
  ax_sub = None
  if sub_plot_num != 0:
    ax_main = plt.subplot(gs[0:main_rows,0])
    ax_sub = []
    for i in range(sub_plot_num):
      ax_sub.append(plt.subplot(gs[main_rows+(sub_rows*i):main_rows+(sub_rows*(i+1)),0], sharex=ax_main))
      ax_sub[i].grid(True)
    #ax_sub.legend()
    #ax_sub.xaxis_date()
    #ax_sub.xaxis.set_major_formatter(mdates.DateFormatter("%m-%d %H:%M"))
  else:
    ax_main = plt.subplot(gs[0:main_rows,0])
  ax_main.grid(True)
  #ax_main.legend()
  ax_main.xaxis_date()
  ax_main.xaxis.set_major_formatter(mdates.DateFormatter("%m-%d %H:%M"))
  #ohlc.index = [y for y in mdates.date2num([pd.to_datetime(x) for x in ohlc['date']])]
  #x = ohlc['date']#ohlc.reset_index().index
  #ohlc = np.vstack((range(len(ohlc)), ohlc.values.T)).T  # x軸データを整数に
  #ohlc['data'] = [pd.to_datetime(t) for t in ohlc['date'].values]
  t_series = mdates.date2num([pd.to_datetime(t) for t in ohlc['date']])
  ohlc_zip = zip(t_series, ohlc['open'].values, ohlc['high'].values, ohlc['low'].values, ohlc['close'].values)
  #ohlc = ohlc.reset_index().values
  mpl_finance.candlestick_ohlc(ax_main, ohlc_zip, width=(1/24/60)*0.9, alpha=0.5, colorup='r', colordown='b')
  markerColor = ['red','blue','green','orange','vioret','yellow']
  index = 0
  for key in df.sort_index(axis=1):
    (title, stg) = get_params(key)
    print('key:{}\n    title:{}  stg:{}'.format(key, title, stg))
    if 'Indicator[edge' in title:
        size = 11 if 'Main' in title else 8
        color = 'black' if 'Main' in title else 'gray'
        line, = ax_main.plot(t_series, df[key], "o", markersize=size, color=color, alpha=0.7, label=title)
        display_legend_main.append((title,line))
    if 'Indicator' in title:
      if not 'position' in stg or stg['position'] == '0':
        if not 'display' in stg or stg['display'] != 'false':
          line, = ax_main.plot(t_series, df[key], label=title)
          display_legend_main.append((title,line))
      else:
        if not 'display' in stg or stg['display'] != 'false':
          no = int(stg['position'])-1
          line, = ax_sub[no].plot(t_series, np.array(df[key])/pips, label=title)
          display_legend_sub[no].append((title,line))
    elif 'TradeRecordTable' in title:
      line = None
      if 'long' in title:
        line, = ax_main.plot(t_series, df[key], "^", markersize=10, color=markerColor[int(index/3)], label=title)
      elif 'short' in title:
        line, = ax_main.plot(t_series, df[key], "v", markersize=10, color=markerColor[int(index/3)], label=title)
      elif 'release' in title:
        line, = ax_main.plot(t_series, df[key], "o", markersize=10, color=markerColor[int(index/3)], label=title)
      if line is not None:
        display_legend_main.append((title,line))
      index += 1
  ax_main.legend([elem[1] for elem in display_legend_main], [elem[0] for elem in display_legend_main])
  if sub_plot_num:
    for i in range(sub_plot_num):
      ax_sub[i].legend([elem[1] for elem in display_legend_sub[i]], [elem[0] for elem in display_legend_sub[i]])
  # ロケータの設定
  #ax.grid(True)
  #ax.xaxis_date()
  #ax.xaxis.set_major_formatter(mdates.DateFormatter("%m-%d %H:%M"))
  #ax.format_xdata = mdates.DateFormatter('%Y-%m-%d')
  #locator = mdates.AutoDateLocator()
  #ax.xaxis.set_major_locator(locator)
  #ax.xaxis.set_major_formatter(mdates.AutoDateFormatter(locator))

  #plt.show()
  
  return fig

def main():
  start_time = datetime.datetime.now()
  filepath = r'./tradeHistory.csv'
  ohlc, df = loadCSV(filepath)
  print('loadCSV finished')
  fig = graph(ohlc, df)
  print('graph setting finished')
  print('{}[s]'.format(datetime.datetime.now()-start_time))
  plt.show()

if __name__ == '__main__':
  argv = sys.argv
  if len(argv) == 2:
    SHOW_END = int(argv[1])
  elif len(argv) == 3:
    SHOW_START = int(argv[1])
    SHOW_END = int(argv[2])
  main()