__author__ = 'jmrbcu'

# python imports
import os
import time
import logging

# gevent imports
try:
    # gevent compatibility
    from gevent.monkey import patch_all
    patch_all(thread=False)
except ImportError:
    pass

logger = logging.getLogger(__file__)


class Tail(object):

    HEAD, TAIL = (0, 2)

    def __init__(self, filename, callback, start=HEAD):
        self.filename = filename
        self.callback = callback
        self.fp = None
        self.start = start
        self.last_size = 0
        self.last_inode = -1
        self.last_line = ''

    def process_file(self):
        if self.fp is None:
            try:
                msg = 'Openning file: {0} for tailing'
                logger.info(msg.format(self.filename))
                self.fp = open(self.filename, 'r')
                self.fp.seek(0, self.start)
                stat = os.stat(self.filename)
                self.last_inode = stat.st_ino
                self.last_size = 0
            except Exception as e:
                logger.error('Cannot open the file: {0}'.format(self.filename))
                if self.fp:
                    self.fp.close()
                self.fp = None
                return

        # check to see if file has moved under us
        try:
            stat = os.stat(self.filename)
            size = stat.st_size
            inode = stat.st_ino

            if size < self.last_size or inode != self.last_inode:
                self.last_size = size
                self.last_inode = inode
                raise Exception
        except Exception as e:
            logger.info('File: {0} was rotated, updating'.format(self.filename))
            self.fp.close()
            self.fp = None
            return

         # read if size has changed
        if self.last_size < size:
            self.last_size = size
            while True:
                line = self.fp.readline()
                time.sleep(0)
                if not line:
                    return

                if self.callback:
                    self.callback(line)

    def mainloop(self, sleepfor=0.1):
        try:
            while True:
                self.process_file()
                time.sleep(sleepfor)
        except (KeyboardInterrupt, SystemExit):
            raise
        finally:
            if self.fp:
                self.fp.close()
                self.fp = None

if __name__ == '__main__':
    import sys
    import gevent

    logging.basicConfig(level=logging.INFO)

    def test_writing():
        with open('test_tailer.txt', 'w') as f:
            while True:
                f.write('Line written to the test file from another greenlet\n')
                f.flush()
                time.sleep(0.5)

    def test_head():
        try:
            Tail('test_tailer.txt', sys.stdout.write).mainloop(0.1)
        except KeyboardInterrupt:
            pass

    def test_tail():
        try:
            tailer = Tail('test_tailer.txt', sys.stdout.write, Tail.TAIL)
            tailer.mainloop(0.1)
        except KeyboardInterrupt:
            pass

    logger.info('STARTING')
    test_head()





