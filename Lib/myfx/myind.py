import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import myfx.myutil as myutil

# Moving Average
def MA(line, period):
    '''MA(line, period)
    create Moving Average line
    '''
    return line.rolling(period).mean()

def MA_live(line, period, i):
    if i < period or np.isnan(period):
        return np.nan
    period = int(period)
    return np.average(line[i-period+1:i+1])

def EMA(line, period):
    '''EMA(line, period)
    create Exponentioal Moving Average line
    '''
    return line.ewm(period).mean()

def DL(line, delay):
    '''DL(line, delay)
    move the line by delay in time direction
    '''
    point_all = len(line)
    dl = []
    for i in range(0,delay):
        dl.append(float('nan'))
    for i in range(0, point_all):
        j = i -delay
        if j < 0 or j >= point_all:
            continue
        dl.append(line[j])
    for i in range(point_all+delay, point_all):
        dl.append(float('nan'))
    return pd.Series(dl, index=line.index)

def STD(line, period):
    return line.rolling(period).std(ddof=0)

def STD_live(line, period, i):
    if i < period or np.isnan(period):
        return np.nan
    period = int(period)
    return np.std(line[i-period+1:i+1])

def VSTD(line, list_period):
    lp = np.ceil(list_period)
    np_lp = lp.as_matrix()
    point = len(line)
    vSTD = np.array([np.nan]*point)
    std = {}
    set_period = set(lp.dropna())
    for s in set_period:
        std[s]=STD(line, int(s))
    nan_count = len(np.where(lp != lp)[0])
    offset = max(nan_count, int(max(set_period)))
    for i in range(offset, point):
        if not np.isnan(np_lp[i]):
            index = int(np_lp[i])
            vSTD[i] = std[index][i]
    return pd.Series(vSTD, index=line.index)

# BollingerBand
def BollingerBand(line, period, dev):
    '''BollingerBand(line, period, dev)
    create BollingerBand line
    line :line value
    period :period of BollingerBand
    dev: deviation
    '''
    base = MA(line, period)
    sgm = STD(line, period)
    upper = base + sgm*dev
    lower = base - sgm*dev
    return upper, lower

#MACD
def MACD(line, period_f=12, period_s=26, period_diff=9):
    '''MACD(line, period_f=12, period_s=26, period_diff=9)
    create MACD line
    '''
    fEMA = line.ewm(period_f).mean()
    sEMA = line.ewm(period_s).mean()
    diff_EMA = fEMA - sEMA
    signal = diff_EMA.ewm(period_diff).mean()
    return diff_EMA, signal

def DM(ohlc):
    '''Directional Movement'''
    point_all = len(ohlc)
    dm_p = np.zeros(point_all)
    dm_m = np.zeros(point_all)
    high = ohlc['high']
    low = ohlc['low']
    dm_p[0] = dm_m[0] = 0
    for i in range(1, point_all):
        p = high[i]-high[i-1]
        m = low[i] - low[i-1]
        dm_p[i] = p if p > 0 else 0
        dm_m[i] = m if m > 0 else 0
        dm_p[i],dm_m[i] = (dm_p[i],0) if dm_p[i] > dm_m[i] else (0,dm_m[i])
    return pd.Series(dm_p,index=ohlc.index), pd.Series(dm_m,index=ohlc.index)

def TR(ohlc):
    '''True Range'''
    point_all = len(ohlc)
    tr = np.zeros(point_all)
    tr[0] = 0
    for i in range(1, point_all):
        a = ohlc['high'][i] - ohlc['low'][i]
        b = ohlc['high'][i] - ohlc['close'][i-1]
        c = ohlc['close'][i-1] - ohlc['low'][i]
        tr[i] = max(a,b,c)
    return pd.Series(tr,index=ohlc.index)

# Direction Indicator
def DI(dm_p, dm_m, tr, DI_period=14):
    '''Direction Indicator'''
    di_p = dm_p.rolling(DI_period).sum()/tr.rolling(DI_period).sum()*100.
    di_m = dm_m.rolling(DI_period).sum()/tr.rolling(DI_period).sum()*100.
    return di_p, di_m

