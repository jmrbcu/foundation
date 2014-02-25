# -*- coding: utf-8 -*-
# iat imports
from foundation.core.plugin_manager import Plugin, ExtensionPoint


class ProcessifyPlugin(Plugin):
    id = 'iat.plugins.processify'
    name = 'Processify Plugin'
    version = '0.1'
    description = 'Processify plugin for the IAT framework'
    platform = 'all'
    author = ['Jose M. Rodriguez Bacallao']
    author_email = 'jrodriguez@interactivetel.com'
    depends = []
    enabled = True

    workers = ExtensionPoint('processify.workers')

    def enable(self):
        # create and register the dispatcher so that any other plugin
        # that need it can look for it
        from foundation.core.application import application
        from .process_manager import ProcessManager

        # get the global settings
        settings = application.settings

        # read/setup our settings
        settings = settings.setdefault('processify', {})
        stop_timeout = settings.setdefault('stop_timeout', 10)
        check_timeout = settings.setdefault('check_timeout', 2)

        # create dispatcher services
        process_manager = ProcessManager(self.workers, check_timeout,
                                         stop_timeout)

        # register the service
        self.plugin_manager.register_service('core.application',
                                             process_manager)
