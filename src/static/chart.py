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

#### 固定
osc_postfix = '*'

#### 可変
pips = 0.0001
SHOW_START = 0
SHOW_END = -1#10000
grid_rows = 6


###############################################################
def loadCSV(filePath):
  # 読み込み
  df = pd.read_csv(filePath, header=0, parse_dates=['date'])#, index_col='date')
  df.drop(['blank'], axis=1, inplace=True)
  df = df[SHOW_START:SHOW_END]
  ohlc = df[['date','open','high','low','close']]
  df.drop(['open','high','low','close','volume'], axis=1, inplace=True)
  return ohlc, df


def graph(ohlc, df):
  # プロッターの設定
  fig = plt.figure(figsize=(9,4))
  gs = gridspec.GridSpec(nrows=grid_rows,ncols=1,hspace=0.4,wspace=0.1)
  gs.update(left=0.1,right=0.9,top=0.965,bottom=0.03,wspace=0.3,hspace=0.09)
  if True in [(osc_postfix in key) for key in df.keys()]:
    ax_main = plt.subplot(gs[0:grid_rows-2,0])
    ax_sub = plt.subplot(gs[grid_rows-2:grid_rows-1,0], sharex=ax_main)
    ax_sub.grid(True)
    ax_sub.legend()
    #ax_sub.xaxis_date()
    #ax_sub.xaxis.set_major_formatter(mdates.DateFormatter("%m-%d %H:%M"))
  else:
    ax_main = plt.subplot(gs[0:grid_rows-1,0])
  ax_main.grid(True)
  ax_main.legend()
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
    print(key)
    if 'Indicator[edge' in key:
        size = 11 if 'Main' in key else 8
        color = 'black' if 'Main' in key else 'gray'
        ax_main.plot(t_series, df[key], "o", markersize=size, color=color, alpha=0.7, label=key)
    if 'Indicator' in key:
      if key.endswith(osc_postfix):
        ax_sub.plot(t_series, np.array(df[key])/pips, label=key)
      else:
        ax_main.plot(t_series, df[key], label=key)
    elif 'TradeRecordTable' in key:
      if 'long' in key:
        ax_main.plot(t_series, df[key], "^", markersize=10, color=markerColor[int(index/3)], label=key)
      if 'short' in key:
        ax_main.plot(t_series, df[key], "v", markersize=10, color=markerColor[int(index/3)], label=key)
      if 'release' in key:
        ax_main.plot(t_series, df[key], "o", markersize=10, color=markerColor[int(index/3)], label=key)
      index += 1

  # ロケータの設定
  #ax.grid(True)
  #ax.xaxis_date()
  #ax.xaxis.set_major_formatter(mdates.DateFormatter("%m-%d %H:%M"))
  #ax.format_xdata = mdates.DateFormatter('%Y-%m-%d')
  #locator = mdates.AutoDateLocator()
  #ax.xaxis.set_major_locator(locator)
  #ax.xaxis.set_major_formatter(mdates.AutoDateFormatter(locator))

  #plt.show()
  plt.legend()
  
  return fig

def main():
  start_time = datetime.datetime.now()
  filepath = r'./tradeHistory.csv'
  if len(sys.argv) == 2:
    filepath = sys.argv[1]
  ohlc, df = loadCSV(filepath)
  print('loadCSV finished')
  fig = graph(ohlc, df)
  print('graph setting finished')
  print('{}[s]'.format(datetime.datetime.now()-start_time))
  plt.show()

if __name__ == '__main__':

  main()