# Direction movement indeX
def DX(di_p, di_m):
    '''Direction movement indeX'''
    dx = np.abs(di_p-di_m)/(di_p+di_m)
    return dx


def ADX(ohlc, DI_period=14, ADX_period=9):
    '''ADX(ohlc, DI_period=14, ADX_period=9)
    Average Directionmovement indeX
    DI_period  : half of standard period (as a guide)
    ADX_period : one third of standard period (as a guide)
    ex) standard period:60 , DI:30,  ADX:20
    day criterion : DI:14, ADX:9
    '''
    dm_p, dm_m = DM(ohlc)
    tr = TR(ohlc)
    di_p, di_m = DI(dm_p, dm_m, tr, DI_period)
    dx = DX(di_p, di_m)
    adx = EMA(dx, ADX_period)
    return adx, di_p, di_m

def SDR(line, period, th):
    return MA(np.log10((line.diff().rolling(int(period)).std(ddof=0))**8)+th, period)

def VMA(line, list_period):
    lp = np.ceil(list_period)
    np_lp = lp.as_matrix()
    point = len(line)
    vMA = np.array([np.nan]*point)
    ma = {}
    set_period = set(lp.dropna())
    for s in set_period:
        ma[s]=MA(line, int(s))
    nan_count = len(np.where(lp != lp)[0])
    offset = max(nan_count, int(max(set_period)))
    for i in range(offset, point):
        if not np.isnan(np_lp[i]):
            index = int(np_lp[i])
            vMA[i] = ma[index][i]
    return pd.Series(vMA, index=line.index)


def VBB(line, list_period, deviation):
    lp = np.ceil(list_period)
    np_lp = lp.as_matrix()
    point = len(line)
    upper = np.array([np.nan]*point)
    lower = np.array([np.nan]*point)
    base = {}
    sgm = {}
    set_period = set(lp.dropna())
    for s in set_period:
        base[s] = MA(line, int(s))
        sgm[s] =  line.rolling(int(s)).std(ddof=0)
    nan_count = len(np.where(lp != lp)[0])
    offset = int(max(nan_count, max(set_period)))
    for i in range(offset, point):
        period_no = int(np_lp[i])
        upper[i] = base[period_no][i] + sgm[period_no][i]*deviation
        lower[i] = base[period_no][i] - sgm[period_no][i]*deviation
    return pd.Series(upper,index=line.index),pd.Series(lower,index=line.index)

def VBB_live(line, period, deviation, i):
    if i < period or np.isnan(period):
        return np.nan, np.nan
    base = MA_live(line, period, i)
    sgm = STD_live(line, period, i)*deviation
    upper = base + sgm
    lower = base - sgm
    return upper, lower

def MMax(line, window):
    return line.rolling(window).max()

def MMin(line, window):
    return line.rolling(window).min()

def log2_palus(palus, x, tau, base=2):
    return (-3.*base*palus/(4.*tau)*x)+palus*np.log(x/tau*(base-1)+1.)/np.log(base)

def ParaboricSeries(line, tau, tau_amplitude=0.1, log_base=6):
    pass


def ParaboricBand(line, tau, line_period=720, tau_amplitude=0.1, log_base=6):
    np_line = line.as_matrix()
    point = len(np_line)
    pP = [0,0,0,0,0] #[now,standard,zeroline,palus,index]
    pM = [1e10,0,0,0,0]
    pb_plus = np.array([np.nan]*point)
    pb_minus = np.array([np.nan]*point)
    pb_plus_index = np.zeros(point)
    pb_minus_index = np.zeros(point)
    offset = len(line[np.isnan(line)])
    for i in range(offset,point):
        if pP[0] < np_line[i]:# or pP[4] >= line_period:
            pP[0] = pP[1] = np_line[i]
            pP[2] = pM[1]
            pP[3] = tau_amplitude#(pP[1] - pP[2])*diff_coef
            pP[4] = 0
        else:
            pP[0] = pP[1] + log2_palus(pP[3], pP[4], tau, log_base)
            pP[4] += 1

        if pM[0] > np_line[i]:# or pM[4] >= line_period:
            pM[0] = pM[1] = np_line[i]
            pM[2] = pP[1]
            pM[3] = tau_amplitude#(pM[2] - pM[1])*diff_coef
            pM[4] = 0
        else:
            pM[0] = pM[1] - log2_palus(pM[3], pM[4], tau, log_base)
            pM[4] += 1
        pb_plus[i] = pP[0]
        pb_minus[i] = pM[0]
        pb_plus_index[i] = pP[4]
        pb_minus_index[i] = pM[4]
    return pd.Series(pb_plus,index=line.index), pd.Series(pb_minus,index=line.index),\
            pd.Series(pb_plus_index,index=line.index), pd.Series(pb_minus_index,index=line.index)

