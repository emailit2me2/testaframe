
"""Top level derived environment classes.

This file should be clear of project specific code.
L{config.std_env} has all the company/project specific environment class implementations.
L{config.base_env} has all the base environment classes.

"""
import config.our_envs
import data.databuilder
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.chrome.options import Options
from . import std_env
import traceback


class SystemEnv(std_env.StdEnv):
    pass


# This class may no longer be necessary
class API_OSBrowser(std_env.StdOSBrowserEnv):
    OS_BROWSER = 'API'


class OSBrowserEnv(API_OSBrowser):

    def prep_for_se(self, env):
        try:
            return API_OSBrowser.prep_for_se(self, env)
        except Exception as exc:
            traceback.print_exc()
            try:
                self.driver.quit()
            finally:
                raise exc

    def teardown_for_se(self, test_name):
        API_OSBrowser.teardown_for_se(self, test_name)


class Localhost_Env(SystemEnv):
    ENV_NAME = config.our_envs.Environment.LOCALHOST

    def create_data_builder(self):
        return data.databuilder.TestDataBuilder()


class LocalVM_Env(SystemEnv):
    ENV_NAME = config.our_envs.Environment.LOCAL_VM

    def create_data_builder(self):
        return data.databuilder.TestDataBuilder()


class Dev_Env(SystemEnv):
    ENV_NAME = config.our_envs.Environment.DEV

    def create_data_builder(self):
        return data.databuilder.TestDataBuilder()


class CI_Env(SystemEnv):
    ENV_NAME = config.our_envs.Environment.CI

    def create_data_builder(self):
        return data.databuilder.CIDataBuilder()


class QA_Env(SystemEnv):
    ENV_NAME = config.our_envs.Environment.QA

    def create_data_builder(self):
        return data.databuilder.QADataBuilder()


class Staging_Env(SystemEnv):
    ENV_NAME = config.our_envs.Environment.STAGING

    def create_data_builder(self):
        return data.databuilder.StagingDataBuilder()


class Prod_Env(SystemEnv):
    ENV_NAME = config.our_envs.Environment.PROD
    ATTRS_ARE_ORED_WARNING = "run_PROD.py multiple -a args are or'ed, should be '-a ProdSafe,Smoke'."

    def __init__(self, *args):
        import sys
        assert [arg for arg in sys.argv if [attr for attr in self.PROD_SAFE_ATTRS if attr in arg]
                ], """run_PROD.py should only be run with -a %s.""" % "|".join(self.PROD_SAFE_ATTRS)
        assert ['-a'] == [arg for arg in sys.argv if arg.startswith('-a')], self.ATTRS_ARE_ORED_WARNING
        # assert [] == [arg for arg in sys.argv if arg.startswith('--processes')],
        #                                             "run_PROD.py can not be run multiprocess."
        # fail for multiprocess in Prod_env (above) or only warn (below)  # TODO add to config.our_envs.py
        if [] != [arg for arg in sys.argv if arg.startswith('--processes')]:
            print("Warning: running multiprocess can be dangerous against Prod.")
        SystemEnv.__init__(self, *args)

    def create_data_builder(self):
        return data.databuilder.ProdDataBuilder()


class Prod_Terminator_Env(SystemEnv):
    ENV_NAME = config.our_envs.Environment.PROD

    def create_data_builder(self):
        return data.databuilder.ProdDataBuilder()

    def env_print_attributes(self):
        pass


class Staging_Terminator_Env(SystemEnv):
    ENV_NAME = config.our_envs.Environment.STAGING

    def create_data_builder(self):
        return data.databuilder.ProdDataBuilder()

    def env_print_attributes(self):
        pass


class Prod_Launchy_Env(SystemEnv):
    ENV_NAME = config.our_envs.Environment.PROD

    def create_data_builder(self):
        return data.databuilder.ProdDataBuilder()

    def env_print_attributes(self):
        pass


