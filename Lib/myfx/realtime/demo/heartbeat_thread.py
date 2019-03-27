import myenvironment
import sys
sys.path.append(myenvironment.path)
import traceback

import queue
import threading as th
import numpy as np
import pandas as pd
import time
from collections import deque
import pandas.tseries.offsets as offsets
import json
import requests

import oandapyV20
import oandapyV20.endpoints.pricing as pricing
from coincheck import market as coincheck_market
from pubnub.callbacks import SubscribeCallback
from pubnub.enums import PNStatusCategory
from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub_tornado import PubNubTornado
from pubnub.pnconfiguration import PNReconnectionPolicy
from tornado import gen

import  myfx.realtime.demo.event_thread as event_thread

class HeartbeatThread():

    def __init__(self, fxevents, com_type, instruments, heartbeat, **kwargs):
        self.fxevents = fxevents
        self.com_type = com_type
        self.heartbeat = heartbeat
        self.server = None
        tick_interval = heartbeat*0.1
        if com_type=='FX_Real':
            pass
        elif com_type=='FX_Demo':
            ACCOUNT_ID = '101-001-6187232-001'
            ACCESS_TOKEN = '451faa1c762459cae6c1dcd3d46d673d-78b5fcfbee57f4ad6846c325d9d69cb4'
            self.server = OANDATickServer(fxevents, tick_interval, ACCESS_TOKEN, ACCOUNT_ID, instruments)
        elif com_type=='FX_Study':
            self.server = PseudoTickServer(fxevents, tick_interval)
        elif com_type=='bitcoin':
            self.server = BitcoinTickServer(fxeventstick_interval)
        elif com_type=='offline':
            self.server = OfflineServer(fxevents, tick_interval, **kwargs)
        else:
            raise Exception
        self.run = True
    
    def start(self):
        self.th_ = th.Thread(target=self.thread, args=[])
        self.th_.start()

    def thread(self):
        print('heartbeat thread start!')
        th_server = th.Thread(target=self.server.thread, args=[])
        th_server.start()
        self.ohlc = {}
        try:
            while self.run:
                time.sleep(self.heartbeat)
                ticks = []
                while ticks==[]:
                    ticks = self.server.get_ticks()
                time_ = time.time()
                heartbeat_res = []
                self.ohlc = {}
                if ticks != []:
                    self.ohlc['High']  = float(np.max(ticks))
                    self.ohlc['Low']   = float(np.min(ticks))
                    if not 'Close' in self.ohlc:
                        self.ohlc['Close'] = (self.ohlc['High']+self.ohlc['Low'])/2
                    self.ohlc['Open']  = self.ohlc['Close']
                    self.ohlc['Close'] = ticks[-1]
                    heartbeat_res = [time_, self.ohlc]
                #print('heartbeat reaponse:{}'.format(heartbeat_res))
                if heartbeat_res != []:
                    self.fxevents.put(event_thread.EventContainer(name='tick',value=heartbeat_res))
        except:
            print('@HeartbeatThread : exception raised.')
            traceback.print_exc()
            self.fxevents.put(event_thread.EventContainer(name='exception', value=[]))
        print('** heartbeat thread finished!')
    
    def thread_close(self):
        print('stop')
        self.run = False
        self.server.thread_close()
            

class PseudoTickServer():

    def __init__(self, fxevents, tick_interval):
        self.fxevents = fxevents
        self.tick_interval = tick_interval
        self.ticks = []
        self.time = 0
        self.run = True
    
    def get_ticks(self):
        ticks = [x for x in self.ticks]
        self.ticks = []
        return ticks

    def get_time(self):
        return self.time
    
    def thread(self):
        '''
        return 1minute tick OHLC value
        '''
        print('pseudoserver thread start!')
        randn = 1000
        i = randn
        randomwalk = None
        try:
            while self.run:
                time.sleep(self.tick_interval)
                if i >= randn:
                    randomwalk = self.get_randomwalk(randn)
                    i = 0
                self.ticks.append(randomwalk[i])
                self.time += self.tick_interval
                i += 1
        except:
            print('@pseudoTickServerThread : exception raised.')
            traceback.print_exc()
            self.fxevents.put(event_thread.EventContainer(name='exception', value=[]))
        print('** pseudoserver thread finished!')
    
    def thread_close(self):
        self.run = False
    
    def get_randomwalk(self, size, intercept=100):
        random = np.random.choice([-0.005,0.005], size=size)
        return np.cumsum(random)+intercept