def LRC(line, window):   #Linear Regression Coefficient
    np_line = line.as_matrix()
    point = len(np_line)
    point_offset = len(line[np.isnan(line)])
    LRc = np.array([np.nan]*point)
    _x = np.arange(window)
    for i in range(window+point_offset, point):
        _y = np_line[i-window:i]
        a, b = np.polyfit(_x, _y, 1)
        LRc[i] = a
    return pd.Series(LRc, index=line.index)

def LRC_live(line, window, i):
    if i < window or np.isnan(window):
        return np.nan
    window = int(window)
    _x = np.arange(window)
    _y = line[i-window+1:i+1]
    if True in np.isnan(_y):
        return np.nan
    a, b = np.polyfit(_x, _y, 1)
    return a

def VLRC(line, list_period):
    lp = np.ceil(list_period)
    point = len(line)
    vLRC = np.array([np.nan]*point)
    set_period = set(lp.dropna())
    lrc_dic = {}
    lrc_nan_count = [0]*len(set_period)
    for i in range(len(set_period)):
        s = int(set_period.pop())
        lrc = LRC(line, s)
        lrc_nan_count[i] = len(np.where(lrc != lrc)[0])
        lrc_dic[s] = lrc
    nan_count = len(np.where(lp != lp)[0])
    for i in range(nan_count):
        vLRC[i] = np.nan
    offset = max(nan_count, int(max(lrc_nan_count)))
    for i in range(offset, point):
        vLRC[i] = lrc_dic[int(lp[i])][i]
    return pd.Series(vLRC, index=line.index)

def LRL(line, window):#Linear Regression Line
    np_line = line.as_matrix()
    point = len(np_line)
    point_offset = len(line[np.isnan(line)])
    LRl = np.array([np.nan]*point)
    _x = np.arange(window)
    for i in range(window+point_offset, point):
        _y = np_line[i-window:i]
        if myutil.len_na(_y) == 0:
            a, b = np.polyfit(_x, _y, 1)
            LRl[i] = (a*_x+b)[-1]
    return pd.Series(LRl, index=line.index)

def LRL_live(line, window, i):
    if i < window or np.isnan(window):
        return np.nan
    window = int(window)
    _x = np.arange(window)
    _y = line[i-window+1:i+1]
    if True in np.isnan(_y):
        return np.nan
    a, b = np.polyfit(_x, _y, 1)
    return (a*_x+b)[-1]

def VLRL(line, list_period):
    lp = np.ceil(list_period)
    point = len(line)
    vLRL = np.array([np.nan]*point)
    set_period = set(lp.dropna())
    lrl_dic = {}
    lrl_nan_count = [0]*len(set_period)
    for i in range(len(set_period)):
        s = int(set_period.pop())
        lrl = LRL(line, s)
        lrl_nan_count[i] = len(np.where(lrl != lrl)[0])
        lrl_dic[s] = lrl
    nan_count = len(np.where(lp != lp)[0])
    for i in range(nan_count):
        vLRL[i] = np.nan
    offset = max(nan_count, int(max(lrl_nan_count)))
    for i in range(offset, point):
        vLRL[i] = lrl_dic[int(lp[i])][i]
    return pd.Series(vLRL, index=line.index)

