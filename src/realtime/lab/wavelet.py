import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import pandas as pd
from scipy import signal
import copy
import datetime

N = 32
P = 32
A = 32
period = 0
ohlc_flag = False
A_interval = 75
w_cut_start = 0.001
w_cut_end = 0.999

graph_py  = True
graph_nim = True

##########################################################################################################
def rickerWavelet(t, s=1.0):
  a = 2 * np.sqrt(3 * s) * np.pi**0.25
  b = 1 - (t / s)**2
  c = np.exp(-1 * t**2 / (2 * s**2))
  return a * b * c
def haarWavelet(t):
  f = lambda x : 1.0 if (0.0 <= x and x < 0.5) else (-1.0 if (0.5 <= x and x < 1.0) else 0.0)
  f_u = np.frompyfunc(f, 1, 1)
  return f_u(t)
def cosWavelet(t):
  return np.cos(t)
def cwt(x, p, t, a):
  dt = t[1] - t[0]
  A = a.reshape(-1, 1, 1)
  B = t.reshape(1, -1, 1)
  T = t.reshape(1, 1, -1)
  xt = x.reshape(1, 1, -1)
  return np.sum(xt * p((T - B) / A), axis=2) / (np.abs(A.reshape(-1, 1)) ** 0.5) * dt
def icwt(xw, e, t, a):
  da = np.array([a[i] - a[i-1] for i in range(len(a))]).reshape(-1, 1, 1);da[0] = a[1]-a[0]#a[1]-a[0]#
  db = t[1] - t[0]
  A = a.reshape(-1, 1, 1)
  B = t.reshape(1, -1, 1)
  T = t.reshape(1, 1, -1)
  Xw = xw.reshape(*xw.shape, 1)
  return np.sum(Xw * e((T - B) / A) / (np.abs(A) ** 0.5) / (A ** 2) * da, axis=(0, 1)) * db
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
    for j in range(raised_point):
      result.append((sgnl[i-1]-sgnl[i]) * (0.5 + 0.5*np.cos(np.pi*(float(j)-2.0*b+a)/(2.0*a))) + sgnl[i])
    for j in range(margin_point):
      result.append(sgnl[i])
  return np.array(result)
##########################################################################################################
##########################################################################################################
def adjustPower(sig1, sig2):
  coef1 = np.sqrt(np.average(np.power(sig1,2.0)))
  coef2 = np.sqrt(np.average(np.power(sig2,2.0)))
  return sig1*coef2/coef1
def processingWaveletObj(w):
  wLen = len(w)
  bLen = len(w[0])
  coefStart = 0.0
  coefEnd = 1.0
  itrStart = 0.0
  itrEnd = 0.3
  deg = (coefEnd-coefStart)/(itrEnd*float(wLen)-itrStart*float(wLen))
  result = []
  for itr_a in range(wLen):
    result.append([])
    for itr_b in range(bLen):
      result[itr_a].append(0)
  for itr_a in range(wLen):
    if int(itrStart*float(wLen)) <= itr_a and itr_a <= int(itrEnd*float(wLen)):
      for itr_b in range(bLen):
        result[itr_a][itr_b] = 0#(w[itr_a][itr_b]/w[itr_a][itr_b]) * abs(w[itr_a][itr_b]) * (coefStart + deg * float(itr_a))
    else:
      for itr_b in range(bLen):
        result[itr_a][itr_b] = w[itr_a][itr_b]
  return np.array(result)
##########################################################################################################

# 信号読み込み
#wavelet = rickerWavelet
sig = None
a_list = None
if ohlc_flag:
  A_interval = 1#1.0/(N/2)/2
  ohlc = pd.read_csv(r"./../../resources/DAT_ASCII_EURUSD_M1_2007.csv", header=None, sep=";", names=('date','open',"high",'low','close','vomule'))
  if P != 0:
    sig = raisedCosineInterpolation(ohlc['close'][:N], P)
  else:
    if period <= 1:
      sig = np.array(ohlc['close'][:N])
    else:
      sig = np.array(pd.Series(ohlc['close'][:N]).rolling(5).mean())
      sig[:5] = sig[0]
  #a_list = np.array([float(i*A_interval) for i in range(1, A+1)])
  a_list = np.array([np.exp(i*0.5 - A/2) for i in range(1,A+1)])#np.arange(1, A+1)
else:
  A_interval = 1
  t = np.linspace(-1, 1, N, endpoint=False)
  sig_org  = np.cos(2 * np.pi * 7 * t) + np.sin(np.pi * 6 * t)
  if P != 0:
    sig = raisedCosineInterpolation(sig_org, P)
  else:
    sig = sig_org
  a_list = np.array([float(x*A_interval) for x in range(1,A+1)])#np.arange(1, A+1)
itrs_t = np.array([x for x in range(0,len(sig))])

