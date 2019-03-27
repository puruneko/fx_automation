import sys
import numpy as np
import pandas as pd
import pandas.tseries.offsets as offsets
import matplotlib.pyplot as plt
import json
import requests

def resample_by_term(df, termSymbol):
    # resampling
    res = df.resample(termSymbol).ohlc()
    # cancel double array
    ret = pd.DataFrame({'Open':  res['open']['open'],
                        'High':  res['high']['high'],
                        'Low':   res['low']['low'],
                        'Close': res['close']['close']},
                        columns= ['open','high','low','close'])
    # drop out NaN
    ret = ret.dropna()
    return ret

def subdivide_second(ohlc_minuts, coef=1):
    if coef == 1:
        return ohlc_minuts['close']

    point = len(ohlc_minuts)
    ohlc_quarter = np.zeros(point*coef)
    ohlc_quarter_index = [0 for i in range(point*coef)]
    ohlc = (ohlc_minuts['open'].as_matrix(),
            ohlc_minuts['high'].as_matrix(),
            ohlc_minuts['low'].as_matrix(),
            ohlc_minuts['close'].as_matrix())
    itr_p = (0, 2, 1)
    itr_m = (0, 1, 2)
    offset = [offsets.Second(i*(60/coef)) for i in range(coef)]
    for i in range(point):
        itr = itr_p if ohlc[0][i]<ohlc[3][i] else itr_m
        for j in range(coef):
            ohlc_quarter[i*coef+j] = ohlc[itr[j]][i]
            ohlc_quarter_index[i*coef+j] = ohlc_minuts.index[i] + offset[j]
    return pd.Series(ohlc_quarter,index=ohlc_quarter_index)

def notification_slack(text, sendTo='main', username='jupyter', icon_emoj=':envelope:', channel='#jupyter_notebook', send=True):
    url_main = 'https://hooks.slack.com/services/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'
    url_sub =  'https://hooks.slack.com/services/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'
    url = url_sub if sendTo == 'sub' else url_main
    payload_dic = {
    "text":text,
    "username":username,
    "icon_emoji":icon_emoj,
#    "channel":channel,
    }
    try:
        if send:
            r = requests.post(url, data=json.dumps(payload_dic))
    except:
        print('failed: notification_slack')
    print(text)