def ParaboricSeries_init(side):
    if side=='upper':
        return {'paraboric':-1.0e10,'intercept':0,'log_start':0,'log_x':0,'itr':0}
    elif side=='lower':
        return {'paraboric':+1.0e10,'intercept':0,'log_start':0,'log_x':0,'itr':0}
    return None

def ParaboricSeries(uplow, memory, spec_now, tau, tau_amplitude, log_base):
    if np.isnan(spec_now):
        memory = ParaboricSeries_init('upper' if uplow>0 else 'lower')
        memory['paraboric'] = spec_now
    else:
        if memory['paraboric']*uplow < spec_now*uplow:
            memory['paraboric'] = memory['intercept'] = spec_now
            memory['log_start'] = tau_amplitude#(pP[1] - pP[2])*diff_coef
            memory['itr'] = memory['log_x'] = 0
        else:
            _log = log2_palus(memory['log_start'], memory['log_x'], tau, log_base)*uplow
            memory['paraboric'] = memory['intercept'] + _log
            memory['log_x'] += 1
            memory['itr'] += 1
    return memory['paraboric'], memory['itr']

def ParaboricSeries_upper(memory, spec_now, tau, tau_amplitude=0.1, log_base=6):
    return ParaboricSeries(+1., memory, spec_now, tau, tau_amplitude, log_base)

def ParaboricSeries_lower(memory, spec_now, tau, tau_amplitude=0.1, log_base=6):
    return ParaboricSeries(-1., memory, spec_now, tau, tau_amplitude, log_base)

def _MMax(memory, spec_now, window):
    memory[1] += 1
    if memory[1] > window:
        memory[0] = -1.0e10
    if memory[0] < spec_now:
        memory[0] = spec_now
        memory[1] = 0
    return memory[0]

def _MMin(memory, spec_now, window):
    memory[1] += 1
    if memory[1] > window:
        memory[0] = +1.0e10
    if memory[0] > spec_now:
        memory[0] = spec_now
        memory[1] = 0
    return memory[0]

def distance(spec, window):
    np_spec = spec.as_matrix()
    point = len(np_spec)
    np_d = np.array([np.nan]*point)
    offset = int(len(np_spec[np.isnan(np_spec)]))
    bias = np.arange(window)/window
    for i in range(offset+window, point):
        spec_window = np_spec[i-window:i]
        d = 0
        for j in range(window):
            for k in range(window):
                x = (k-j)**2
                y = spec_window[k]-spec_window[j]
                d += np.sqrt(x**2+y**2)*bias[k]
        d /= (window-1)**2
        np_d[i] = d
    return pd.Series(np_d, index=spec.index)

def VSGMA(spec, list_period):
    lp = np.ceil(list_period)
    point = len(spec)
    vSGMA = np.array([np.nan]*point)
    set_period = set(lp.dropna())
    lrc_dic = {}
    lrc_nan_count = [0]*len(set_period)
    std_dic = {}
    std_nan_count = [0]*len(set_period)
    for i in range(len(set_period)):
        s = int(set_period.pop())
        lrc = LRC(spec, s)
        lrc_nan_count[i] = len(np.where(lrc != lrc)[0])
        lrc_dic[s] = lrc
        std = STD(spec, s)
        std_nan_count[i] = len(np.where(std != std)[0])
        std_dic[s] = std
    lp_nan_count = len(np.where(lp != lp)[0])
    nan_count = max(max(lrc_nan_count),max(std_nan_count))
    offset = max(nan_count, lp_nan_count)
    for i in range(offset, point):
        vSGMA[i] = lrc_dic[int(lp[i])][i] * std_dic[int(lp[i])][i]
    return pd.Series(vSGMA, index=spec.index)

def MAC(spec, period):
    ma = MA(spec, period)
    ma2_avg = MA(ma**2, period)
    spec2_avg = MA(spec**2, period)
    ma = ma/ma2_avg*spec2_avg
    return ma

