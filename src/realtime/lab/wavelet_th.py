import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import pandas as pd
from scipy import signal
import copy
import datetime

##########################################################################################################
N = 256
P = 4
A = 32
A_interval = 0.5
ma_period = 0
ohlc_flag = True
##########################################################################################################



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
##########################################################################################################
##########################################################################################################
def adjustPower(sig1, sig2):
  coef1 = np.sqrt(np.average(np.power(sig1,2.0)))
  coef2 = np.sqrt(np.average(np.power(sig2,2.0)))
  return sig1*coef2/coef1
def processingWaveletObj(w, th):
  wLen = len(w)
  bLen = len(w[0])
  coefStart = 0.0
  coefEnd = 1.0
  itrStart = 0.0
  itrEnd = th
  #deg = (coefEnd-coefStart)/(itrEnd*float(wLen)-itrStart*float(wLen))
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
def get_signal():
  sig = None
  sig_org = None
  a_list = None
  if ohlc_flag:
    ohlc = pd.read_csv(r"./../../resources/DAT_ASCII_EURUSD_M1_2007.csv", header=None, sep=";", names=('date','open',"high",'low','close','vomule'))
    sig_org = ohlc['close'][:N]
    if P != 0:
      sig = raisedCosineInterpolation2(sig_org, P)
    else:
      if ma_period <= 1:
        sig = np.array(sig_org)
      else:
        sig = np.array(pd.Series(sig_org).rolling(5).mean())
        sig[:5] = sig[0]
    #a_list = np.array([float(i*A_interval) for i in range(1, A+1)])
    a_list = np.array([np.exp(i*0.5 - A/2) for i in range(1,A+1)])#np.arange(1, A+1)
  else:
    t = np.linspace(-1, 1, N, endpoint=False)
    sig_org  = np.cos(2 * np.pi * 7 * t) + np.sin(np.pi * 6 * t)
    if P != 0:
      sig = raisedCosineInterpolation2(sig_org, P)
    else:
      sig = sig_org
    a_list = np.array([float(x*A_interval) for x in range(1,A+1)])#np.arange(1, A+1)
  itrs_t = np.array([x for x in range(0,len(sig))])
  return (sig, sig_org, a_list, itrs_t)

# py processing
def main():
  startTime = datetime.datetime.now()
  # setup
  wavelet = rickerWavelet
  th_list = (0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9)
  nRow = 3
  nCol = int((len(th_list))/nRow)+1
  no = 0
  fig = plt.figure(figsize=(19,9))
  fig.subplots_adjust(wspace=0.4, hspace=0.6)
  # signal
  (sig, sig_org, a_list, itrs_t) = get_signal()
  no += 1; ax = fig.add_subplot(nRow, nCol, no)
  ax.plot(itrs_t, sig, color='red')
  ax.plot(itrs_t, raisedCosineInterpolation(sig_org, P, 0.0), color='green')
  # DWT
  cwtmatr_py = cwt(sig, wavelet, itrs_t, a_list)
  for th in th_list:
    # DWT
    cwtmatr2_py = processingWaveletObj(cwtmatr_py, th)
    sig_inv_py = icwt(cwtmatr2_py, wavelet, itrs_t, a_list)
    sig_inv_py = adjustPower(sig_inv_py,sig)
    print('finish![{}] ({}[s])'.format(th, (datetime.datetime.now()-startTime).seconds))
    # plot
    no += 1; ax = fig.add_subplot(nRow, nCol, no)
    ax.set_title('inv(th={})'.format(th))
    ax.plot(itrs_t, sig_inv_py, color='blue')
    ax.plot(itrs_t, sig, color='red')
  plt.show()

if __name__ == '__main__':
  main()