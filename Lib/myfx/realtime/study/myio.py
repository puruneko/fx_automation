import sys
import numpy as np
import pandas as pd
import pandas.tseries.offsets as offsets
import matplotlib.pyplot as plt
import json
import requests

class HistoricalData():

    candle_header = ('open','high','low','close')
    csv_header = ('Time', *candle_header, 'volume')

    def __init__(self, read_dir, candle_per_minute=6, split_pair=None, split_year=None, split_month=None):
        self.read_dir = read_dir
        self.candle_per_minute = candle_per_minute
        split_pair = split_pair if split_pair is not None else self._default_split_of_pair
        split_year = split_year if split_year is not None else self._default_split_of_year
        split_month = split_month if split_month is not None else self._default_split_of_month
        self.pair = split_pair(read_dir)
        self.year = split_year(read_dir)
        self.month = split_month(read_dir)
        self.historical_data = None

    def __getitem__(self, index):
        return self.historical_data[index]

    def __len__(self):
        return len(self.historical_data)

    def read(self, start_date=None, end_date=None,
                    time_offset=7, ohlc='c', **kwargs):
        self.historical_data = pd.read_csv(self.read_dir, **kwargs)
        self.historical_data.index += offsets.Hour(time_offset)
        start_date = start_date if start_date is not None else 0
        end_date = end_date if end_date is not None else -1
        self.historical_data = self.historical_data[start_date:end_date]
        if ohlc != 'olhc':
            if ohlc == 'o':
                self.historical_data = self.historical_data['open']
            elif ohlc == 'h':
                self.historical_data = self.historical_data['high']
            elif ohlc == 'l':
                self.historical_data = self.historical_data['low']
            elif ohlc == 'c':
                self.historical_data = self.historical_data['close']
        self.index = self.historical_data.index
        self.ohlc = ohlc

    def as_matrix(self):
        return self.historical_data.as_matrix()

    def resample_by_term(self, termSymbol):
        # resampling
        self.historical_data = self.historical_data.resample(termSymbol).ohlc()
        # cancel double array
        self.historical_data = pd.DataFrame({'Open':  res['open']['open'],
                                             'High':  res['high']['high'],
                                             'Low':   res['low']['low'],
                                             'Close': res['close']['close']},
                                             columns= [*HistoricalData.candle_header])
        # drop out NaN
        self.historical_data = self.historical_data.dropna()

    def subdivide_second(self, coef=1):
        if coef == 1:
            return self.historical_data['close']

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
                ohlc_quarter_index[i*coef+j] = self.historical_data.index[i] + offset[j]
        self.historical_data = pd.Series(ohlc_quarter,index=ohlc_quarter_index)

    def _default_split_of_pair(self, str_):
        return str_.split('\\')[-1].split('_')[0]

    def _default_split_of_year(self, str_):
        return str_.split('\\')[-1].split('_')[3].split('.')[0]

    def _default_split_of_month(self, str_):
        return str_.split('\\')[-1].split('_')[3].split('.')[1]

class ExcelParameterBook():

    def __init__(self, path, dic_sep='.', name='name', value='value', coef='coef', option='option'):
        self.book = pd.ExcelFile(path)
        self.dic_sep = dic_sep
        self.name = name
        self.value = value
        self.coef = coef
        self.option = option
        self.coefs = {}

    def resister_coef(self, key, value):
        self.coefs[key] = value

    def parse(self):
        param = {}
        for sht in self.book.sheet_names:
            sheet = self.book.parse(sht)
            param[sht] = {}
            for nm in sheet.name:
                now = param[sht]
                nmsplit = nm.split(self.dic_sep)
                len_ = len(nmsplit)
                splt = None
                for i, splt in enumerate(nmsplit):
                    if not splt in now:
                        now[splt] = {}
                    if i != len_-1:
                        now = now[splt]
                v = sheet[sheet[self.name]==nm][self.value].values[0]
                c = sheet[sheet[self.name]==nm][self.coef].values[0]
                if c is None or (type(c) != str and np.isnan(c)):
                    c = 1
                elif type(c) == str:
                    c = self.coefs[c]
                now[splt] = v*c
        return param

class Notification():
    ''' notification '''

    slack_url_main = 'https://hooks.slack.com/services/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'
    slack_url_sub =  'https://hooks.slack.com/services/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'

    def __init__(self, switch=True, output=True):
        self.switch = switch
        self.output = output

    def slack(self, text, sendTo='main', username='jupyter', icon_emoj=':envelope:',
                    channel='#jupyter_notebook'):
        if self.switch:
            url = Notification.slack_url_sub if sendTo == 'sub'\
                                            else Notification.slack_url_main
            payload_dic = {
            "text":text,
            "username":username,
            "icon_emoji":icon_emoj,
        #    "channel":channel,
            }
            try:
                r = requests.post(url, data=json.dumps(payload_dic))
            except:
                print('failed: notification_slack')
            if self.output:
                print(text)
