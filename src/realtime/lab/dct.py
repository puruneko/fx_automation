
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

##########################################################################################################
N = 16
P = 4
A_interval = 1
ma_period = 0
ohlc_flag = True
graph_py = True
graph_nim = False
##########################################################################################################


def mean_static(sgnl):
  return sum(sgnl)/float(len(sgnl))
def adjustPower(sig, ref):
  coef1 = np.sqrt(np.average(np.power(sig,2.0)))
  coef2 = np.sqrt(np.average(np.power(ref,2.0)))
  return np.array(sig)*coef2/coef1
def direction(a, b):
  return int((b-a)/abs(b-a)) if float(a) != float(b) else 0
def raisedCosine(start, end, N):
  result = []
  a = float(N) * 0.5
  b = float(N) * 0.25
  for i in range(N):
    result.append((start-end) * (0.5 + 0.5*np.cos(np.pi*(float(i)-2.0*b+a)/(2.0*a))) + end)
  return result
def raisedCosineInterpolation(sgnl, padding, margin=0.1):
  margin_point = int(padding * margin)
  raised_point = padding-margin_point
  pf = float(raised_point)
  a = pf * 0.5
  b = pf * 0.25
  result = []
  for j in range(padding):
    result.append(sgnl[0])
  for i in range(1,len(sgnl)):
    for r in raisedCosine(sgnl[i-1], sgnl[i], raised_point):
      result.append(r)
    for j in range(margin_point):
      result.append(sgnl[i])
  return np.array(result)
def raisedCosineInterpolation2(sgnl, padding, margin=0.1):
  result = []
  margin_point = int(padding * margin)
  dir_ = direction(sgnl[0], sgnl[1])
  itr_start = 0
  counter = 1
  #for j in range(padding):
  #  result.append(sgnl[0])
  for i in range(1, len(sgnl)):
    dir_now = direction(sgnl[i-1], sgnl[i])
    if dir_now == dir_:
      counter += 1
    elif dir_now != dir_ or dir_now == 0:
      point = padding*counter
      for r in raisedCosine(sgnl[itr_start], sgnl[i-1], point-margin_point):
        result.append(r)
      for j in range(margin_point):
        result.append(sgnl[i-1])
      dir_ = dir_now
      counter = 1
      itr_start = i-1
  if True:#counter != 1:
    #counter -= 1
    i = len(sgnl)-1
    point = padding*counter
    raised_point = point-margin_point
    a = float(raised_point) * 0.5
    b = float(raised_point) * 0.25
    for j in range(raised_point):
      result.append((sgnl[itr_start]-sgnl[i]) * (0.5 + 0.5*np.cos(np.pi*(float(j)-2.0*b+a)/(2.0*a))) + sgnl[i])
    for j in range(margin_point):
      result.append(sgnl[i])
  return np.array(result)

def dct(ind):
  result = []
  f = np.array(ind)
  N = float(len(ind))
  #coef = np.sqrt(2.0/N)
  for itr_k in range(int(N)):
    k = float(itr_k)
    result.append(0.0)
    for itr_n in range(int(N)):
      t = np.pi/N*(float(itr_n)+0.5)*k
      result[itr_k] += f[itr_n]*np.cos(t)
  result[0] = 0
  return np.array(result)

def idct(ind):
  result = []
  w = np.array(ind)
  N = float(len(ind))
  coef = 2.0/N
  bias = w[0]/N
  for itr_k in range(int(N)):
    k = float(itr_k)
    result.append(0.0)
    for itr_n in range(int(N)):
      t = np.pi/N*float(itr_n)*(k+0.5)
      result[itr_k] += bias + coef*w[itr_n]*np.cos(t)
  return np.array(result)

# 信号読み込み
def get_signal():
  sig = None
  sig_org = None
  a_list = None
  if ohlc_flag:
    ohlc = pd.read_csv(r"./../../resources/DAT_ASCII_EURUSD_M1_2007.csv", header=None, sep=";", names=('date','open',"high",'low','close','vomule'))
    sig_org = ohlc['close'][:N]
    if P != 0:
      sig = raisedCosineInterpolation2(sig_org, P, 0.0)
    else:
      if ma_period <= 1:
        sig = np.array(sig_org)-mean_static(sig_org)
      else:
        sig = np.array(pd.Series(sig_org).rolling(5).mean())
        sig[:5] = sig[0]
  else:
    t = np.linspace(-1, 1, N, endpoint=False)
    sig_org  = np.cos(2 * np.pi * 7 * t) + np.sin(np.pi * 6 * t)
    if P != 0:
      sig = raisedCosineInterpolation2(sig_org, P, 0.0)
    else:
      sig = sig_org
  return (sig, sig_org)

def w_filter(w, th):
  w_len = len(w)
  result = []
  for i in range(w_len):
    if i > th:
      result.append(0)
    else:
      result.append(w[i])
  return result

graph_data = {}

if graph_nim:
  df = pd.read_csv('signal_nim.csv', header=None)
  d_list = []
  for elems in df.values:
    d_list.append(np.array(elems))
  sig = np.array(d_list)

  df = pd.read_csv('signal_nim_inverse.csv', header=None)
  d_list = []
  for elems in df.values:
    d_list.append(np.array(elems))
  graph_data["sig_inv"] = np.array(d_list)

  df = pd.read_csv('signal_nim_inverse2.csv', header=None)
  d_list = []
  for elems in df.values:
    d_list.append(np.array(elems))
  graph_data["sig_inv2"] = np.array(d_list)

  df = pd.read_csv('dct.csv', header=None)
  d_list = []
  for elems in df.values:
    d_list.append(np.array(elems))
  graph_data["dct"] = np.array(d_list)

  df = pd.read_csv('dct2.csv', header=None)
  d_list = []
  for elems in df.values:
    d_list.append(np.array(elems))
  #graph_data["dct2"] = np.array(d_list)

if graph_py:
  (sig, sig_org) = get_signal()
  print('signal completed.')
  w = dct(sig)
  for th in (1, 2, 4, 8, 16, 32, len(w)):
    w2 = w_filter(w, th)
    inv = idct(w2)
    graph_data['th_{}'.format(th)] = inv#adjustPower(inv+mean_static(sig), sig)
    print('th_{} completed.'.format(th))
    if th == 1.0:
      graph_data['spectrum'] = np.array(w2[1:int(len(w2)*0.1)])

fig = plt.figure(figsize=(19,9))
fig.subplots_adjust(wspace=0.4, hspace=0.6)
nRow = 3
nCol = int(len(graph_data)/nRow)+1
for no, (key, value) in enumerate(graph_data.items()):
  ax = fig.add_subplot(nRow, nCol, no+1)
  ax.set_title(key)
  ax.plot([t for t in range(len(value))], value, c='red')
  if key != 'spectrum':
    ax.plot([t for t in range(len(value))], sig[:len(value)], c='green')
plt.show()