class OANDATickServer():

    def __init__(self, fxevents, tick_interval, access_token, account_id, instruments):
        self.fxevents = fxevents
        self.tick_interval = tick_interval
        self.access_token = access_token
        self.account_id = account_id
        self.instruments = instruments
        self.ticks = []
        self.time = 0
        self.myevent = th.Event()
        self.run = True
    
    def get_ticks(self):
        self.stop()
        ticks = [x for x in self.ticks]
        self.ticks = []
        self.start()
        return ticks

    def get_time(self):
        return self.time

    def thread(self):
        client = None
        req = None
        try:
            client = oandapyV20.API(access_token=self.access_token)
            params = {'instruments':self.instruments}
            req = pricing.PricingInfo(accountID=self.account_id, params=params)
        except Exception as e:
            errmsg = 'Caught exception when connecting to stream\n' + str(e)
            req.terminate(errmsg)

        res = client.request(req)
        self.start()
        try:
            while self.run:
                self.wait_until_start_is_called()
                time.sleep(self.tick_interval)
                res = client.request(req)
                tick = res['prices'][0]
                instrument = tick['instrument']
                self.time = pd.DatetimeIndex([pd.Timestamp(tick['time'])]).astype(np.int64)[0]//10**9
                bid  = float(tick['bids'][0]['price'])
                ask  = float(tick['asks'][0]['price'])
                print('tickServer response:{}'.format(bid))
                self.ticks.append(bid)
        except:
            print('@OANDATickServerThread : exception raised.')
            traceback.print_exc()
            self.fxevents.put(event_thread.EventContainer(name='exception', value=[]))
    
    def thread_close(self):
        self.run = False

    def wait_until_start_is_called(self):
        self.myevent.wait()
    
    def stop(self):
        self.myevent.clear()
    
    def start(self):
        self.myevent.set()


class BitcoinTickServer():

    def __init__(self, fxevents, tick_interval):
        self.fxevents = fxevents
        self.tick_interval = tick_interval
        self.instruments = 'lightning_ticker_BTC_JPY'
        config = PNConfiguration()
        config.subscribe_key = 'sub-c-52a9ab50-291b-11e5-baaa-0619f8945a4f'
        config.reconnect_policy = PNReconnectionPolicy.LINEAR
        self.pubnub = PubNubTornado(config)
        self.run = True
    
    def get_ticks(self):
        ticks = self.listener.get_ticks()
        return ticks
    
    def get_time(self):
        time = self.listener.get_time()
        return time
    
    @gen.coroutine
    def thread(self):
        self.listener = BitflyerSubscriberCallback(self.tick_interval)
        self.pubnub.add_listener(self.listener)
        self.pubnub.subscribe().channels(self.instruments).execute()
        self.pubnub.start()
        try:
            while self.run:
                self.do_unsubscribe()
        except:
            print('@BitcoinTickServerThread : exception raised.')
            traceback.print_exc()
            self.fxevents.put(event_thread.EventContainer(name='exception', value=[]))
    
    def thread_close(self):
        self.run = False
    
    def do_unsubscribe(self):
        if self.run==False:
            self.pubnub.unsubscribe({'channel': self.instruments})
            raise Exception

class BitflyerSubscriberCallback(SubscribeCallback):

    def __init__(self, tick_interval, *args, **kwargs):
        super(BitflyerSubscriberCallback, self).__init__(*args, **kwargs)
        self.tick_interval = tick_interval
        self.ticks = []
        self.time = 0
    
    def get_ticks(self):
        ticks = [x for x in self.ticks]
        self.ticks = []
        return ticks

    def get_time(self):
        return self.time

    def presence(self, pubnub, presence):
        pass  # handle incoming presence data

    def status(self, pubnub, status):
        if status.category == PNStatusCategory.PNUnexpectedDisconnectCategory:
            pass  # This event happens when radio / connectivity is lost

        elif status.category == PNStatusCategory.PNConnectedCategory:
            # Connect event. You can do stuff like publish, and know you'll get it.
            # Or just use the connected event to confirm you are subscribed for
            # UI / internal notifications, etc
            pass
        elif status.category == PNStatusCategory.PNReconnectedCategory:
            pass
            # Happens as part of our regular operation. This event happens when
            # radio / connectivity is lost, then regained.
        elif status.category == PNStatusCategory.PNDecryptionErrorCategory:
            pass
            # Handle message decryption error. Probably client configured to
            # encrypt messages and on live data feed it received plain text.

    def message(self, pubnub, message):
        # Handle new message stored in message.message
        # メインの処理はここで書きます
        # 登録したチャンネルからメッセージ(価格の変化など)がくるたび、この関数が呼ばれます
        time.sleep(tick_interval)
        res = message.message
        bid = res['best_bid']
        self.ticks.append(bid)
        self.time = pd.DatetimeIndex([pd.Timestamp(res['timestamp'])]).astype(np.int64)[0]//10**9


