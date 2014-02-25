# python imports
import signal, logging

# gevent and gipc imports
import gevent
from gipc import start_process, pipe

logger = logging.getLogger(__name__)


class ProcessManager(object):
    def __init__(self, workers, check_timout=2, stop_timeout=5):
        self.stop_timeout = stop_timeout
        self.check_timeout = check_timout
        self.workers = workers

        self._processes = {}
        self._monitor = None
        self._stop = False

    def start(self):
        """Start all contributed workers in individual processes"""

        # set the exit and configuration handler for operating system signals
        signals = (
            signal.SIGILL, signal.SIGQUIT, signal.SIGTRAP, signal.SIGABRT,
            signal.SIGFPE, signal.SIGBUS, signal.SIGSEGV, signal.SIGSYS,
            signal.SIGPIPE, signal.SIGTERM, signal.SIGTSTP, signal.SIGTTIN,
            signal.SIGTTOU, signal.SIGXCPU, signal.SIGXFSZ, signal.SIGVTALRM,
            signal.SIGPROF, signal.SIGALRM, signal.SIGUSR2,
        )

        # gevent.signal(signal.SIGHUP, self.reload_config)
        for sig in signals:
            gevent.signal(sig, self.stop)

        try:
            # spawn a green worker for checking the child processes
            # for aliveness and restarting them as needed
            self._stop = False
            self._monitor = gevent.spawn(self._check_alive)

            # start all the workers
            for worker in self.workers:
                self.start_worker(worker)

            # wait for the green worker to stop
            gevent.joinall([self._monitor])
        except (KeyboardInterrupt, SystemExit):
            self.stop()

        logger.info('Main dispatcher process exited')

    def stop(self):
        """"Stop all the dispatcher processes"""

        # stop the monitor first
        self._stop = True
        gevent.joinall([self._monitor])

        # tell all the workers to quit the right way
        for _, (process, channel) in self._processes.iteritems():
            logger.info('telling process: {0} to quit!'.format(process.pid))
            channel.put('QUIT')

            # wait for the process at least 5 seconds and if it cannot
            # terminate, the kill it.
            process.join(self.stop_timeout)
            if process.is_alive():
                msg = 'Process {0} taking to long, terminating it'
                logger.info(msg.format(process.pid))
                process.terminate()

        # remove the process from the internal dict
        for _, (process, _) in self._processes.iteritems():
            process.join()

    def start_worker(self, worker):
        """Start a worker in a separate process

        :param worker: the worker object to be run in a separate process
        """

        # create a bidirectional pipe for the communication
        child_channel, parent_channel = pipe(duplex=True)

        # create and start the worker
        process = start_process(target=worker, args=(child_channel,))
        self._processes[worker] = (process, parent_channel)

        msg = 'Spawning new worker process with pid: {0}'
        logger.info(msg.format(process.pid))

    def _check_alive(self):
        """Check for dead processes and start new ones
        to replace the previous.
        """
        while not self._stop:
            # check the processes ready for removal and restart it if necessary
            for worker, (process, _) in self._processes.iteritems():
                if not process.is_alive() and process.exitcode != 0:
                    msg = 'Worker process with pid: {0} killed'
                    logger.info(msg.format(process.pid))

                    del self._processes[worker]
                    self.start_worker(worker)

                    msg = 'Spawning new worker process to replace the old one'
                    logger.info(msg)

            gevent.sleep(self.check_timeout)
