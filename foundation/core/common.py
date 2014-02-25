# python imports
import os
import sys
import imp
import logging
import logging.handlers
import platform
import time


def get_home_dir():
    """Return the user home directory"""
    return os.path.expanduser('~')


def get_app_home(app_name):
    """Return the application home directory. This will be a directory
    in $HOME/.app_name/ but with app_name lower cased.
    """
    return os.path.join(get_home_dir(), '.' + app_name.lower())


# from http://www.py2exe.org/index.cgi/HowToDetermineIfRunningFromExe
def main_is_frozen():
    """Return True if we are running from an executable, False otherwise"""
    return (
        hasattr(sys, 'frozen') or  # new py2exe
        hasattr(sys, 'importers') or  # old py2exe
        imp.is_frozen('__main__')  # tools/freeze
    )


def get_root_dir():
    """Return the root directory of the application"""

    # was run from an executable?
    if main_is_frozen():
        return os.path.dirname(sys.executable)
    return os.path.dirname(sys.argv[0])


def get_module_path():
    '''Get the path to the current module no matter how it's run.'''
    if '__file__' in globals():
        # If run from py
        return os.path.dirname(__file__)

    # If run from command line or an executable
    return get_root_dir()


def get_module_pkg():
    """Return the module's package path.
    Ej:
        if current module is imagis.utils.common the the call to:
            get_module_pkg()
        should return: imagis.utils
    """
    return '.'.join(__name__.split('.')[:-1])


def get_system_name():
    """Return the system identification name. Posible
    values until now are: (linux, windows, mac).

    :return:
        the system name as a string (linux, windows or mac)
    """
    system_name = platform.system().lower()
    if system_name in ['linux']:
        return 'linux'
    elif system_name in ['windows', 'microsoft']:
        return 'windows'
    elif system_name in ['darwin', 'mac', 'macosx']:
        return 'mac'
    else:
        raise 'iMagis could not detect your system: %s' % system_name

def get_nice_size(n_bytes):
    nice_size = lambda s: [(s % 1024 ** i and "%.1f" % (s / 1024.0 ** i) or \
        str(s / 1024 ** i)) + x.strip() for i, x in enumerate(' KMGTPEZY') \
        if s < 1024 ** (i + 1) or i == 8][0]
    return nice_size(n_bytes)

class ExecutionTime(object):
    """
    Helper that can be used in with statements to have a simple
    measure of the timming of a particular block of code, e.g.
    with ExecutionTime("db flush"):
        db.flush()
    """
    def __init__(self, info="", with_traceback=False):
        self.info = info
        self.with_traceback = with_traceback

    def __enter__(self):
        self.now = time.time()

    def __exit__(self, type, value, stack):
        logger = logging.getLogger(__file__)
        msg = '%s: %s' % (self.info, time.time() - self.now)
        if logger.handlers:
            logger.debug(msg)
        else:
            print msg
        if self.with_traceback:
            import traceback
            msg = traceback.format_exc()
            if logger.handlers:
                logger.error(msg)
            print msg

