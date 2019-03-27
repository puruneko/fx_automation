
from collections import OrderedDict, deque
import numpy as np
import pandas as pd
import types


class FXIndicators():

    max_buffer = 1000 # 1000 is temporal number
    timeSeries = None
    name_rate = 'Rate'
    name_ohlc = ('Open','High','Low','Close')
    name_repr = 'Close'

    def __init__(self, prop=None):
        self.indicators = OrderedDict()
        # set Rate, Open, High, Low, Close
        self.add_indicator(FXIndicators.name_rate)
        for name in FXIndicators.name_ohlc:
            self.indicators[name] = FXIndicator()
        # set propaties
        self.parse_propaties(prop)
        # set buffer
        FXIndicators.max_buffer = FXIndicators.max_buffer
        FXIndicators.timeSeries = deque([],FXIndicators.max_buffer)

    def __getitem__(self, name):
        return self.indicators[name]

    def set_buffer_size(self, size_):
        FXIndicators.max_buffer = size_

    def get_timeSeries(self):
        return list(FXIndicators.timeSeries)

    def newest_time(self):
        return FXIndicators.timeSeries[-1]

    def add_indicator(self, name, **kwargs):
        indicator = FXIndicator(**kwargs)
        self.set_indicator(name, indicator)
    
    def set_indicator(self, name, indicator):
        self.indicators[name] = indicator
    
    def time_to_index(self, time):
        return np.min(np.where(np.array(FXIndicators.timeSeries)>=time))

    def update_rate(self, newest_ohlc):
        ohlc = [newest_ohlc[name] for name in FXIndicators.name_ohlc]
        self.indicators[FXIndicators.name_rate].append(ohlc)
        for name in FXIndicators.name_ohlc:
            self.indicators[name].append(newest_ohlc[name])
        if len(self.indicators[FXIndicators.name_rate]) > FXIndicators.max_buffer:
            self.indicators[FXIndicators.name_rate].shift()
        if len(self.indicators[FXIndicators.name_repr]) > FXIndicators.max_buffer:
            self.indicators[FXIndicators.name_repr].shift()

    def update_indicator(self, i):
        for name in self.indicators:
            if name != FXIndicators.name_rate or not name in FXIndicators.name_ohlc:
                self.indicators[name].update(i)
    
    def update(self, t, ohlc):
        FXIndicators.timeSeries.append(t)
        if len(FXIndicators.timeSeries) >= FXIndicators.max_buffer:
            FXIndicators.timeSeries.popleft()
        self.update_rate(ohlc)
        i = self.time_to_index(t)
        self.update_indicator(i)

    def parse_propaties(self, prop_dict):
        # TODO:chart幅の倍数に書き直す->延期
        if prop_dict is not None:
            if 'buffer' in prop_dict:
                FXIndicators.max_buffer = int(prop_dict['buffer'])
            else:
                FXIndicators.max_buffer = 1000
            if 'member' in prop_dict:
                member = prop_dict['member']
                for iname in member:
                    func = FXIndicatorFunction.PASS_live
                    if 'func' in member[iname]:
                        func = eval('FXIndicatorFunction.'+member[iname]['func'])
                    kwargs = {'func':func}
                    for arg in member[iname]:
                        if arg == 'func':
                            continue
                        if type(arg) == dict:
                            for k,v in arg.items():
                                if k == '$ind':
                                    kwargs[arg] = self.indicators[v].newest
                                else:
                                    kwargs[arg] = {k:v}
                        else:
                            kwargs[arg] = member[iname][arg]
                    self.add_indicator(iname, **kwargs)


class FXIndicator():

    def __init__(self, default=None, func=None, forTransactionMarker=False, update_flag=True, scalar=False, **kwargs_for_func):
        self._value = deque([],FXIndicators.max_buffer)
        if default is not None:
            self._value.append(default)
        self.append_value = self._value.append
        self.shift_value = self._value.popleft
        self._set_update_function(func)
        self.kwargs_for_func = kwargs_for_func
        self.update_flag = update_flag
        self.scalar = scalar

    def __len__(self):
        return len(self._value)

    def __contains__(self, x):
        return x in self._value

    def __getitem__(self, i):
        return list(self._value)[i]

    def _set_update_function(self, func):
        self.update_func = func
        
    def get_items(self):
        return {'x':list(FXIndicators.timeSeries),
                'y':list(self._value)}

    def newest(self):
        return self._value[-1]

    def get(self, i):
        return {'x':list(FXIndicators.timeSeries)[i],
                'y':self._value[i]}

    def set(self, i, value):
        self._value[i] = value

    def get_value(self, i):
        return self._value[i]

    def get_values(self):
        return list(self._value)

    def set_value(self, i, value):
        self._value[i] = value

    def append(self, v):
        self.append_value(v)

    def shift(self):
        self.shift_value()
    
    def time_to_index(self, time):
        return np.min(np.where(np.array(FXIndicators.timeSeries)>=time))

    def get_ylim(self, xlim=None):
        i0 = self.time_to_index(xlim[0]) if xlim is not None else 0
        i1 = self.time_to_index(xlim[1]) if xlim is not None else len(self._value)
        max_ = np.max(list(self._value)[i0:i1])
        min_ = np.min(list(self._value)[i0:i1])
        ylim = [min_, max_]
        print('@FXIndicator :i[{},{}] ylim{}'.format(i0,i1, ylim))
        return ylim

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
            # calculate update value.
            v = self.update_func(self, i, **kwargs)
            # update
            self.append(v)
            # If type of this Indicator is scalar,
            # all value is set NAN except the newest value.
            if self.scalar and i != 0:
                self._value[i-1] = np.nan
            # If values array length is longer than max_buffer,
            # execute shift(popleft).
            if len(self._value) >= FXIndicators.max_buffer:
                self.shift()
    
    def set_update_arguments(self, dict_):
        for k,v in dict_.items():
            self.set_update_argument(k,v)

    def set_update_argument(self, key, value):
        self.kwargs_for_func[key] = value


class FXIndicatorFunction():

    def PASS_live(self, i, line):
        return line[i]

    def MA_live(self, i, line, period):
        if i < period:
            return np.nan
        return np.average(line[i-period+1:i+1])

