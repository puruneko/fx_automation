import sys
import oandapyV3
import time
import json
import oandapyV20
import oandapyV20.endpoints.instruments as instruments
import oandapyV20.endpoints.pricing as pricing
import pandas as pd

print('start')
ACCOUNT_ID = '101-001-6187232-001'
ACCESS_TOKEN = '451faa1c762459cae6c1dcd3d46d673d-78b5fcfbee57f4ad6846c325d9d69cb4'

client = oandapyV20.API(access_token=ACCESS_TOKEN)
params = {"instruments":'EUR_USD'}
req = pricing.PricingInfo(accountID=ACCOUNT_ID, params=params)
res = client.request(req)
print(res['prices'])
tick = res['prices'][0]
instrument = tick['instrument']
time = pd.Timestamp(tick['time'])
bid  = tick['bids'][0]['price']
ask  = tick['asks'][0]['price']
print("{} {} {} {}".format(time, instrument, bid, ask))

comment='''
rq = pricing.PricingStream(accountID=ACCOUNT_ID, params=params)
rs = client.request(rq)
maxrecs = -1
for ticks in rs:
    #print(json.dumps(ticks, indent=2), ',')
    if ticks['type']=='PRICE':
        time = pd.Timestamp(ticks['time'])
        bid  = ticks['bids'][0]['price']
        ask  = ticks['asks'][0]['price']
        with open("history2.txt", "a") as file:
            file.write("{} (B:{}, A:{})\n".format(time, bid, ask))
    if maxrecs == 0:
        rq.terminate("maxrecs recoeds receiced.")
    maxrecs -= 1
'''