def VMAC(spec, list_period, avg_coef=1):
    vma = VMA(spec, list_period)
    vma2_avg = VMA(vma**2, list_period/avg_coef)
    spec2_avg = VMA(spec**2, list_period/avg_coef)
    ma = vma/vma2_avg*spec2_avg
    return ma

def ALRC(spec, window):   #Linear Regression Coefficient
    np_spec = spec.as_matrix()
    point = len(np_spec)
    point_offset = len(spec[np.isnan(spec)])
    LRc = np.array([np.nan]*point)
    _x = np.arange(window)
    alpha = np.exp(np.arange(window)/window)-1
    for i in range(window+point_offset, point):
        _y = np_spec[i-window:i]
        avg = np.average(_y)
        _y = np.array([(_y[i]-avg)*alpha[i] for i in range(window)])
        a, b = np.polyfit(_x, _y, 1)
        LRc[i] = a
    return pd.Series(LRc, index=spec.index)

def VLRL(spec, list_period):
    lp = np.ceil(list_period)
    point = len(spec)
    vLRL = np.array([np.nan]*point)
    set_period = set(lp.dropna())
    lrl_dic = {}
    lrl_nan_count = [0]*len(set_period)
    for i in range(len(set_period)):
        s = int(set_period.pop())
        lrl = LRL(spec, s)
        lrl_nan_count[i] = len(np.where(lrl != lrl)[0])
        lrl_dic[s] = lrl
    nan_count = len(np.where(lp != lp)[0])
    for i in range(nan_count):
        vLRL[i] = np.nan
    offset = max(nan_count, int(max(lrl_nan_count)))
    for i in range(offset, point):
        vLRL[i] = lrl_dic[int(lp[i])][i]
    return pd.Series(vLRL, index=spec.index)

def GAP(tar, ref, window):
    np_tar = tar.as_matrix()
    np_ref = ref.as_matrix()
    point = len(np_tar)
    gap = np.array([np.nan]*point)
    for i in range(window,point):
        gap[i] = np.sum(np_tar[i-window:i] - np_ref[i-window:i])
    return pd.Series(gap, index=tar.index)

def GAP_live(tar, ref, window, i):
    if i < window or np.isnan(window):
        return np.nan
    window = int(window)
    gap = np.sum(np.array(tar[i-window+1:i+1]) - np.array(ref[i-window+1:i+1]))
    return gap

def VGAP(tar,ref, list_period):
    np_tar = tar.as_matrix()
    np_ref = ref.as_matrix()
    point = len(np_tar)
    gap = np.array([np.nan]*point)
    lp = np.ceil(list_period)
    np_lp = lp.as_matrix()
    set_period = set(lp.dropna())
    offset = int(max(set_period))
    for i in range(offset, point):
        if not np.isnan(np_lp[i]):
            window = int(np_lp[i])
            gap[i] = np.sum(np_tar[i-window:i] - np_ref[i-window:i])
    return pd.Series(gap, index=tar.index)

def DEV_live(tar, ref, window, i):
    if i < window or np.isnan(window):
        return np.nan
    window = int(window)
    dev = np.average((np.array(tar[i-window+1:i+1]) - np.array(ref[i-window+1:i+1]))**2)
    return dev

def VBB2(spec, list_period, dev_base, list_dev, dev_coef=2):
    lp = np.ceil(list_period)
    np_lp = lp.as_matrix()
    point = len(spec)
    upper = np.array([np.nan]*point)
    lower = np.array([np.nan]*point)
    sgm = {}
    set_period = set(lp.dropna())
    for s in set_period:
        sgm[s] =  spec.rolling(int(s)).std(ddof=0)
    vma = VMA(spec, list_period)
    for i in range(point):
        if not np.isnan(np_lp[i]):
            period_no = int(np_lp[i])
            upper[i] = vma[i] + sgm[period_no][i]*(dev_base+list_dev[i]*dev_coef)
            lower[i] = vma[i] - sgm[period_no][i]*(dev_base-list_dev[i]*dev_coef)
    return pd.Series(upper,index=spec.index),pd.Series(lower,index=spec.index)

