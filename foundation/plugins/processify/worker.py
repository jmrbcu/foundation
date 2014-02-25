# -*- coding: utf-8 -*-
__author__ = 'jmrbcu'

# python imports
import signal


class Worker(object):

    def __call__(self, channel):
        signal.signal(signal.SIGINT, signal.SIG_IGN)
        self.run(channel)

    def run(self, channel):
        with channel:
            pass
