import myenvironment
import sys
import threading as th


class FXThreadException(Exception):

    def __init__(self, *args, **kwargs):
        super(FXThreadException, self).__init__(*args, *kwargs)

