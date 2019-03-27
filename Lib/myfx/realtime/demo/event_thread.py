import myenvironment
import sys
import traceback

import queue
import threading as th

from myfx.realtime.demo.fx_thread import FXThreadException


class EventThread():

    def __init__(self, fxevents, method={}):
        self.fxevents = fxevents
        self.method = method
        self.run = True
    
    def set_connection(self, event_name, event_method):
        if not event_name in self.method:
            self.method[event_name] = []
        self.method[event_name].append(event_method)
    
    def start(self):
        self.th_ = th.Thread(target=self.thread, args=[])
        self.th_.start()
    
    def thread(self):
        print('event thread start!')
        try:
            while self.run:
                try:
                    e = self.fxevents.get(False)
                except queue.Empty:
                    pass
                else:
                    event_name = e.get_name()
                    argument = e.get_value()
                    #print('@eventThread:{} event recieved!'.format(event_name))
                    for m in self.method[event_name]:
                        m(*argument)
        except:
            print('@eventThread : exception raised.')
            traceback.print_exc()
            for m in self.method['exception']:
                m([])
        print('** event thread finished!')
    
    def thread_close(self):
        self.run = False


class EventContainer():

    def __init__(self, name, value):
        self.name = name
        self.value = value
    
    def get_name(self):
        return self.name

    def get_value(self):
        return self.value

    def set_name(self, name):
        self.name = name

    def set_value(self, value):
        self.value = value