# nim load
if graph_nim:
  dfs = pd.read_csv('signal_nim.csv', header=None)
  sig_list = []
  for elems in dfs.values:
    sig_list.append(np.array(elems))
  sig_nim = np.array(sig_list)

  dfw = pd.read_csv('wavelet.csv', header=None)
  cwtmatr_list = []
  for elems in dfw.values:
    cwtmatr_list.append(np.array(elems))
  cwtmatr_nim = np.array(cwtmatr_list)

  dfw2 = pd.read_csv('wavelet2.csv', header=None)
  cwtmatr2_list = []
  for elems in dfw2.values:
    cwtmatr2_list.append(np.array(elems))
  cwtmatr2_nim = np.array(cwtmatr2_list)

  dfi = pd.read_csv('signal_nim_inverse.csv', header=None)
  sig_inv_list = []
  for elems in dfi.values:
    sig_inv_list.append(np.array(elems))
  sig_inv_nim = np.array(sig_inv_list)

  dfi2 = pd.read_csv('signal_nim_inverse2.csv', header=None)
  sig_inv2_list = []
  for elems in dfi2.values:
    sig_inv2_list.append(np.array(elems))
  sig_inv2_nim = np.array(sig_inv2_list)
  sig_inv2_nim = adjustPower(sig_inv2_nim,sig_nim)

  with open('wavelet_nim.csv', 'w') as fp:
    for elems in cwtmatr_nim:
      for elem in elems:
        fp.write('{},'.format(elem))
      fp.write('\n')

# py processing
if graph_py:
  startTime = datetime.datetime.now()
  cwtmatr_py = []
  cwtmatr2_py = []
  sig_inv_py = []
  sig_inv2_py = []
  for itr_w in range(2):
    wavelet = rickerWavelet if itr_w == 0 else cosWavelet
    # DWT
    cwtmatr_py.append(cwt(sig, wavelet, itrs_t, a_list))

    # DWT
    sig_inv_py.append(icwt(cwtmatr_py[itr_w], wavelet, itrs_t, a_list))
    print('finish![{}] {}'.format(itr_w, datetime.datetime.now()-startTime))
    cwtmatr2_py.append(processingWaveletObj(cwtmatr_py[itr_w]))
    sig_inv2_py.append(icwt(cwtmatr2_py[itr_w], wavelet, itrs_t, a_list))
    sig_inv2_py[itr_w] = adjustPower(sig_inv2_py[itr_w],sig)

  #
  with open('signal_python.csv', 'w') as fp:
    for elem in sig:
      fp.write('{}\n'.format(elem))

#### plot
nRow = 3
nCol = 3
no = 0
fig = plt.figure(figsize=(19,9))
fig.subplots_adjust(wspace=0.4, hspace=0.6)

comment='''
no += 1
ax_py_sig = fig.add_subplot(nRow, nCol, no)
ax_py_sig.set_title('original signal')
ax_py_sig.plot([i for i in range(N)], ohlc['close'][:N] if ohlc_flag else sig_org)
'''

no += 1
if graph_py:
  ax_py_sig = fig.add_subplot(nRow, nCol, no)
  ax_py_sig.set_title('python_sig')
  ax_py_sig.plot(itrs_t, sig)
  ax_py_sig = fig.add_subplot(nRow, nCol, no+nCol, sharex=ax_py_sig if graph_py else None)
  ax_py_sig.set_title('python_sig')
  ax_py_sig.plot(itrs_t, sig)
if graph_nim:
  ax_nim_sig = fig.add_subplot(nRow, nCol, no+nCol*2, sharex=ax_py_sig if graph_py else None)
  ax_nim_sig.set_title('nim_sig')
  ax_nim_sig.plot(itrs_t, sig_nim)

comment='''
no += 1
X1, X2 = np.meshgrid(a_list, itrs_t)
if graph_py:
  ax_py_w = fig.add_subplot(nRow, nCol, no, projection='3d')
  ax_py_w.set_title('python_w[0]')
  y_plot = cwtmatr_py[0].reshape(X1.shape)
  im = ax_py_w.plot_surface(X1, X2, y_plot, linewidth=0)
  #im = ax_py_w.imshow(cwtmatr_py[0], aspect='auto', # cmap='PRGn',
  #          vmax=abs(cwtmatr_py[0]).max(), vmin=-abs(cwtmatr_py[0]).max())
  #fig.colorbar(im)
  ax_py_w = fig.add_subplot(nRow, nCol, no+nCol, projection='3d')
  ax_py_w.set_title('python_w[1]')
  y_plot = cwtmatr_py[1].reshape(X1.shape)
  im = ax_py_w.plot_surface(X1, X2, y_plot, linewidth=0)
  #im = ax_py_w.imshow(cwtmatr_py[1], aspect='auto', # cmap='PRGn',
  #          vmax=abs(cwtmatr_py[1]).max(), vmin=-abs(cwtmatr_py[1]).max())
  #fig.colorbar(im)
if graph_nim:
  ax_nim_w = fig.add_subplot(nRow, nCol, no+nCol*2, sharex=ax_py_w if graph_py else None, projection='3d')
  ax_nim_w.set_title('nim_w')
  y_plot = cwtmatr_nim.reshape(X1.shape)
  im = ax_nim_w.plot_surface(X1, X2, y_plot, linewidth=0)
  #im = ax_nim_w.imshow(cwtmatr_nim, aspect='auto',
  #          vmax=abs(cwtmatr_nim).max(), vmin=-abs(cwtmatr_nim).max())
  #fig.colorbar(im)
'''