class Staging_Launchy_Env(SystemEnv):
    ENV_NAME = config.our_envs.Environment.STAGING

    def create_data_builder(self):
        return data.databuilder.StagingDataBuilder()

    def env_print_attributes(self):
        pass


class Local_FF_OSBrowser(OSBrowserEnv):
    DO_POPUPS_WORK = False
    OS_BROWSER = 'Local_FF'
    PLATFORM_SUFFIX = 'FF'

    def my_se(self):
        return "Local_FF Se for %s" % self.__class__.__name__

    def get_se_driver(self):
        drv = webdriver.Firefox()
        # size = drv.get_window_size()
        # drv.set_window_size(1025,size['height'])
        return drv


class Local_Chrome_OSBrowser(OSBrowserEnv):
    OS_BROWSER = 'Local_Chrome'
    DO_POPUPS_WORK = True

    def my_se(self):
        return "Local_Chrome Se for %s" % self.__class__.__name__

    def get_se_driver(self):
        opts = Options()
        opts.add_argument('start-maximized')
        #opts.add_argument('remote-debugging-port=9222')
        ret = webdriver.Chrome(chrome_options=opts)
        return ret


class Local_PhantomJS_OSBrowser(OSBrowserEnv):
    OS_BROWSER = 'Local_PhantomJS'
    DO_POPUPS_WORK = True

    def my_se(self):
        return "Local_PhantomJS Se for %s" % self.__class__.__name__

    def get_se_driver(self):
        return webdriver.PhantomJS()


class Local_IE_OSBrowser(OSBrowserEnv):
    OS_BROWSER = 'Local_IE'
    DO_POPUPS_WORK = True
    NEED_PRECLEAN = True

    def my_se(self):
        return "Local_IE Se for %s" % self.__class__.__name__

    def get_se_driver(self):
        return webdriver.Ie()


class Linux_FF_OSBrowser(OSBrowserEnv):
    OS_BROWSER = 'Linux_FF'

    def my_se(self):
        return "Linux_FF Se for %s" % self.__class__.__name__

    def env_driver(self):
        host = config.my_cfg.config['HOST']['LINUX']
        return webdriver.Remote(desired_capabilities=DesiredCapabilities.FIREFOX,
                                command_executor='http://%s/wd/hub' % host)

    def get_se_driver(self):
        return self.env_driver()


class Linux_Chrome_OSBrowser(OSBrowserEnv):
    OS_BROWSER = 'Linux_Chrome'
    DO_POPUPS_WORK = True

    def my_se(self):
        return "Linux_Chrome Se for %s" % self.__class__.__name__

    def env_driver(self):
        host = config.my_cfg.config['HOST']['LINUX']
        return webdriver.Remote(desired_capabilities=DesiredCapabilities.CHROME,
                                command_executor='http://%s/wd/hub' % host)

    def get_se_driver(self):
        return self.env_driver()


class OSX_FF_OSBrowser(OSBrowserEnv):
    OS_BROWSER = 'OSX_FF'

    def my_se(self):
        return "OSX_FF Se for %s" % self.__class__.__name__

    def env_driver(self):
        host = config.my_cfg.config['HOST']['OSX']
        drv = webdriver.Remote(desired_capabilities=DesiredCapabilities.FIREFOX,
                               command_executor='http://%s/wd/hub' % host)
        size = drv.get_window_size()
        drv.set_window_size(1300, size['height'])
        return drv

    def get_se_driver(self):
        return self.env_driver()


class OSX_Chrome_OSBrowser(OSBrowserEnv):
    OS_BROWSER = 'OSX_Chrome'
    DO_POPUPS_WORK = True

    def my_se(self):
        return "OSX_Chrome Se for %s" % self.__class__.__name__

    def env_driver(self):
        host = config.my_cfg.config['HOST']['OSX']
        dc = DesiredCapabilities.CHROME
        dc['chrome.switches'] = ['--start-maximized']
        return webdriver.Remote(desired_capabilities=dc,
                                command_executor='http://%s/wd/hub' % host)

    def get_se_driver(self):
        return self.env_driver()


