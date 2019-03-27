import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

POS_LONG   = +1
POS_SHORT  = -1
ORD_ENTRY  = +1
ORD_EXIT   = -1
DT_NORMAL  = 0
DT_LOSSCUT = -1
DT_GETPROF = +1
DT_ILLEGAL = -2

headerList = ('id',)
entryList = ('pair','posType','lot',
            'entry_time','entry_rate',
            'get_prof', 'loss_cut',)
exitList  = ('exit_time','exit_rate','dec_type',
            'swap','spread',)
extraList = ('profit','time_diff',)

def init(col=[*headerList,*entryList,*exitList,*extraList]):
    return {k:[] for k in col}

def issueTicket(history):
    _id = len(history['id'])
    for k in history:
        history[k].append(np.nan)
    history['id'][_id] = _id
    return _id

def issueOrder(_type, _id):
    d = {}
    if _type == ORD_ENTRY:
        d['arg'] = {k:np.nan for k in entryList}
        d['arg']['_id'] = _id
        d['type'] = _type
    elif _type == ORD_EXIT:
        d['arg'] = {k:np.nan for k in exitList}
        d['arg']['_id'] = _id
        d['type'] = _type
    return d

def entry(history, _id, pair, posType, lot, entry_time, entry_rate, get_prof=np.nan, loss_cut=np.nan):
    history['pair'][_id] = pair
    history['posType'][_id] = posType
    history['lot'][_id] = lot
    history['entry_time'][_id] = entry_time
    history['entry_rate'][_id] = entry_rate
    history['get_prof'][_id] = get_prof
    history['loss_cut'][_id] = loss_cut
    return None

def edit(history, _id, pair=np.nan, posType=np.nan, lot=np.nan, entry_time=np.nan, entry_rate=np.nan, get_prof=np.nan, loss_cut=np.nan):
    return entry(history, _id, history['pair'][_id]       if np.isnan(pair)       else pair,
                               history['posType'][_id]    if np.isnan(posType)    else posType,
                               history['lot'][_id]        if np.isnan(lot)        else lot,
                               history['entry_time'][_id] if np.isnan(entry_time) else entry_time,
                               history['entry_rate'][_id] if np.isnan(entry_rate) else entry_rate,
                               history['get_prof'][_id]   if np.isnan(get_prof)   else get_prof,
                               history['loss_cut'][_id]   if np.isnan(loss_cut)   else loss_cut)

def profit(history, _id, now_rate): # except commission
    return (now_rate-history['entry_rate'][_id])*history['posType'][_id]*history['lot'][_id]

def exit(history, _id, exit_time, exit_rate, spread, dec_type=DT_NORMAL, swap=0):
    history['exit_time'][_id] = exit_time
    history['exit_rate'][_id] = exit_rate
    history['dec_type'][_id]  = dec_type
    history['swap'][_id]      = swap
    history['spread'][_id]    = spread
    history['profit'][_id]    = profit(history, _id, exit_rate) - spread
    history['time_diff'][_id] = history['exit_time'][_id]-history['entry_time'][_id]
    return None

def collectTicket():
    return np.nan

def collectOrder():
    return None

def drawdown(pd_prof):
    _max = _min = dd = 0
    for p in pd_prof.values:
        if p > _max:
            _max = _min = p
        elif p < _min:
            _min = p
        if (_max-_min) > dd:
            dd = (_max-_min)
    return dd