no += 1
if graph_py:
  ax_py_inv = fig.add_subplot(nRow, nCol, no)
  ax_py_inv.set_title('python_inv[0]')
  ax_py_inv.plot(itrs_t, sig_inv_py[0])
  ax_py_inv = fig.add_subplot(nRow, nCol, no+nCol)
  ax_py_inv.set_title('python_inv[1]')
  ax_py_inv.plot(itrs_t, sig_inv_py[1])
if graph_nim:
  ax_nim_inv = fig.add_subplot(nRow, nCol, no+nCol*2, sharex=ax_py_inv if graph_py else None)
  ax_nim_inv.set_title('nim_inv')
  ax_nim_inv.plot(itrs_t, sig_inv_nim)

comment='''
no += 1
if graph_py:
  ax_py_w2 = fig.add_subplot(nRow, nCol, no)
  ax_py_w2.set_title('python_w2[0]')
  im = ax_py_w2.imshow(cwtmatr2_py[0], aspect='auto',
            vmax=abs(cwtmatr2_py[0]).max(), vmin=-abs(cwtmatr2_py[0]).max()) # 比較のため元データ使用
  fig.colorbar(im)
  ax_py_w2 = fig.add_subplot(nRow, nCol, no+nCol)
  ax_py_w2.set_title('python_w2[1]')
  im = ax_py_w2.imshow(cwtmatr2_py[1], aspect='auto',
            vmax=abs(cwtmatr2_py[1]).max(), vmin=-abs(cwtmatr2_py[1]).max()) # 比較のため元データ使用
  fig.colorbar(im)
if graph_nim:
  ax_nim_w2 = fig.add_subplot(nRow, nCol, no+nCol*2, sharex=ax_py_w2 if graph_py else None)
  ax_nim_w2.set_title('nim_w2')
  im = ax_nim_w2.imshow(cwtmatr2_nim, aspect='auto',
            vmax=abs(cwtmatr2_nim).max(), vmin=-abs(cwtmatr2_nim).max())
  fig.colorbar(im)
'''

no += 1
if graph_py:
  ax_py_inv2 = fig.add_subplot(nRow, nCol, no)
  ax_py_inv2.set_title('python_inv2[0]')
  ax_py_inv2.plot(itrs_t, sig_inv2_py[0])
  ax_py_inv2.plot(itrs_t, sig)
  ax_py_inv2 = fig.add_subplot(nRow, nCol, no+nCol)
  ax_py_inv2.set_title('python_inv2[1]')
  ax_py_inv2.plot(itrs_t, sig_inv2_py[1])
  ax_py_inv2.plot(itrs_t, sig)
if graph_nim:
  ax_nim_inv2 = fig.add_subplot(nRow, nCol, no+nCol*2, sharex=ax_py_inv2 if graph_py else None)
  ax_nim_inv2.set_title('nim_inv2')
  ax_nim_inv2.plot(itrs_t, sig_inv2_nim)
  ax_nim_inv2.plot(itrs_t, sig_nim)

plt.show()


nRow = 3
nColMax = A
nCol = 6
tb = np.linspace(0, len(cwtmatr_py if graph_py else cwtmatr2_nim), len(cwtmatr_py if graph_py else cwtmatr2_nim), endpoint=False)
for m in range(int(nColMax/nCol)+1):
  fig = plt.figure(figsize=(19,9))
  fig.subplots_adjust(wspace=0.4, hspace=0.6)
  for n in range(1,nCol+1):
    no = n+m
    if no > nColMax:
      break
    if graph_py:
      ax_py_w0 = fig.add_subplot(nRow, nCol, n)
      ax_py_w0.set_title('python_w0[0]')
      ax_py_w0.plot(itrs_t, cwtmatr_py[0][no-1])#[cwtmatr_py[x][n-1] for x in range(len(cwtmatr_py))])
      ax_py_w0 = fig.add_subplot(nRow, nCol, n+nCol)
      ax_py_w0.set_title('python_w0[1]')
      ax_py_w0.plot(itrs_t, cwtmatr_py[1][no-1])#[cwtmatr_py[x][n-1] for x in range(len(cwtmatr_py))])
    if graph_nim:
      ax_nim_w0 = fig.add_subplot(nRow, nCol, n+nCol*2, sharex=ax_py_w0 if graph_py else None)
      ax_nim_w0.set_title('nim_w0')
      ax_nim_w0.plot(itrs_t, cwtmatr_nim[no-1])#[cwtmatr_nim[x][n-1] for x in range(len(cwtmatr_nim))])
  plt.show()