class IPhone_OSBrowser(OSBrowserEnv):
    OS_BROWSER = 'iPhone'
    PLATFORM_SUFFIX = 'IOS'
    DO_POPUPS_WORK = True

    def my_se(self):
        return "IPhone Se for %s" % self.__class__.__name__

    def env_driver(self):
        host = config.my_cfg.config['HOST']['IPHONE']
        dc = DesiredCapabilities.IPHONE
        print(dc, host)
        return webdriver.Remote(desired_capabilities=dc,
                                command_executor='http://%s/wd/hub' % host)

    def get_se_driver(self):
        return self.env_driver()


class Android_OSBrowser(OSBrowserEnv):
    OS_BROWSER = 'Android'
    DO_POPUPS_WORK = True

    def my_se(self):
        return "Android Se for %s" % self.__class__.__name__

    def env_driver(self):
        host = config.my_cfg.config['HOST']['ANDROID']
        dc = DesiredCapabilities.ANDROID
        print(dc, host)
        return webdriver.Remote(desired_capabilities=dc,
                                command_executor='http://%s/wd/hub' % host)

    def get_se_driver(self):
        return self.env_driver()


class Prod_OSX_Chrome_OSBrowser(OSBrowserEnv):
    OS_BROWSER = 'Prod_OSX_Chrome'
    DO_POPUPS_WORK = True

    def my_se(self):
        return "Prod_OSX_Chrome Se for %s" % self.__class__.__name__

    def env_driver(self):
        host = config.my_cfg.config['HOST']['PROD_OSX']
        dc = DesiredCapabilities.CHROME
        dc['chrome.switches'] = ['--start-maximized']
        return webdriver.Remote(desired_capabilities=dc,
                                command_executor='http://%s/wd/hub' % host)

    def get_se_driver(self):
        return self.env_driver()


class Win7_FF_OSBrowser(OSBrowserEnv):
    OS_BROWSER = 'Win7_FF'
    DO_POPUPS_WORK = False

    def my_se(self):
        return "Win7_FF Se for %s" % self.__class__.__name__

    def env_driver(self):
        host = config.my_cfg.config['HOST']['WIN_7']
        drv = webdriver.Remote(desired_capabilities=DesiredCapabilities.FIREFOX,
                               command_executor='http://%s/wd/hub' % host)
        size = drv.get_window_size()
        drv.set_window_size(1025, size['height'])
        return drv

    def get_se_driver(self):
        return self.env_driver()


class Win7_Chrome_OSBrowser(OSBrowserEnv):
    OS_BROWSER = 'Win7_Chrome'
    DO_POPUPS_WORK = True

    def my_se(self):
        return "Win7_Chrome Se for %s" % self.__class__.__name__

    def env_driver(self):
        host = config.my_cfg.config['HOST']['WIN_7']
        dc = DesiredCapabilities.CHROME
        dc['chrome.switches'] = ['--start-maximized']
        return webdriver.Remote(desired_capabilities=dc,
                                command_executor='http://%s/wd/hub' % host)

    def get_se_driver(self):
        return self.env_driver()


class Win7_IE_OSBrowser(OSBrowserEnv):
    OS_BROWSER = 'Win7_IE'
    NEED_PRECLEAN = True
    DO_POPUPS_WORK = True

    def my_se(self):
        return "Win_IE Se for %s" % self.__class__.__name__

    def env_driver(self):
        host = config.my_cfg.config['HOST']['WIN_7']
        dc = DesiredCapabilities.INTERNETEXPLORER
        dc['ensureCleanSession'] = 'true'  # this just doesn't work.  we stay logged in from prev test.
        wd = webdriver.Remote(desired_capabilities=dc,
                              command_executor='http://%s/wd/hub' % host)
        return wd

    def get_se_driver(self):
        return self.env_driver()