class OfflineServer():

    def __init__(self, fxevents, tick_interval, **kwargs):
        self.fxevents = fxevents
        self.tick_interval = tick_interval
        self.ticks = []
        self.time = 0
        self.dir = kwargs['dir'] if 'dir' in kwargs else r'C:\Users\Ryutaro\Dropbox\prog\git\github\project_fx\source\downloads'
        self.year = kwars['year'] if 'year' in kwargs else 2016
        self.range = kwargs['range'] if 'range' in kwargs else ['01-01 00:00:00', '12-31 00:00:00']
        self.instruments = kwargs['instruments'] if 'instruments' in kwargs else 'USDJPY'
        self.timeframe = kwargs['timeframe'] if 'timeframe' in kwargs else 'M1'
        timedelta = {'M1':pd.offsets.timedelta(seconds=60), 'S10':pd.offsets.timedelta(seconds=10)}
        self.timedelta = timedelta[self.timeframe]
        self.starttime = self.range[0]
        sp = {'M1':self.split_pair, 'S10':None}
        sy = {'M1':self.split_year, 'S10':None}
        sm = {'M1':self.split_month, 'S10':None}
        cpm = {'M1':1, 'S10':6}
        sep = {'M1':';', 'S10':','}
        csv_name = {}
        csv_name['M1']  = r'DAT_ASCII_'+self.instruments+r'_M1_' + str(self.year) + r'.csv'
        csv_name['S10'] = self.instruments+r'_10 Secs_Bid_'+str(self.year)+r'.01.01_'+str(self.year)+r'.12.31.csv'
        read_dir = self.dir + '\\' + str(csv_name[self.timeframe])
        self.hd = HistoricalData(read_dir, candle_per_minute=cpm[self.timeframe],
                                           split_pair=sp[self.timeframe],
                                           split_year=sy[self.timeframe],
                                           split_month=sm[self.timeframe])
        _start_date = self.hd.year+'-'+ self.range[0]
        _end_date =   self.hd.year+'-'+ self.range[1]
        self.hd.read(start_date=_start_date, end_date=_end_date,
                     ohlc='ohlc', sep=sep[self.timeframe], skiprows=1,
                     names=HistoricalData.csv_header, index_col='Time', parse_dates=True)
        self.run = True
    
    def get_ticks(self):
        ticks = [x for x in self.ticks]
        self.ticks = []
        return ticks
    
    def get_time(self):
        return self.time
    
    def thread(self):
        try:
            for t in self.hd.index:
                if self.ticks == []:
                    ohlc = self.hd[str(t)]
                    self.ticks.append(ohlc['open'])
                    self.ticks.append(ohlc['high'])
                    self.ticks.append(ohlc['low'])
                    self.ticks.append(ohlc['close'])
                    self.time = pd.DatetimeIndex([pd.Timestamp(t)]).astype(np.int64)[0]//10**9
                while self.ticks != []:
                    pass
        except:
            print('@OfflineTickServerThread : exception raised.')
            traceback.print_exc()
            self.fxevents.put(event_thread.EventContainer(name='exception', value=[]))
    
    def thread_close(self):
        self.run = False

    def split_pair(self, str_):
        return str_.split('\\')[-1].split('_')[2]

    def split_year(self, str_):
        return str_.split('\\')[-1].split('_')[4].split('.')[0]

    def split_month(self, str_):
        return '01'


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

    def __getitem__(self, timeStr):
        return self.historical_data.loc[timeStr]

    def __len__(self):
        return len(self.historical_data)
    
    def get_value_by_number(self, number):
        return self.historical_data.iloc[number]

    def get_time(self, index):
        return self.historical_data.index[index]

    def read(self, start_date=None, end_date=None,
                    time_offset=7, ohlc='c', **kwargs):
        self.historical_data = pd.read_csv(self.read_dir, **kwargs)
        self.historical_data.index += offsets.Hour(time_offset)
        start_date = start_date if start_date is not None else 0
        end_date = end_date if end_date is not None else -1
        self.historical_data = self.historical_data[start_date:end_date]
        if ohlc != 'ohlc':
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
