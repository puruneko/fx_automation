import sys
import numpy as np

class Trade():
    ''' upper class for the class of processing trading '''

    order_type = ('entry', 'exit')
    pos_type = ('long', 'short')
    exit_type = ('standard', 'stoploss', 'takeprof', 'illegal')
    kind = None
    name = []
    header_list = ('id_',)
    entry_list = ('pair','posType','lot',
                'entry_time','entry_rate',
                'get_prof', 'loss_cut',)
    exit_list  = ('exit_time','exit_rate','dec_type',
                'swap','spread',)
    extra_list = ('profit','time_diff',)

    def __init__(self, kind):
        Trade.kind = kind
        for k in kind:
            for pos in pos_type:
                Trade.name.append(k+'_'+pos)

class TradeFlag(Trade):
    ''' flag for trading '''

    def __init__(self):
        self._value = {}
        for k in TradeFlag.kind:
            self._value[k] = {}
            for pos in TradeFlag.pos_type:
                self._value[k][pos] = False

    def __getitem__(self, index):
        return self._value[index]

    def __call__(self, index, bool_):
        return self._value[index] = bool_

    def __iter__(self):
        return self

    def __next__(self):

        return self._value.__next__()

    def __reversed__(self):
        return self._value.__reversed__()

    def set(self, index, _bool):
        return self._value[index] = bool_

class OrderList(Trade):
    ''' contents of order '''

    def __init__(self, tran_type, **kwargs):
        self._list = {}
        self.order_type = order_type
        if order_type == 'entry':
            _list = {k:kwargs[k] for k in OrderList.entry_list}
        elif order_type == 'exit':
            _list = {k:kwargs[k] for k in OrderList.exit_list}

    def __getitem__(self, index):
        return self._list[index]

    def __iter__(self):
        return self._list.__iter__()

    def __next__(self):
        return self._list.__next__()

    def __reversed__(self):
        return self._list.__reversed__()]

class EntryOrderList


class Order(Trade):
    ''' order processing '''

    def __init__(self, tran_type, **kwargs):
        self._orderlist = {}
        self.order_type = order_type
        if order_type == 'entry':
            _list = {k:kwargs[k] for k in OrderList.entry_list}
        elif order_type == 'exit':
            _list = {k:kwargs[k] for k in OrderList.exit_list}


class Ticket(Trade):
    ''' certificate '''

    def __init__(self, pair, posType, lot, get_prof, loss_cut):
        self._tickets = {}
