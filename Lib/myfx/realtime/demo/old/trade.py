import queue
import time
import pandas as pd
import pandas.tseries.offsets as offsets
import threading
from streaming import StreamingForexPrices

class Trade(object):
    def __init__(self, events, strategy, order, heartbeat):
        self.events = events
        self.strategy = strategy
        self.order = order
        self.heartbeat = heartbeat


    def start(self):
        FLAG_loop = True
        while(FLAG_loop):
            nowTime = pd.Timestamp.today().tz_localize('UTC')
            if nowTime.second % self.heartbeat == 0:
                self.set_tick_event()
                with open("history_event.txt", "a") as file:
                    file.write("@trade\t{}  set\n".format(nowTime))
            try:
                event = self.events.get(False)
            except queue.Empty:
                pass
            else:
                if event is not None:
                    if event.type == 'TICK':
                        self.strategy.signal(event)
                    elif event.type == 'ORDER':
                        self.order.send_order(event)
                    elif event.type == 'STOP':
                        FLAG_loop = False
            time.sleep(1)

    def set_tick_event(self):
        StreamingForexPrices.put_event.set()
    def clear_tick_event(self):
        StreamingForexPrices.put_event.clear()
