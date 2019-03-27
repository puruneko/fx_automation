import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import scipy.fftpack as spfft
import myfx.myind as myind
import myfx.myutil as myutil

def iirdesign_LPF(fc):
    """IIR版ローパスフィルタ、fc:カットオフ周波数"""
    a = [0.0] * 3
    b = [0.0] * 3
    denom = 1 + (2 * np.sqrt(2) * np.pi * fc) + 4 * np.pi**2 * fc**2
    b[0] = (4 * np.pi**2 * fc**2) / denom
    b[1] = (8 * np.pi**2 * fc**2) / denom
    b[2] = (4 * np.pi**2 * fc**2) / denom
    a[0] = 1.0
    a[1] = (8 * np.pi**2 * fc**2 - 2) / denom
    a[2] = (1 - (2 * np.sqrt(2) * np.pi * fc) + 4 * np.pi**2 * fc**2) / denom
    return a, b


def iir(x, a, b):
    """IIRフィルタをかける、x:入力信号、a, b:フィルタ係数"""
    y = [0.0] * len(x)  # フィルタの出力信号
    Q = len(a) - 1
    P = len(b) - 1
    for n in range(len(x)):
        for i in range(0, P + 1):
            if n - i >= 0:
                y[n] += b[i] * x[n - i]
        for j in range(1, Q + 1):
            if n - j >= 0:
                y[n] -= a[j] * y[n - j]
    return y


def LPF(spec, window, cutoff=2.):
    np_spec = spec.as_matrix()
    point = len(spec)
    dt = 1./window
    fs = 1./dt
    cutoff_analog = np.tan(cutoff * np.pi / fs) / (2. * np.pi)
    a, b = iirdesign_LPF(cutoff_analog)
    y = np.array([np.nan]*point)
    for i in range(window, point):
        _y = iir(np_spec[i-window:i],a,b)
        y[i] = _y[-1]
    lpf = pd.Series(y, index=spec.index)
    lpf = lpf*np.average(spec)/np.average(lpf)
    return lpf

def exp_palus(palus, x, tau):
    return palus*np.exp(-x/tau)

def exp_integral(palus, palusList, tau, period=4):
    palusList.append(list([palus,0]))
    _sum = 0
    for i in range(len(palusList)):
        v = exp_palus(palusList[i][0], palusList[i][1], tau)
        _sum += v
        palusList[i][1] += 1
    list_copy = palusList.copy()
    for i in range(len(list_copy)):
        if list_copy[i][1] >= tau*period:
            palusList.pop(i)
    return _sum

def exp_integral_max(chart, int_tau=60, int_period=4, int_att=1.):
    palusList = []
    _sum = 0
    _chart = chart.copy()
    for i in range(len(_chart)):
        if np.isnan(_chart[i]):
            continue
        palus = 0
        if _chart[i] > _chart[i-1]:
            palus = _chart[i]
        _chart[i] += _sum
        _sum = exp_integral(palus, palusList, int_tau, int_period)*int_att
    return _chart

def slope(line, window):
    '''incline(line, window)
    Calc slope of the line between window
    '''
    c = []
    dx = window
    for i in range(window):
        c.append(float('nan'))
    for i in range(window, len(line)):
        dy = line[i]-line[i-window]
        c.append(dy/dx)
    return pd.Series(c,index=line.index)

def to_binary(line, th=0, upper=1, lower=-1):
    b = np.zeros(len(line))+lower
    over = np.where(line > 0)[0]
    for i in over:
        b[i] = upper
    return pd.Series(b, index=line.index)

def intSeries(sr):
    return sr.fillna(0).astype(int)

def complex_power(c):
    return c.real*c.real+c.imag*c.imag

def windowFn_None(window):
    return 1
def windowFn_Double(window):
    return (-(2/window)**2*(np.arange(window)-window/2)**2)+1

def period_FFT(spec, fft_window, ref=0, period_coef=1,
               windowFn_name='Double', offset_big=3, offset_small=0):
    point = len(spec)
    st = int(offset_big)
    ed = int(fft_window/2)-int(offset_small)
    if(st > ed):
        raise SyntaxError("'st' must be larger than 'ed'")
    windowFn_dic = {'None': windowFn_None, 'Double':windowFn_Double}
    coef = fft_window*period_coef
    period = np.array([np.nan]*point)
    np_spec = spec.as_matrix()
    target = np_spec-ref
    offset = fft_window + len(target[np.isnan(target)])
    windowFn = windowFn_dic[windowFn_name]
    for i in range(offset, point):
        x = target[i-fft_window:i]
        if myutil.len_na(x) == 0:
            X = complex_power(spfft.fft(x))
            X = X * windowFn(fft_window)
            X_max = np.where(X[st:ed] == max(X[st:ed]))[0][0]+offset_big
            period[i] = int(np.ceil(coef/X_max)/2)
    return pd.Series(period,index=spec.index)

def period_FFT_live(line, fft_window, i,
                    period_coef=1, windowFn_name='Double',
                    offset_big=3, offset_small=0):
    if i < fft_window or np.isnan(fft_window):
        return np.nan
    st = int(offset_big)
    ed = int(fft_window/2)-int(offset_small)
    if(st > ed):
        raise SyntaxError("'st' must be larger than 'ed'")
    windowFn_dic = {'None': windowFn_None, 'Double':windowFn_Double}
    x = line[i-fft_window:i]
    x -= np.average(x)
    period = np.nan
    if not np.nan in x:
        X = complex_power(spfft.fft(x))
        X = X * windowFn_dic[windowFn_name](fft_window)
        X_max = np.where(X[st:ed] == max(X[st:ed]))[0][0]+offset_big
        period = int(np.ceil(fft_window*period_coef/X_max))
    return period

def LPF_FFT(spec, window, cutoff):
    np_spec = spec.as_matrix()
    point = len(np_spec)
    lpf = np.array([np.nan]*point)
    point_offset = max(window, len(spec[np.isnan(spec)]))
    for i in range(point_offset, point):
        y = np_spec[i-window:i]
        Y = spfft.fft(y)
        Y[cutoff:] = 0
        y = spfft.ifft(Y)
        lpf[i] = y[-1]
    return pd.Series(lpf, index=spec.index)

def centering(tar, ref, period):
    tar2_avg = myind.MA(tar**2, period)
    ref2_avg = myind.MA(ref**2, period)
    tar = tar/tar2_avg*ref2_avg
    return tar