def slope2deg(slope):
    point = len(slope)
    deg = np.array([np.nan]*point)
    for i in range(point):
        deg[i] = np.arctan2(slope[i], 1)

def VBB3(spec, list_period, dev_base, slope, period_max, period_min, deg_limit, list_dev, dev_coef):
    lp = np.ceil(list_period)
    np_lp = lp.as_matrix()
    point = len(spec)
    upper = np.array([np.nan]*point)
    lower = np.array([np.nan]*point)

    sgm = {}
    set_period = set(lp.dropna())
    for s in set_period:
        sgm[s] =  spec.rolling(int(s)).std(ddof=0)

    deg = np.abs(np.arctan2(slope, 1.)/(2.*np.pi)*360.)
    list_period_vbb = -(period_max-period_min)/deg_limit*deg+period_max
    list_period_vbb[list_period_vbb < period_min] = period_min
    vma = VMA(spec, list_period_vbb)

    for i in range(point):
        if not np.isnan(np_lp[i]):
            period_no = int(np_lp[i])
            upper[i] = vma[i] + sgm[period_no][i]*dev_base+list_dev[i]*dev_coef
            lower[i] = vma[i] - sgm[period_no][i]*dev_base-list_dev[i]*dev_coef
    return pd.Series(upper,index=spec.index),pd.Series(lower,index=spec.index),list_period_vbb

def Band(spec, period, dev):
    lrl = LRL(spec, period)
    std = STD(spec, period)
    upper = lrl + std*dev
    lower = lrl - std*dev
    return upper, lower

def Band_LRC(upper, lower, period):
    lrc_upper = LRC(upper, period)
    lrc_lower = LRC(lower, period)
    point = len(upper)
    lrc = np.array([np.nan]*point)
    for i in range(point):
        lrc[i] = lrc_upper[i] if np.abs(lrc_upper[i]) > np.abs(lrc_lower[i]) else lrc_lower[i]
    return pd.Series(lrc, index=upper.index)

def Band_deviation(spec, upper, lower, window):
    np_spec = spec.as_matrix()
    np_upper = upper.as_matrix()
    np_lower = lower.as_matrix()
    np_center = (np_upper+np_lower)/2
    point = len(np_spec)
    dev = np.array([np.nan]*point)
    for i in range(window, point):
        inbound_range = np.average(np_upper[i-window:i]-np_lower[i-window:i])/2
        dev[i] = np.average(np_spec[i-window:i]-np_center[i-window:i])/inbound_range
    return pd.Series(dev, index=spec.index)

def band_gap(upper, lower, window, i):
    if i < window or np.isnan(window):
        return np.nan
    window = int(window)
    gap = np.average([upper[c]-lower[c] for c in range(i-window+1,i+1)])
    return gap

def band_polalization(line, upper, lower, window, i):
    if i < window or np.isnan(window):
        return np.nan
    window = int(window)
    gap = [line[c]-(upper[c]+lower[c])/2 for c in range(i-window+1,i+1)]
    inbound = band_gap(upper, lower, window, i)/2
    dev = np.average(gap)
    return dev/inbound

def adaptivizeBand(line, upper, lower, window, inner_rate, move_rate, i):
    if i < window or np.isnan(window):
        return np.nan, np.nan
    window = int(window)
    gap = [line[c]-(upper[c]+lower[c])/2 for c in range(i-window+1,i+1)]
    inbound = np.average([(upper[c]-lower[c]) for c in range(i-window+1,i+1)])/2
    dev_p = np.average(gap)/inbound
    move = 0
    a = b = 0
    if np.abs(dev_p) > 1.:
        a = inbound
        b = 0
    else:
        inner = inbound*inner_rate/100.
        a = (inbound-inner)
        b = inner
        if dev_p < 0:
            b = (-1)*b
    move = (a*dev_p + b)*move_rate/100.
    upper = upper[-1] + move
    lower = lower[-1] + move
    return upper, lower

def VBB_live(line, base_period, sgm_period, deviation, i):
    if i < base_period or np.isnan(base_period)\
        or i < sgm_period or np.isnan(sgm_period):
        return np.nan, np.nan
    base = myind.MA_live(line, base_period, i)
    sgm = myind.STD_live(line, sgm_period, i)*deviation
    upper = base + sgm
    lower = base - sgm
    return upper, lower

