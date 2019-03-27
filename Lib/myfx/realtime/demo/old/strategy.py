import queue
from event import OrderEvent

class Strategy(object):
    def __init__(self, instrument, units, events):
        self.instrument = instrument
        self.units = units
        self.events = events

    def signal(self, tick):
        with open("history_event.txt", "a") as file:
            file.write("@signal\t{}  Bid:{}\n".format(tick.time, tick.bid))

class TestStrategy(Strategy):
    def __init__(self, instrument, units, events):
        super.__init__(instrument, units, events)

    def signal(self, tick):
        pass
