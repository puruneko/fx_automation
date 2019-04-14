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
result_lebel = ['benefit', 'unrealizedProfit', 'unrealizedLoss']

space_pips = 20
max_pips = 100
x_label = [-100,-80,-60,-40,-20,0,20,40,60,80,100]

###############################################################
def loadCSV(filePath):
  # 読み込み
  df = pd.read_csv(filePath, header=0, parse_dates=['date'])
  result = [[], [], []]
  benefit = []
  profit = []
  loss = []
  totalBenefit = 0
  for x in x_label:
    for i in range(len(result)):
      result[i].append([])
  for x in range(2):
    for i in range(len(result)):
      result[i].append([])
  base_index = math.ceil(abs(max_pips/space_pips))
  for b,p,l in zip(df['benefit'].values,df['unrealizedProfit'].values,df['unrealizedLoss'].values):
    point = [b / pips, p / pips, l / pips]
    totalBenefit += b/pips
    try:
      for i in range(len(result)):
        if point[i] == 0:
          continue
        shift_index = int(abs(point[i]/space_pips))
        if point[i] < 0:
          if point[i] < -max_pips:
            result[i][0].append(point[i])
          else:
            result[i][base_index-shift_index].append(point[i])
        else:
          if point[i] > max_pips:
            result[i][-1].append(point[i])
          else:
            result[i][base_index+shift_index+1].append(point[i])
    except:
      print('{},{}'.format(len(result), base_index))
  result_arr = {}
  for i in range(len(result)):
    result_arr[result_lebel[i]] = [len(a) for a in result[i]]
  return len(df['benefit']), totalBenefit, result_arr

def graph(count, benefit, y):
  # プロッターの設定
  fig = plt.figure(figsize=(9,4))
  ax = fig.add_subplot(111)
  x_label.insert(-1, min(x_label)-space_pips)
  x_label.insert(len(x_label), max(x_label)+space_pips)
  x_label_shift = np.array(x_label)
  for key, value in y.items():
    x_label_shift = x_label_shift - space_pips/(len([a for a in y.keys()])+2)
    ax.bar(x_label_shift, value, label=key)
  ax.legend()
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