def SPEED(line, period, unitX=1, unitY=100):
    np_line = line.as_matrix()
    point = len(np_line)
    speed = np.array([np.nan]*point)
    _x = np.arange(period)*unitX
    for i in range(period, point):
        _y = line[i-period+1:i+1]
        if True in np.isnan(_y):
            continue
        dist = _y[-1]-_y[0]
        time = _x[-1]-_x[0]
        s = dist/time
        speed[i] = s
    return pd.Series(speed, index=line.index)

def speed_live(line, period, i, unitX=1, unitY=100):
    if i < period or np.isnan(period):
        return np.nan
    period = int(period)
    _x = np.arange(period)*unitX
    _y = line[i-period+1:i+1]
    if True in np.isnan(_y):
        return np.nan
    dist = _y[-1]-_y[0]
    time = _x[-1]-_x[0]
    speed = dist/time
    return speed

def WMA_live(line, period, i):
    if i < period or np.isnan(period):
        return np.nan
    period = int(period)
    coef = np.arange(period)
    wma_series = np.array(line[i-period+1:i+1])*coef/np.average(coef)
    return np.average(wma_series)

def WDEV_live(sig, ref, period, i):
    if i < period or np.isnan(period):
        return np.nan
    period = int(period)
    coef = np.arange(period)
    gap = np.array(sig[i-period+1:i+1])-np.array(ref[i-period+1:i+1])
    wdev_series = (gap)**2*coef/np.average(coef)
    return np.average(wdev_series)

def WSTD_live(line, period, i):
    avg = [np.average(line)]*len(line)
    return WDEV_live(line, avg, period, i)

def LATL_init(latl_init):
        return {'latl_now':latl_init,'latl_past':latl_init,'speed':0,'itr':0}

def LATL_live(uplow, memory, line_entry, line_exit, line_speed,
              speed_coef, est_coef, margin, margin_offset, cmp_bias,
              period_ready, period_speed, unitX, unitY, i): # Line Along The Line
    if np.isnan(line_entry[i]) or np.isnan(line_exit[i]) or np.isnan(line_speed[i]):
        memory = LATL_init(np.nan)
    else:
        latl_est = mysig.estimated_rate(memory['latl_past'], memory['latl_now'], est_coef)
        exit_est = mysig.estimated_rate(line_exit[i-1], line_exit[i], est_coef)
        line_entry_bias = line_entry[i]+cmp_bias*uplow
        if (memory['itr'] <= period_ready and memory['latl_now']*uplow < line_entry_bias*uplow)\
           or (memory['itr'] > period_ready and latl_est*uplow < exit_est*uplow):
            memory['latl_past']  = memory['latl_now']
            memory['latl_now']   = line_entry[i]
            memory['itr']   = 0
            memory['speed'] = 0
        else:
            speed = speed_live(line_speed, period_speed, i, unitX, unitY)
            memory['speed'] = speed if speed*uplow<0 else 0#-speed#memory['speed']
            if memory['itr'] < period_ready:
                if False:#speed*uplow > 0:
                    memory['latl_past']  = memory['latl_now']
                    memory['latl_now']   = line_entry[i]
                    memory['itr']   = 0
                    memory['speed'] = 0
                else:
                    memory['latl_past'] = memory['latl_now']
                    if memory['itr'] == 0:
                        memory['latl_now'] = line_entry[i]
                    else:
                        memory['latl_now'] = margin_offset/period_ready*uplow*(-1) + memory['latl_now'] # ax+b|x=1 (as 1 candle stick)
                    memory['itr']  += 1
            else:
                memory['latl_past'] = memory['latl_now']
                if memory['itr'] == period_ready:
                    memory['latl_now'] = memory['latl_now'] + margin*uplow
                else:
                    memory['latl_now'] = speed_coef*memory['speed'] + memory['latl_now'] # ��ax+b|x=1 (as 1 candle stick)
                memory['itr']  += 1
    return memory['latl_now'], memory['itr']

