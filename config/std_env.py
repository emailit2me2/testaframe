
"""Environment classes for things specific to this project/company.

Company/project specific setup and teardown should be in here.

L{config.env} has all the top level derived environment classes.
L{config.base_env} has all the base environment classes.

"""

import os
import tempfile

from . import base_env

import services.svc_factory

import db_objects.db_factory
import db_objects.example_db

import pages.sample_pages  # Wish this didn't have to be in here polluting
import pages.wiki_pages

''' This is here to help with the platform_suffix problem.
    Technically only gui_pages that have platform specific pages need to be listed here.
    But it will silently use the generic class, even if you were expecting it to
    use the platform specific one.  So best to list all gui classes here.
'''
ALL_GUI_MODULES = [pages.sample_pages, pages.wiki_pages, ]


# config.our_envs.py is specific to a project or company (in general).
import config.our_envs


class StdEnv(base_env.BaseEnv):
    PROD_SAFE_ATTRS = ('ProdSafe', 'ProdMonitor', 'ProdPing',
                       'ProdSnaps', 'SetupStep1', 'SetupStep2', 'SetupStep3', 'ProdOneTime', 'ProdDaily',
                       'TeardownStep1',)
    MY_JS = ''''''

    def prep_common_services(self, databuilder, default_ident):
        email_creds = self.get_credentials('gmail_creds', {"user": None, "password": None})

        svc_factory = services.svc_factory.ServiceFactory(databuilder)
        svc_factory.add_service("email",
                                base_url=self.get_host(config.our_envs.Host.EMAIL),
                                writes_allowed=self.allows_writes(),
                                port=self.get_port(config.our_envs.Host.EMAIL),
                                user=email_creds['user'],
                                password=email_creds['password'])

        svc_factory.add_service("recorder",
#                                base_url=self.get_url(config.our_envs.Host.RECORDER),
#                                verbose=config.my_cfg.config.get('VERBOSE_RECORDER_OUTPUT', False),
                                writes_allowed=self.allows_writes())

        svc_factory.add_service("tracker",
                                base_url=self.get_url(config.our_envs.Host.TRACKER),
                                additions=config.my_cfg.config.get('TRACKER_WRITER_ADDITIONS', []),
                                subtractions=config.my_cfg.config.get('TRACKER_WRITER_SUBTRACTIONS', []),
                                writes_allowed=self.allows_writes())

        svc_factory.add_service("wikipedia_api",
                                base_url=self.get_url(config.our_envs.Host.WIKIPEDIA_API),
                                writes_allowed=self.allows_writes())

        return svc_factory

    def prep_common_databases(self):
        example_creds = self.get_db_credentials('example', default={})
        db_factory = db_objects.db_factory.DatabaseFactory()
        db_factory.add_database("example",
                                creds=example_creds,
                                writes_allowed=self.allows_writes())

        return db_factory

    def teardown_for_svc(self):
        base_env.BaseEnv.teardown_for_svc(self)


class StdOSBrowserEnv(base_env.BaseOSBrowserEnv):

    def __init__(self):
        base_env.BaseOSBrowserEnv.__init__(self)
        self.all_gui_modules = ALL_GUI_MODULES

    def prep_for_se(self, env):
        return base_env.BaseOSBrowserEnv.prep_for_se(self, env)

    def teardown_for_se(self, test_name):
        base_env.BaseOSBrowserEnv.teardown_for_se(self, test_name)
