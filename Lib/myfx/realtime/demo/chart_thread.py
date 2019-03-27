import myenvironment
import sys
import traceback

import threading as th
import time

import myfx.realtime.demo.event_thread as event_thread


class ChartThread():

    def __init__(self, fxevents, interval):
        self.fxevents = fxevents
        self.interval = interval
        self.tick_counter = 0
        self.run = True
    
    def start(self):
        self.th_ = th.Thread(target=self.thread, args=[])
        self.th_.start()
    
    def tick_counter_increament(self, *args, **kwargs):
        self.tick_counter += 1
    
    def thread(self):
        print('chart thread start!')
        self.tick_counter = 0
        try:
            while self.run:
                if self.tick_counter >= self.interval:
                    self.fxevents.put(event_thread.EventContainer(name='draw', value=[]))
                    self.tick_counter = 0
        except:
            print('@ChartThread : exception raised.')
            traceback.print_exc()
            self.fxevents.put(event_thread.EventContainer(name='exception', value=[]))
        print('** chart thread finished!')

    def thread_close(self):
        self.run = False