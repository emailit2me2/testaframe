
"""Basic environment classes and functionality.

This file should be clear of project specific code.
L{config.std_env} has all the company/project specific environment class implementations.
L{config.env} has all the top level derived environment classes.

"""

import os
import pwd
import json
import tempfile
import traceback
import inspect
import sys
import linecache
import datetime

# This is strange having nose stuff here, but it works best here.
from nose.plugins.skip import SkipTest

from selenium.webdriver.chrome.options import Options

import selenium.common.exceptions

import data.databuilder

import pages.base_page

try:
    import config.my_cfg
    # Setting this here, or in my_cfg, means it is the same across all tests in a run even with --processes > 1
    config.my_cfg.config['TEST_PASS_START_TIME'] = config.my_cfg.config.get('TEST_PASS_START_TIME', datetime.datetime.now().isoformat())
except ImportError:
    raise Exception("You must create 'config/my_cfg.py'.  See: config/my_cfg_example.py")
# my_cfg.py is specific to each person (or environment (e.g. CI))

# config.our_envs.py is specific to a project or company (in general).
import config.our_envs


class BaseEnv(object):

    ENV_NAME = ''
    MY_JS = ''

    def teardown_for_svc(self):
        pass

    def create_data_builder(self):
        assert False, "Must be overridden"

    def __repr__(self):
        return "%s_env" % self.ENV_NAME

    def get_host_spec(self, host_enum, spec_enum):
        """Get an arbitrary specification for a specified host.

        The host and the specification should be specified in terms of the
        ENUMs from config.our_envs.
        """
        # non-existent specs should not be an error. If an environment doesn't specify
        # a port, for example, then just return None
        return config.our_envs.envs[self.ENV_NAME][config.our_envs.SpecGroup.HOSTS][host_enum].get(
            spec_enum, None)

    def get_host(self, host_enum):
        return self.get_host_spec(host_enum, config.our_envs.SpecKey.HOST)

    def get_port(self, host_enum):
        return self.get_host_spec(host_enum, config.our_envs.SpecKey.PORT)

    def get_url(self, host_enum):
        host = self.get_host(host_enum)
        port = self.get_port(host_enum)
        return self.get_host_spec(host_enum, config.our_envs.SpecKey.URL_TMPL).format(host=host, port=port)

    def get_env_prefix(self, host_enum):
        return self.get_host_spec(host_enum, config.our_envs.SpecKey.PREFIX)

    def allows_writes(self):
        assert config.our_envs.SpecGroup.ALLOWS_WRITES in config.our_envs.envs[
            self.ENV_NAME], "SpecGroup.ALLOWS_WRITES must be defined by each env: %r" % repr(self)
        return config.our_envs.envs[self.ENV_NAME][config.our_envs.SpecGroup.ALLOWS_WRITES]

    def assert_env_allows_writes(self):
        # print "checking if writes are allowed"
        if not self.allows_writes():
            raise SkipTest("no writes allowed in this env")
        print("writes are allowed in this env")

    def get_my_js(self):
        return self.MY_JS

    def get_db_credentials(self, db_name, default=None):
        db_creds = config.my_cfg.config['db_creds'].get(db_name, default)
        return db_creds

    def get_credentials(self, creds, default=None):
        env_creds = config.my_cfg.config.get(creds, default)
        return env_creds

    def get_username(self):
        for name in ('LOGNAME', 'USER', 'LNAME', 'USERNAME'):
            user = os.environ.get(name)
            if user:
                return user
        # If not user from os.environ.get()
        return pwd.getpwuid(os.getuid())[0]


    # ######## Facebook stuff goes here ###########
    # We can get the FB code back from github or from testaframe if/when we need it.


class FauxStart(object):

    def __init__(self):
        self.poll_max = 1


