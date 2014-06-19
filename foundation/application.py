# python imports
import sys
import logging
import argparse

# iat imports
from .conf import SimpleSettings
from .plugin_manager import PluginManager, ExtensionPoint
from .common import get_app_home, get_root_dir
from .log_utils import setup_root_logger
from .paths import path
from .signals import Signal


logger = logging.getLogger(__name__)
application = None


class Argument(object):

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs


class Application(object):
    """The application object"""

    arguments = ExtensionPoint('application.arguments')

    def __init__(self, name, version):
        """Initialize an application object with the name and
        version of the application

        :param name: application name
        :type name: str

        :param version: application version
        :type version: str
        """
        self.about_to_start = Signal()
        self.about_to_quit = Signal()
        self.enabling_plugin = Signal()
        self.plugin_enabled = Signal()

        # store the application object
        global application
        application = self

        # setup application parameters
        self.name = name
        self.version = version

        # setup basic logging configuration
        logging.basicConfig(level=logging.DEBUG)

        # setup application command line parser
        desc = self.name.capitalize() + ' v' + self.version + ' application help'
        self.option_parser = argparse.ArgumentParser(description=desc)
        self.options = None

        # create application root and home directories
        self.root_dir = path(get_root_dir())
        sys.path.insert(0, self.root_dir)
        self.home_dir = path(get_app_home(self.name))
        if not self.home_dir.exists():
            try:
                self.home_dir.makedirs()
            except Exception as e:
                logger.error(e)

        # load settings
        settings_file = path(self.home_dir).join(self.name.lower() + '.conf')
        self.settings = SimpleSettings(settings_file)
        self.settings.load()

        # setup root logger
        logging.root.removeHandler(logging.root.handlers[0])
        self.log_dir = path(self.home_dir).join('logs')
        if not self.log_dir.exists():
            self.log_dir.makedirs()

        log_file = path(self.log_dir).join(self.name.lower() + '.log')
        log_size = self.settings.setdefault('log_size', 5242880)
        log_count = self.settings.setdefault('log_count', 5)
        fmt_str = '%(asctime)s - %(levelname)s - %(name)s - %(message)s'
        formatter = self.settings.setdefault('log_formatter', fmt_str)
        setup_root_logger(level=logging.INFO, formatter=formatter, log_file=log_file,
                          log_size=log_size, log_count=log_count)

        # create the plugin manager
        self.plugin_dir = path(self.root_dir).join('plugins')
        self.user_plugin_dir = path(self.home_dir).join('plugins')
        if not self.user_plugin_dir.exists():
            self.user_plugin_dir.makedirs()

        dirs = (self.user_plugin_dir, self.plugin_dir)
        PluginManager.register_extension_point(Application.arguments)
        self.plugin_manager = PluginManager(dirs)

        # parse the arguments
        for argument in self.arguments:
            self.option_parser.add_argument(*argument.args, **argument.kwargs)

        help = 'Generate default configuration file based on plugins options'
        self.option_parser.add_argument(
            '-g', '--generate_config', action='store_true', help=help
        )
        self.options = self.option_parser.parse_args()

    def start(self):
        """Start the application"""

        # check command line options
        if self.options.generate_config:
            msg = 'Generating default config file based on enabled plugins'
            logger.info(msg)
            self.generate_default_config()
            return

        logger.info('starting application: %s', self.name)
        try:
            # enable all plugins and start the app
            self.plugin_manager.enable_plugins(self._plugin_notification)

            # signal that we are about to start the application
            self.about_to_start()

            # get the main entry point and execute it
            application = self.plugin_manager.get_service('core.application')
            if application:
                application.start()
        except:
            import traceback
            logger.error(traceback.format_exc())
        finally:
            logger.info('System exit requested')
            self.about_to_quit()
            logger.info('stopping application: %s', self.name)

    def generate_default_config(self):
        settings_file = path(self.home_dir).join(self.name.lower() + '.conf')
        self.settings = SimpleSettings(settings_file)
        self.settings.load()
        for plugin in self.plugin_manager.plugins:
            plugin.configure()
        self.settings.save()

    def get_service(self, id):
        return self.plugin_manager.get_service(id)

    def register_service(self, id, service):
        self.plugin_manager.register_service(id, service)

    def _plugin_notification(self, enabled, plugin):
        if not enabled:
            self.enabling_plugin(plugin)
        else:
            self.plugin_enabled(plugin)

    def __str__(self):
        return self.name + ' ' + self.version
