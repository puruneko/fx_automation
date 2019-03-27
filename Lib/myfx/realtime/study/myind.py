import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import re
import types
import pywt

class Indicator():

    def __init__(self, default=None, func=None, forTransactionMarker=False, update_flag=True, scalar=False, **kwargs_for_func):
        self._value = [] if default is None else [default]
        self.append = self._value.append
        self._set_update_function(func)
        self.kwargs_for_func = kwargs_for_func
        self.update_flag = update_flag
        self.scalar = scalar

    def __len__(self):
        return len(self._value)

    def __contains__(self, x):
        return x in self._value

    def __getitem__(self, i):
        return self._value[i]

    def __add__(self, y):
        _y = y if isinstance(y,np.ndarray) else np.array(y)
        ans = list(np.array(self._value)+_y)
        return self._copy_param(ans)

    def __sub__(self, y):
        _y = y if isinstance(y,np.ndarray) else np.array(y)
        ans = list(np.array(self._value)-_y)
        return self._copy_param(ans)

    def __mul__(self, y):
        _y = y if isinstance(y,np.ndarray) else np.array(y)
        ans = list(np.array(self._value)*_y)
        return self._copy_param(ans)

    def __truediv__(self, y):
        _y = y if isinstance(y,np.ndarray) else np.array(y)
        ans = list(np.array(self._value)/_y)
        return self._copy_param(ans)

    def _copy_param(self, value):
        return Indicator(   default=value,
                            func=self.update_func,
                            **self.kwargs_for_func)

    def _set_update_function(self, func):
        self.update_func = func

    def newest(self):
        return self._value[-1]

    def append(self, value):
        self.append(value)

    def get(self, i):
        return self._value[i]
    def set(self, i, value):
        self._value[i] = value

    def update(self, i):
        if self.update_func is not None and self.update_flag==True:
            kwargs = {}
            for key in self.kwargs_for_func:
                # If type of kwargs for function is FunctionType or MethodType,
                # execute it.
                if type(self.kwargs_for_func[key]) is types.FunctionType\
                   or type(self.kwargs_for_func[key]) is types.MethodType:
                    kwargs[key] = self.kwargs_for_func[key]()
                else:
                    kwargs[key] = self.kwargs_for_func[key]
            v = self.update_func(self, i, **kwargs)
            self.append(v)
            if self.scalar and i != 0:
                self._value[i-1] = np.nan

    def set_update_argument(self, key, value):
        self.kwargs_for_func[key] = value

def NAN_live(self, i):
    return np.nan

def PASS_live(self, i, line):
    if np.isnan(i):
        return np.nan
    return line[i]

def STEADY_live(self,i):
    if self._value == []:
        return np.nan
    return self.newest()

def ADD_live(self, i, **kwargs):
    if np.isnan(i):
        return np.nan
    elem = []
    for key in kwargs.keys():
        if isinstance(kwargs[key],Indicator):
            elem.append(kwargs[key][i])
        else:
            elem.append(kwargs[key])
    return np.sum(elem)

def SUB_live(self, i, **kwargs):
    if np.isnan(i):
        return np.nan
    num = len(kwargs)
    elem = [0]*num
    for key in kwargs.keys():
        mt = int(re.match(r'(\D+)(\d+)',key).group(2))-1
        if isinstance(kwargs[key],Indicator):
            elem[mt] = kwargs[key][i]
        else:
            elem[mt] = kwargs[key]
        elem[mt] = -elem[mt] if mt != 0 else elem[mt]
    return np.sum(elem)

def MUL_live(self, i, **kwargs):
    if np.isnan(i):
        return np.nan
    elem = []
    for key in kwargs.keys():
        if isinstance(kwargs[key],Indicator):
            elem.append(kwargs[key][i])
        else:
            elem.append(kwargs[key])
    return np.prod(elem)

def DIV_live(self, i, **kwargs):
    if np.isnan(i):
        return np.nan
    num = len(kwargs)
    elem = [1]*num
    for key in kwargs.keys():
        mt = int(re.match(r'(\D+)(\d+)',key).group(2))-1
        if isinstance(kwargs[key],Indicator):
            if kwargs[key][i] != 0:
                elem[mt] = kwargs[key][i]
        else:
            if kwargs[key] != 0:
                elem[mt] = kwargs[key]
        elem[mt] = 1./elem[mt] if (mt != 0 and elem[mt] != 0) else elem[mt]
    return np.prod(elem)