def LATL_upper_live(memory, line_entry, line_exit, line_speed,
                    speed_coef, est_coef, margin, margin_offset, cmp_bias,
                    period_ready, period_speed, unitX, unitY, i):
    return LATL_live(+1, memory, line_entry, line_exit, line_speed,
                     speed_coef, est_coef, margin, margin_offset, cmp_bias,
                     period_ready, period_speed, unitX, unitY, i)

def LATL_lower_live(memory, line_entry, line_exit, line_speed,
                    speed_coef, est_coef, margin, margin_offset, cmp_bias,
                    period_ready, period_speed, unitX, unitY, i):
    return LATL_live(-1, memory, line_entry, line_exit, line_speed,
                     speed_coef, est_coef, margin, margin_offset, cmp_bias,
                     period_ready, period_speed, unitX, unitY, i)

def cross_frequency_init():
    return {'counter':0, 'value':False}

def cross_frequency(memory, line_f, line_s, count_limit, i):
    if mysig.cross_line(line_f, i, line_s) != 0:
        if memory['counter'] < count_limit:
            memory['value'] = True
        memory['counter'] = 0
    else:
        memory['counter'] += 1
        if memory['counter'] >= count_limit:
            memory['value'] = False
    return memory['value']

def diff_frequency_init():
    return {'counter':0, 'value':False}

def diff_frequency(memory, diff, loc, count_limit, i):
    if mysig.cross_loc(diff, i, loc) < 0 or mysig.cross_loc(diff, i, -loc) > 0:
        if memory['counter'] < count_limit:
            memory['value'] = True
        memory['counter'] = 0
    else:
        memory['counter'] += 1
        if memory['counter'] >= count_limit:
            memory['value'] = False
    return memory['value']

def updown(line, thresh, i):
    if line[i] > thresh:
        return 1
    elif line[i] < -thresh:
        return -1
    return 0
def easyFFT(line):
    np_line = line.as_matrix()
    avg = np.average(np_line)
    np_LINE = spfft.fft(np_line-avg)
    return np_LINE

def highlow_itr_new(itr, period, th):
    np_itr = itr.as_matrix()
    point = len(np_itr)
    new_itr = np.array([np.nan]*point)
    base = 0
    record = 0
    for i in range(point):
        v = np_itr[i]
        if v <= th:
            if base == 0:
                base = record = np_itr[i-1]
            base -= record/period
            if base <= 0:
                base = 0
        new_itr[i] = base + v
    return pd.Series(new_itr, index=itr.index)

def distance(line, period):
    np_line = line.as_matrix()
    point = len(np_line)
    d = np.array([np.nan]*point)
    for i in range(period,point):
        d[i] = np.sqrt((line[i]-line[i-period])**2+period**2)-period
    return pd.Series(d, index=line.index)

def DI(line, period):
    np_line = line.as_matrix()
    point = len(np_line)
    d = np.array([np.nan]*point)
    for i in range(period,point):
        d[i] = np.abs(line[i]-line[i-period])
    return pd.Series(d, index=line.index)
def DI_live(line, period, i):
    if i < period or np.isnan(period):
        return np.nan
    return np.abs(line[i]-line[i-period])
def V0(line, period):
    np_line = line.as_matrix()
    point = len(np_line)
    d = np.array([np.nan]*point)
    for i in range(period,point):
        d[i] = np.sum([np.abs(line[i-period+j]-line[i-period+j+1]) for j in range(period-1)])
    return pd.Series(d, index=line.index)
def V0_live(line, period, i):
    if i < period or np.isnan(period):
        return np.nan
    return np.sum([np.abs(line[i-period+j]-line[i-period+j+1]) for j in range(period-1)])
def ER(line, period):
    di = DI(line, period)
    v0 = V0(line, period)
    return di/v0
def ER_live(line, period, i):
    if i < period or np.isnan(period):
        return np.nan
    di = DI_live(line, period, i)
    v0 = V0_live(line, period, i)
    return di/v0