def arrange_history(history):
    point_history = len(history['id'])
    prof         = [np.nan]*point_history
    prof_time    = [np.nan]*point_history
    tran = {'long'         :[np.nan]*point_history,
            'short'        :[np.nan]*point_history,
            'settle_long'  :[np.nan]*point_history,
            'settle_short' :[np.nan]*point_history,
            'losscut'      :[np.nan]*point_history}
    tran_time = {'long'         :[np.nan]*point_history,
                 'short'        :[np.nan]*point_history,
                 'settle_long'  :[np.nan]*point_history,
                 'settle_short' :[np.nan]*point_history,
                 'losscut'      :[np.nan]*point_history}
    line = {'long'   :[],
            'short'  :[]}
    line_time = {'long'   :[],
                 'short'  :[]}
    plus = minus = 0
    for _id in range(point_history):
        if history['posType'][_id] == POS_LONG:
            tran     ['long'][_id] = history['entry_rate'][_id]
            tran_time['long'][_id] = history['entry_time'][_id]
            line     ['long'].append(history['entry_rate'][_id])
            line_time['long'].append(history['entry_time'][_id])
            line     ['long'].append(history['exit_rate'][_id])
            line_time['long'].append(history['exit_time'][_id])
            line     ['long'].append(np.nan)
            line_time['long'].append(history['exit_time'][_id])
            if history['dec_type'][_id] == DT_LOSSCUT:
                tran     ['losscut'][_id] = history['exit_rate'][_id]
                tran_time['losscut'][_id] = history['exit_time'][_id]
            else:
                tran     ['settle_long'][_id] = history['exit_rate'][_id]
                tran_time['settle_long'][_id] = history['exit_time'][_id]
        elif history['posType'][_id] == POS_SHORT:
            tran     ['short'][_id] = history['entry_rate'][_id]
            tran_time['short'][_id] = history['entry_time'][_id]
            line     ['short'].append(history['entry_rate'][_id])
            line_time['short'].append(history['entry_time'][_id])
            line     ['short'].append(history['exit_rate'][_id])
            line_time['short'].append(history['exit_time'][_id])
            line     ['short'].append(np.nan)
            line_time['short'].append(history['exit_time'][_id])
            if history['dec_type'][_id] == DT_LOSSCUT:
                tran     ['losscut'][_id] = history['exit_rate'][_id]
                tran_time['losscut'][_id] = history['exit_time'][_id]
            else:
                tran     ['settle_short'][_id] = history['exit_rate'][_id]
                tran_time['settle_short'][_id] = history['exit_time'][_id]
        else:
            continue
        prof[_id]      = history['profit'][_id]
        prof_time[_id] = history['exit_time'][_id]

    col = ('long', 'short', 'settle_long', 'settle_short', 'losscut')
    tranMarker = pd.DataFrame({},index=[])
    for c in col:
        pd_index = pd.Series(tran_time[c]).dropna().values
        dna = (pd.Series(tran[c]).dropna()).values
        df = pd.DataFrame({c:dna}, index=pd_index)
        tranMarker = tranMarker.join(df, how='outer')

    tranLine = {}
    tranLine['long']  = pd.DataFrame({'long':line['long']},index=line_time['long'])
    tranLine['short'] = pd.DataFrame({'short':line['short']},index=line_time['short'])

    index_prof_time = pd.Series(prof_time).dropna().values
    pd_prof = pd.Series((pd.Series(prof).dropna()).values, index=index_prof_time).sort_index()
    np_accum = np.zeros(len(pd_prof))
    for i, p in enumerate(pd_prof.values):
        np_accum[i] = np_accum[i-1] + p
    accum = pd.Series(np_accum, index=pd_prof.index)

    arange_dic = {}
    arange_dic['drawdown'] = drawdown(pd_prof)
    np_tmp = np.array(history['profit'])
    arange_dic['profit_max'] = max(np_tmp)
    arange_dic['loss_max']   = min(np_tmp)
    arange_dic['win_count']  = len(np_tmp[np_tmp > 0])
    arange_dic['lose_count'] = len(np_tmp[np_tmp < 0])
    arange_dic['plus_sum']   = sum(np_tmp[np_tmp > 0])
    arange_dic['minus_sum']  = sum(np_tmp[np_tmp < 0])
    arange_dic['pf']         = arange_dic['plus_sum']/np.abs(arange_dic['minus_sum'])
    np_tmp = np.array(history['lot'])
    arange_dic['lot_max']    = max(np_tmp)
    np_tmp = np.array(history['dec_type'])
    arange_dic['losscut_count'] = len(np_tmp[np_tmp == DT_LOSSCUT])

    return tranMarker, tranLine, accum, arange_dic

def adjust_sum(sum_s, spec):
    sum_value = []
    j = 0
    v = sum_s[0]
    for i in range(len(spec)):
        if spec.index[i] == sum_s.index[j]:
            v = sum_s[j]
            j +=1
            if j >= len(sum_s):
                j -= 1
        sum_value.append(v)
    new_df_sum = pd.Series(sum_value,index=spec.index)
    return new_df_sum


def isReservedExit(now_rate, pos, _id, tranHis):
    g = isGettingProfit(now_rate, pos, _id, tranHis)
    c = isCuttingLoss(now_rate, pos, _id, tranHis)
    if g == DT_GETPROF and c is None:
        return DT_GETPROF
    elif c == DT_LOSSCUT and g is None:
        return DT_LOSSCUT
    elif g is None and c is None:
        return None
    raise ValueError('Illegal value @isReservedExit')

def isGettingProfit(now_rate, pos, _id, tranHis):
    if now_rate*pos > tranHis['get_prof'][_id]*pos:
        return DT_GETPROF
    return None

def isCuttingLoss(now_rate, pos, _id, tranHis):
    if now_rate*pos < tranHis['loss_cut'][_id]*pos:
        return DT_LOSSCUT
    return None

def isExist(obj):
    if obj is None:
        return False
    if np.isnan(obj):
        return False
    return True

def get_dec_type(tranHis, _id):
    if np.isnan(_id):
        return np.nan
    return tranHis['dec_type'][_id]