class BaseOSBrowserEnv(object):
    DO_POPUPS_WORK = False
    NEED_PRECLEAN = False  # needed for IE since it doesn't start a virgin instance each time.
    PLATFORM_SUFFIX = ''  # none by default
    OS_BROWSER = ''

    def __init__(self):
        self.driver = None
        self.all_gui_modules = None

    def get_se_driver(self):
        assert False, "Must be overridden"

    def get_platform_suffix(self):
        return self.PLATFORM_SUFFIX
        # some projects have different pages displayed per OS/browser (usually mobile).
        # so the PLATFORM_SUFFIX allowed for IndexPage_IOS and IndexPage for others.
        # TODO make sure this still works

    def specific_setup(self):
        pass  # overridable

    def force_login(self):
        return config.my_cfg.config.get('FORCE_LOGIN', False)

    def prep_for_se(self, env):
        try:
            self.driver = self.get_se_driver()
            start = pages.base_page.PageFactory(
                self.driver,
                env,
                self.NEED_PRECLEAN,
                self.all_gui_modules,
                self.get_platform_suffix(),
                config.my_cfg.config.get(
                    'HIGHLIGHT_DELAY',
                    0))
            self.driver.implicitly_wait(1)
            self.specific_setup()
            return start
        except Exception as e:
            traceback.print_exc()
            try:
                self.driver.quit()
            finally:
                raise e

    def restart_driver(self, env, tracker):
        start = self.new_driver(env, tracker)
        self.driver = start.driver
        return start

    def new_driver(self, env, tracker, poll_max=20, poll_delay=0.1):
        driver = self.get_se_driver()
        start = pages.base_page.PageFactory(
            driver,
            env,
            self.NEED_PRECLEAN,
            self.all_gui_modules,
            self.get_platform_suffix(),
            config.my_cfg.config.get(
                'HIGHLIGHT_DELAY',
                0))
        start.tracker = tracker
        driver.implicitly_wait(1)
        start.poll_max = poll_max  # push it through for page object use
        start.poll_delay = poll_delay  # push it through for page object use
        return start

    def find_error_messages(self):
        # TODO add a list of expected errors that should be on the page so
        # negative test cases don't have misleading warning messages.
        try:
            if 'Internal Server Error' in self.driver.page_source:
                print("\nFailed with Internal Server Error\n")
        except selenium.common.exceptions.StaleElementReferenceException as e:
            pass  # it is OK if there are no errors.
        #

    def teardown_for_se(self, test_name):
        # see if we failed and take a screen shot if we did
        # TODO only save on failure
        quit_driver = config.my_cfg.config.get('QUIT_DRIVER_ON_EXIT', True)
        try:
            # TODO maybe add datetimestamp.
            # TODO maybe only capture if a failing test, if we can tell
            errors = None  # self.find_error_messages()
            snapshot_dir = config.my_cfg.config.get('SNAPSHOT_DIR', '')
            if snapshot_dir:
                if config.my_cfg.config.get('SNAPSHOT_DIR_AUTOCREATE', False) and not os.path.exists(snapshot_dir):
                    print("Autocreating snapshot dir: %r" % snapshot_dir)
                    os.makedirs(snapshot_dir)
            else:
                snapshot_dir = tempfile.gettempdir()
            if errors or config.my_cfg.config.get('SAVE_SCREENSHOT', False):
                # TODO make an option for named screenshot and/or latest
                snap = os.path.join(snapshot_dir, "snap_%s.png" % test_name)
                print("saving screenshot as: %s" % snap)
                if not self.driver.get_screenshot_as_file(snap):
                    print("FAILED to write snap")
                snap = os.path.join(snapshot_dir, "snap_%s.png" % 'last_test')
                print("saving screenshot as: %s" % snap)
                if not self.driver.get_screenshot_as_file(snap):
                    print("FAILED to write snap")
            if errors or config.my_cfg.config.get('SAVE_SOURCE', False):
                source = os.path.join(snapshot_dir, "source_%s.html" % test_name)
                print("saving source as: %s" % source)
                f = open(source, 'wb')
                f.write(self.driver.page_source.encode('utf8'))
                f.close()
                source = os.path.join(snapshot_dir, "source_%s.html" % 'last_test')
                print("saving source as: %s" % source)
                f = open(source, 'wb')
                f.write(self.driver.page_source.encode('utf8'))
                f.close()
            tb = sys.exc_info()[2]
            if tb:  # then we probably took an exception/assert
                print("=========== Call stack ===========")
                tb = tb.tb_next  # pull off the 2 boilerplate nose test runner frames
                tb = tb.tb_next
                while tb:
                    line = linecache.getline(tb.tb_frame.f_code.co_filename, tb.tb_lineno)[:-1]
                    for l in inspect.getsource(tb.tb_frame).split('\n'):
                        if line == l:
                            print("-->", l)
                        else:
                            print("   ", l)
                    print("-" * 60)

                    tb = tb.tb_next
                # end while tb frames
                print("==================================")
        #
        finally:
            if quit_driver and self.driver:
                self.driver.quit()
                # time.sleep(5) # getting Windows [32] error because process is not stopped, so lets wait a little

    def save_snapshot(self, snap_name):
        snapshot_dir = config.my_cfg.config.get('SNAPSHOT_DIR', '')
        if snapshot_dir:
            if config.my_cfg.config.get('SNAPSHOT_DIR_AUTOCREATE', False) and not os.path.exists(snapshot_dir):
                print("Autocreating snapshot dir: %r" % snapshot_dir)
                os.makedirs(snapshot_dir)
        else:
            snapshot_dir = tempfile.gettempdir()
        snap = os.path.join(snapshot_dir, "snap_%s.png" % (snap_name))
        print("saving screenshot as: %s" % snap)
        self.driver.get_screenshot_as_file(snap)

    def full_snapshot_id(self, snapshot_id, env_name):
        return "%s_on_%s_%s" % (snapshot_id, self.OS_BROWSER, env_name)

    def get_grid_wd(self, caps, host):
        wd = webdriver.Remote(desired_capabilities=caps,
                              command_executor='http://%s/wd/hub' % host)
        print("Remote capabilities", wd.desired_capabilities)
        info_url = "http://%s/grid/api/testsession?session=%s" % (host, wd.session_id)
        import requests
        r = requests.get(info_url, headers={"Content-Type": "application/json"})
        if r.status_code == 200:
            ret = json.loads(r.content)
            # TODO Check data structures, and all return types
            print("Got remote grid session info %s" % repr(ret))
        else:
            print("Error calling for info: %s %s" % (r.status_code, r.content), file=sys.stderr)
        # end
        return wd