def LOG_live(self, i, line):
    if np.isnan(i):
        return np.nan
    return np.log(line[i])

def ABS_live(self, i, line):
    if np.isnan(i):
        return np.nan
    return np.abs(line[i])

def shift_time_live(self, i, line, shift):
    if np.isnan(i) or i < shift:
        return np.nan
    return line[i-shift]

def complex_power(c):
    return c.real*c.real+c.imag*c.imag
def windowFn_None(window):
    return 1
def windowFn_Double(window):
    return (-(2/window)**2*(np.arange(window)-window/2)**2)+1
def period_FFT_live(self, i, line, fft_window,
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
    return int(period)


def MA_live(self, i, line, period):
    if i < period or np.isnan(period):
        return np.nan
    period = int(period)
    return np.average(line[i-period+1:i+1])

def WMA_live(self, i, line, period, weight=1):
    if i < period or np.isnan(period):
        return np.nan
    period = int(period)
    coef = np.arange(period)*weight
    return np.sum(np.array(line[i-period+1:i+1])*coef)/np.sum(coef)

def STD_live(self, i, line, period):
    if i < period or np.isnan(period):
        return np.nan
    period = int(period)
    return np.std(line[i-period+1:i+1])

def BB_upper_live(self, i, line, period, deviation):
    if i < period or np.isnan(period):
        return np.nan
    base = MA_live(i, line, period)
    sgm = STD_live(i, line, period)*deviation
    upper = base + sgm
    return upper

def BB_lower_live(self, i, line, period, deviation):
    if i < period or np.isnan(period):
        return np.nan
    base = MA_live(i, line, period)
    sgm = STD_live(i, line, period)*deviation
    lower= base - sgm
    return lower

def speed_live(self, i, line, period, unitX=1, unitY=100):
    ''' as pips '''
    if i < period or np.isnan(period):
        return np.nan
    period = int(period)
    _x = np.arange(period)*unitX
    _y = np.array(line[i-period+1:i+1])*unitY
    if True in np.isnan(_y):
        return np.nan
    dist = _y[-1]-_y[0]
    time = _x[-1]-_x[0]
    speed = dist/time
    return speed

def highlow_band_init(line_now):
    return {'start':np.nan, 'value':line_now, 'itr':0}

def highlow_band_live(self, i, highlow, memory, line_value, line_exit, period_wait, speed):
    # error processing
    if np.isnan(line_value[i]) or np.isnan(line_exit[i]):
        memory = highlow_band_init(np.nan)
    # not error processing
    else:
        # If highlow indicator is equal to NAN,
        # highlow indicator is current value of 'line_value'.
        if np.isnan(memory['value']):
            memory['value'] = line_value[i]
        # If highlow indicator is lower than 'line_value',
        #    memory is initialized to current value of 'line_value'.
        if (memory['itr'] == 0 and memory['value']*highlow < line_value[i]*highlow)\
           or (memory['itr'] != 0 and memory['value']*highlow < line_value[i]*highlow\
                                  and memory['value']*highlow < line_exit[i]*highlow):
            memory['start'] = np.nan
            memory['value'] = line_value[i]
            memory['itr'] = 0
        # If highlow indicator is higher than 'line_value',
        #    indicator value is created.
        else:
            # first value is memorized.
            if memory['itr'] == 0:
                memory['start'] = line_value[i]
            # iterator increament
            memory['itr'] += 1
            # highlow value is added by speed.
            memory['value'] += speed
    # return value and iterator
    return memory['value']#, memory['itr']

def high_line_live(self, i, memory, line_value, line_exit, period_wait, speed):
    speed_high = speed if speed < 0 else -speed
    return highlow_band_live(self, i, +1, memory, line_value, line_exit, period_wait, speed_high)

def low_line_live(self, i, memory, line_value, line_exit, period_wait, speed):
    speed_low = speed if speed > 0 else -speed
    return highlow_band_live(self, i, -1, memory, line_value, line_exit, period_wait, speed_low)

def highslows_line_live(self, i, memory, limit):
    if np.isnan(i) or i == 0:
        return np.nan
    if memory['itr'] < limit:
        return self.newest()
    return memory['start']

def highs_line_live(self, i, line, period, margin):
    if np.isnan(i) or i < period+margin:
        return np.nan
    line_window = line[i-period-margin+1:i-margin+1]
    return sorted(line_window, key=lambda x:-x)[0]

def lows_line_live(self, i, line, period, margin):
    if np.isnan(i) or i < period+margin:
        return np.nan
    line_window = line[i-period-margin+1:i-margin+1]
    return sorted(line_window)[0]

def shift_power_live(self, i, sig, ref, period):
    if i < period or np.isnan(period):
        return np.nan
    avg_sig2 = np.average(np.array(sig[i-period+1:i+1])**2)
    avg_ref2 = np.average(np.array(ref[i-period+1:i+1])**2)
    if np.isnan(avg_sig2) or np.isnan(avg_ref2):
        return np.nan
    sig_new = sig[i]/np.sqrt(avg_sig2)*np.sqrt(avg_ref2)
    return sig_new

def DISTRIBUTELINE_init(now_line):
    return {'value':now_line, 'speed':0, 'itr':0}

def DISTRIBUTELINE_live(self, i, memory, line, period, unitX, unitY):
    if i < period or np.isnan(period):
        return np.nan
    if memory['itr'] % period == 0:
        speed = myind.speed_live(line, period, i, unitX, unitY)
        speed = speed if not np.isnan(speed) else 0
        memory['speed'] = speed
        #memory['value'] = line[i]
    memory['value'] += memory['speed']
    memory['itr'] += 1
    return memory['value']

def band_pol_live(self, i, high, low, targetLine):
    gap = high[i] - low[i]
    center = (high[i] + low[i])/2
    diff = targetLine[i] - center
    pol = 2*diff/gap
    return pol

def angle_live(self, i, line, period, unitX, unitY):
    ''' calculate the angle of line between period as 'unitX'/'unitY' is π/4. '''
    if i < period or np.isnan(line[i]) or np.isnan(line[i-1]):
        return np.nan
    period = int(period)
    y = (line[i] - line[i-period])/unitY
    x = period/unitX
    angle = np.arctan2(y,x)
    return angle/(2*np.pi)*360.

#line = [float(100.00),100.2,float(100.80),100.6,100.8]
#print(angle_live(i=2,line=line,period=2,unitX=4,unitY=0.8))

def adjust_std_live(self, i, sig, ref, period):
    if i < period or np.isnan(period):
        return np.nan
    comment='''
    np_sig = np.array(sig[i-period+1:i+1])
    std_ref = np.std(ref[i-period+1:i+1])**2
    avg_sig = np.average(np_sig)
    sum_sig = np.sum(np_sig)
    s = sum_sig2 = np.sum(np_sig**2)
    sum_avg2_sig = np.sum(avg_sig**2)
    t = -2.0*avg_sig*sum_sig
    u = sum_avg2_sig-period*std_ref
    root = t**2 - 4.0*s*u
    if np.isnan(s) or np.isnan(t) or np.isnan(u) or root < 0:
        return np.nan
    mother = -t+np.sqrt(root)
    mother = mother if mother > 0 else -mother
    child = 4*s
    kai = mother/child
    return sig[i]*kai
    '''
    std_ref = np.std(ref[i-period+1:i+1])
    std_sig = np.std(sig[i-period+1:i+1])
    alpha = np.sqrt(std_ref/std_sig)
    return sig[i]*alpha

def shift_angle_live(self, i, line, angle, period, unitX, unitY):
    if i < period or np.isnan(period):
        return np.nan
    if isinstance(angle, Indicator):
        angle = angle[i]
    now_angle = angle_live(self, i, line, period, unitX, unitY)
    return period*unitY*np.tan((now_angle+angle)/360.0*2*np.pi)/unitX+line[i-period]

def change_angle_live(self, i, line, angle, period, unitX, unitY):
    if i < period or np.isnan(period):
        return np.nan
    if isinstance(angle, Indicator):
        angle = angle[i]
    return period*unitY*np.tan(now_angle/360.0*2*np.pi)/unitX+line[i-period]

def gravity_average(self, i, line, period):
    if np.isnan(i) or i < period:
        return np.nan
    d = line[i]-line[i-period]
    p = period
    g = d/p
    return g

def gravity_field(self, i, updown, line, period):
    if np.isnan(i) or i < period:
        return np.nan
    g = gravity_average(self, i, line, period)
    s = []
    for j in range(period):
        x = 1
        y = line[i-period-j]-line[i-period-j-1]# + g
        s.append(y/x)
    if s == [] or np.nan in s:
        return 0
    s_np = np.array(s)
    s_np = s_np[s_np*updown > 0]
    s_np = s_np * np.arange(len(s_np))
    ret = np.abs(np.sum(s_np)/np.sum(np.arange(len(s_np))))
    if np.isnan(ret):
        return 0
    return ret

def gravity_up(self, i, line, period):
    return gravity_field(self, i, +1, line, period)

def gravity_down(self, i, line, period):
    return gravity_field(self, i, -1, line, period)

def difflog_std_live(self, i, line, period):
    if np.isnan(i) or i < period:
        return np.nan
    diff= [0]*(period-1)
    for j in range(period-1):
        diff[j] = np.log(line[i-period+j+1]/line[i-period+j])
    sgm = np.std(diff)
    return np.exp(sgm)


def wt_coef_func(l,n=None):
    len_ = len(l)
    if n is None:
        n = len_/4
    new_l = np.array([x if i<len_/n else 0 for i,x in enumerate(l)])
    return new_l

def WNC_live(self, i, line, period, wavelet_type='coif2', coef_func=wt_coef_func, **funcargs): #wavelet noise cancelling
    if i < period:
        return np.nan
    comment='''
    wt = pywt.wavedecn(line[i-period+1:i+1], wavelet_type)
    l_,s_ = pywt.coeffs_to_array(wt)
    l_ = coef_func(l_, **funcargs)S
    rewt = pywt.array_to_coeffs(l_,s_)
    reline = pywt.waverecn(rewt,wavelet_type)
    return reline[-1]
    '''
    ca, cd = pywt.dwt(line[i-period+1:i+1], wavelet_type)
    ca = pywt.threshold(ca, np.std(ca)/2)
    cd = pywt.threshold(cd, np.std(cd)/2)
    reline = pywt.idwt(ca, cd, wavelet_type)
    return reline[-1]

def WNC2_live(self,i,line,period,n_down_sample,max_process,first_wavelet_name,first_sgm_n,first_coef_m,wavelets_name,sgm_n,coef_m,smoothing=False,output_all=False):
    if i < period or i < n_down_sample:
        if output_all:
            return [np.nan]*period
        else:
            return np.nan
    if period < n_down_sample:
      period = n_down_sample
    w_line = line[i-period:i+1]
    between = int(len(w_line)/n_down_sample)
    tar_line = [w_line[-j] for j in range(between, n_down_sample*between+1, between)]
    tar_line = tar_line[::-1]
    len_ = len(tar_line)
    if first_wavelet_name is not None:
      sub_line = calc_wavelet_th(tar_line,[first_wavelet_name],0,1,[first_sgm_n],[first_coef_m],False)
    else:
      sub_line = [0]*len_
    ana_line = list(np.array(tar_line)-np.array(sub_line))
#    plt.plot(np.arange(len_),tar_line);plt.plot(np.arange(len_),sub_line);plt.plot(np.arange(len_),ana_line);plt.show()
    reline = calc_wavelet_th(ana_line,wavelets_name,0,max_process,sgm_n,coef_m,smoothing)
    reline = list(np.array(reline)+np.array(sub_line))
#    plt.plot(np.arange(len_),reline,np.arange(len_),tar_line);plt.hlines([highs,lows],0,len_);plt.show();
    res = reline[-1]
    if output_all==True:
        res = reline
    return res
def calc_wavelet_th(line, wavelet_name, count_process, max_process, sgm_n, coef_m ,smoothing):
    len_line = len(line)
    rep_line = line[::-1]+line[::]+line[::-1]
    coeffs = pywt.wavedecn(rep_line, wavelet_name[count_process])
    list_, sep_ = pywt.coeffs_to_array(coeffs)
    m_max = int(np.log2(len(list_)))   ### m(frequency) filter ###
    for m in range(1,m_max+1):
        for n in range(2**(m_max-m),2**(m_max-m)*2):
            if m > m_max*coef_m[count_process] and n != 0:
                list_[n] = 0
    lambda_ = np.sqrt(2.0*np.log(len(rep_line)))*sgm_n[count_process]  ### n(location) filter ##
#    plt.plot(np.arange(len(list_)),list_);plt.hlines(lambda_,xmin=0,xmax=len(list_));
    list_ = [x if (i<len(list_)*0.01 or np.abs(x)>lambda_) else 0 for i,x in enumerate(list_)]
#    plt.plot(np.arange(len(list_)),list_);plt.hlines(-lambda_,xmin=0,xmax=len(list_));plt.show();
    coeffs = pywt.array_to_coeffs(list_, sep_)
    reline = pywt.waverecn(coeffs, wavelet_name[count_process])
#    plt.plot(np.arange(len(reline)),reline);plt.plot(np.arange(len(rep_line)),rep_line);plt.show();
    if count_process != max_process-1:
        res = calc_wavelet_th(list(reline[len_line:len_line*2]),wavelet_name,count_process+1,max_process,sgm_n,coef_m,smoothing)
    else:
        if smoothing:
            res = calc_wavelet_smooth(list(reline[len_line:len_line*2]),'Haar',3)
        else:
            res = list(reline[len_line:len_line*2])
    return res
def calc_wavelet_smooth(line, wavelet_name, level):
    rep_line = line[::-1]+line[::]+line[::-1]+line[::]
    N = len(rep_line)
    coeffs = pywt.wavedecn(rep_line, wavelet_name, level=level)
    list_, sep_ = pywt.coeffs_to_array(coeffs)
    level = level if level is not None else int(np.log2(N))
    list_ = [x if i < N/2**level else 0 for i,x in enumerate(list_)]
    coeffs = pywt.array_to_coeffs(list_, sep_)
    smooth = pywt.waverecn(coeffs, wavelet_name)
#    plt.plot(np.arange(N),smooth,np.arange(N),rep_line);plt.show();
    len_line = len(line)
    return list(smooth[len_line:len_line*2])
def highslows_live(self, i, line, period_target, margin_target, highlow_symbol, memory, period_memory):
        if i < period_memory or i < period_target:
            memory.append(np.nan)
            return np.nan
        if highlow_symbol == 'highs':
            highlow = 1
            func = np.nanmax
        elif highlow_symbol == 'lows':
            highlow = -1
            func = np.nanmin
        else:
            return np.nan
        tar_line = line[len(line)-period_target:]
        diff = np.array([(tar_line[j]-tar_line[j-1]) if j < len(tar_line)-margin_target else np.nan for j in range(len(tar_line))])
    #    ax1.cla();ax1.plot(np.arange(len(tar_line)),tar_line);ax2.cla();ax2.plot(np.arange(len(diff)),diff);plt.pause(.01);
        buf = []
        for j in range(1,len(diff)):
            if diff[j-1]*highlow >= 0 and diff[j]*highlow < 0:
                buf.append(tar_line[j])
        buf = list(pd.Series(buf).dropna())
        if buf == []:
            memory.append(np.nan)
        else:
            memory.append(func(buf))
        m = list(pd.Series(memory[i-period_memory:i+1]).dropna())
        if buf == [] and m == []:
            v = self.newest()
        else:
            v = func(buf+m)
        return v
def WT_SMOOTH_live(self, i, line, period, wavelet_name, level=None):
    if i < period:
        return np.nan
    wline = line[i-period:i+1]
    smooth = calc_wavelet_smooth(wline, wavelet_name, level)
    return smooth[-1]
def calc_wavelet_smooth(line, wavelet_name, level=None):
    rep_line = line[::-1]+line[::]+line[::-1]+line[::]
    N = len(rep_line)
    coeffs = pywt.wavedecn(rep_line, wavelet_name, level=level)
    list_, sep_ = pywt.coeffs_to_array(coeffs)
    level = level if level is not None else int(np.log2(N))
    list_ = [x if j < N/2**level else 0 for j,x in enumerate(list_)]
    coeffs = pywt.array_to_coeffs(list_, sep_)
    smooth = pywt.waverecn(coeffs, wavelet_name)
#    plt.plot(np.arange(N),smooth,np.arange(N),rep_line);plt.title('name:{}, level:{}'.format(wavelet_name,level));plt.show();
    len_line = len(line)
    return list(smooth[len_line:len_line*2])

def MTF_MA_live(self, i, line, period, tf): #tf:time frame
    if i < period:
        return np.nan
    shift = i % tf
    conv_line = line[i-shift-period:i-shift+1:tf] # get close value by time frame
    return np.average(conv_line)

def MA_FORCE_live(self, i, ma_speed, period, coef=2):
    if i < period:
        return np.nan
    return np.sqrt(np.abs(ma_speed*period**coef))*ma_speed/np.abs(ma_speed)
