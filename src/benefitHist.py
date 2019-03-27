import os
import sys
from dateutil.parser import parse
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as ticker
import matplotlib.gridspec as gridspec
import mpl_finance
import datetime
import math

#### 可変
pips = 0.0001

space_pips = 20
max_pips = 100
x_label = [-100,-80,-60,-40,-20,0,20,40,60,80,100]

###############################################################
def loadCSV(filePath):
  # 読み込み
  df = pd.read_csv(filePath, header=0, parse_dates=['date'])
  y = []
  benefit = 0
  max_label = x_label[-1]
  min_label = x_label[0]
  for x in x_label:
    y.append([])
  y.append([])
  y.append([])
  base_index = math.ceil(abs(max_pips/space_pips))
  for r in df['benefit'].values:
    rr = r / pips
    benefit += rr
    shift_index = int(abs(rr/space_pips))
    if rr < 0:
      if rr < -max_pips:
        y[0].append(rr)
      else:
        y[base_index-shift_index].append(rr)
    else:
      if rr > max_pips:
        y[-1].append(rr)
      else:
        y[base_index+shift_index+1].append(rr)
  return len(df['benefit']), benefit, [len(a) for a in y]

def graph(count, benefit, y):
  # プロッターの設定
  fig = plt.figure(figsize=(9,4))
  ax = fig.add_subplot(111)
  x_label.insert(-1, min(x_label)-space_pips)
  x_label.insert(len(x_label), max(x_label)+space_pips)
  x_label_shift = np.array(x_label)-(space_pips/2)
  ax.bar(x_label_shift, y)
  ax.set_title('Trade Histgram ({0}count {1:1.1f}pips)'.format(count, benefit))
  ax.set_xlim(x_label[0]-20, x_label[-1]+20)
  ax.xaxis.set_major_locator(ticker.MultipleLocator(space_pips))

  return fig

def main():
  start_time = datetime.datetime.now()
  filepath = r'./tradeReport.csv'
  if len(sys.argv) == 2:
    filepath = sys.argv[1]
  (count, benefit, y) = loadCSV(filepath)
  print('loadCSV finished')
  fig = graph(count, benefit, y)
  print('graph setting finished')
  print('{}[s]'.format(datetime.datetime.now()-start_time))
  plt.show()

if __name__ == '__main__':

  main()