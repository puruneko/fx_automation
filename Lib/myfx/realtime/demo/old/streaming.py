import requests
import json
import queue
import pandas as pd
import oandapyV20
import oandapyV20.endpoints.pricing as pricing
from event import TickEvent
import threading

class StreamingForexPrices(object):
    put_event = threading.Event()

    def __init__(self, access_token, account_id, instruments, events):
        self.access_token = access_token
        self.account_id = account_id
        self.instruments = instruments
        self.events = events

    def connect_to_stream(self):
        try:
            client = oandapyV20.API(access_token=self.access_token)
            params = {'instruments':self.instruments}
            req = pricing.PricingInfo(accountID=self.account_id, params=params)
            return req
        except Exception as e:
            errmsg = 'Caught exception when connecting to stream\n' + str(e)
            req.terminate(errmsg)

    def stream_to_queue(self):
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
        with open("history_stream.txt", "a") as file:
            file.write("@streming\tinit on ready\n")
        while(True):
            if StreamingForexPrices.put_event.is_set():
                res = client.request(req)
                tick = res['prices'][0]
                instrument = tick['instrument']
                time = pd.Timestamp(tick['time'])
                bid  = tick['bids'][0]['price']
                ask  = tick['asks'][0]['price']
                tev = TickEvent(instrument, time, bid, ask)
                self.events.put(tev)
                self.clear_tick_event()
                with open("history_stream.txt", "a") as file:
                    file.write("--- put --->\n")
            with open("history_stream.txt", "a") as file:
                file.write("@Streaming\t{}\n".format(res['prices'][0]))

    def set_tick_event(self):
        StreamingForexPrices.put_event.set()
    def clear_tick_event(self):
        StreamingForexPrices.put_event.clear()

if True:
    events = queue.Queue()
    ACCOUNT_ID = '101-001-6187232-001'
    ACCESS_TOKEN = '451faa1c762459cae6c1dcd3d46d673d-78b5fcfbee57f4ad6846c325d9d69cb4'
    print('start')
    sfp = StreamingForexPrices(ACCESS_TOKEN, ACCOUNT_ID, 'EUR_USD', events)
    sfp.stream_to_queue()