class WinXP_FF_OSBrowser(OSBrowserEnv):
    OS_BROWSER = 'WinXP_FF'
    DO_POPUPS_WORK = False

    def my_se(self):
        return "WinXP_FF Se for %s" % self.__class__.__name__

    def env_driver(self):
        host = config.my_cfg.config['HOST']['WIN_XP']
        drv = webdriver.Remote(desired_capabilities=DesiredCapabilities.FIREFOX,
                               command_executor='http://%s/wd/hub' % host)
        size = drv.get_window_size()
        drv.set_window_size(1025, size['height'])
        return drv

    def get_se_driver(self):
        return self.env_driver()


class WinXP_Chrome_OSBrowser(OSBrowserEnv):
    OS_BROWSER = 'WinXP_Chrome'
    DO_POPUPS_WORK = True

    def my_se(self):
        return "WinXP_Chrome Se for %s" % self.__class__.__name__

    def env_driver(self):
        host = config.my_cfg.config['HOST']['WIN_XP']
        dc = DesiredCapabilities.CHROME
        dc['chrome.switches'] = ['--start-maximized']
        return webdriver.Remote(desired_capabilities=dc,
                                command_executor='http://%s/wd/hub' % host)

    def get_se_driver(self):
        return self.env_driver()


class WinXP_IE_OSBrowser(OSBrowserEnv):
    OS_BROWSER = 'WinXP_IE'
    NEED_PRECLEAN = True
    DO_POPUPS_WORK = True

    def my_se(self):
        return "WinXP_IE Se for %s" % self.__class__.__name__

    def env_driver(self):
        host = config.my_cfg.config['HOST']['WIN_XP']
        dc = DesiredCapabilities.INTERNETEXPLORER
        # dc['ensureCleanSession'] = 'true'  # this just doesn't work.  we stay logged in from prev test.
        wd = webdriver.Remote(desired_capabilities=dc,
                              command_executor='http://%s/wd/hub' % host)
        return wd

    def get_se_driver(self):
        return self.env_driver()


class WinXP_IE8_OSBrowser(OSBrowserEnv):
    OS_BROWSER = 'WinXP_IE8'
    NEED_PRECLEAN = True
    DO_POPUPS_WORK = True

    def my_se(self):
        return "WinXP_IE8 Se for %s" % self.__class__.__name__

    def env_driver(self):
        host = config.my_cfg.config['HOST']['WIN_XP_IE8']
        dc = DesiredCapabilities.INTERNETEXPLORER
        wd = webdriver.Remote(desired_capabilities=dc,
                              command_executor='http://%s/wd/hub' % host)
        return wd

    def get_se_driver(self):
        return self.env_driver()


class Grid_Chrome_OSBrowser(OSBrowserEnv):
    OS_BROWSER = 'Grid Chrome'
    DO_POPUPS_WORK = True

    def my_se(self):
        return "Grid_Chrome Se for %s" % self.__class__.__name__

    def env_driver(self):
        host = config.my_cfg.config['HOST']['GRID']
        caps = DesiredCapabilities.CHROME
        # caps['platform'] = 'OSX'
        return self.get_grid_wd(caps, host)

    def get_se_driver(self):
        return self.env_driver()


class Grid_FF_OSBrowser(OSBrowserEnv):
    OS_BROWSER = 'Grid FF'

    def my_se(self):
        return "Grid_FF Se for %s" % self.__class__.__name__

    def env_driver(self):
        host = config.my_cfg.config['HOST']['GRID']
        caps = DesiredCapabilities.FIREFOX
        # caps['platform'] = 'OSX'
        return self.get_grid_wd(caps, host)

    def get_se_driver(self):
        return self.env_driver()


class Grid_IE_OSBrowser(OSBrowserEnv):
    OS_BROWSER = 'Grid IE'
    NEED_PRECLEAN = True
    DO_POPUPS_WORK = True

    def my_se(self):
        return "Grid_IE Se for %s" % self.__class__.__name__

    def env_driver(self):
        host = config.my_cfg.config['HOST']['GRID']
        caps = DesiredCapabilities.INTERNETEXPLORER
        # caps['platform'] = 'WIN'
        return self.get_grid_wd(caps, host)

    def get_se_driver(self):
        return self.env_driver()
