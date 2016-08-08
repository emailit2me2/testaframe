#!/usr/bin/env python

"""
Browser Launching system.
"""
import argparse

from test_gui.std_tst import StdGuiStandAloneBase
import config.env

from pages.wiki_pages import WikiHomePage


class Launchy(StdGuiStandAloneBase):

    """
    Launches a browser.
    """

    ENVS = {
        "PROD": config.env.Prod_Launchy_Env,
        "STAGING": config.env.Staging_Launchy_Env
    }

    OS_BROWSERS = {
        "firefox": config.env.Local_FF_OSBrowser,
        "chrome": config.env.Local_Chrome_OSBrowser,
        "ie": config.env.Local_IE_OSBrowser,
    }

    AUTO_MODE = StdGuiStandAloneBase.AutomationMode.GUI
    ENV = config.env.Prod_Launchy_Env
    OS_BROWSER = config.env.Local_FF_OSBrowser

    def __init__(self, env, os_browser):
        StdGuiStandAloneBase.__init__(self)
        self.ENV = self.ENVS[env.upper()]
        self.OS_BROWSER = self.OS_BROWSERS[os_browser.lower()]

    def setUp(self):
        StdGuiStandAloneBase.setUp(self)

    def tearDown(self):
        # Make driver stay open
        self.start = None
        StdGuiStandAloneBase.tearDown(self)

    @staticmethod
    def find_automation_shortname():
        return "Launchy"

    def find_automation_name(self):
        pass

    def find_automation_func_name(self):
        pass

    def find_automation_complete_name(self):
        return "Launchy"

    def print_attributes(self):
        pass

    def launch(self):
        self.setUp()
        self.start.at(WikiHomePage)



def main():
    parser = argparse.ArgumentParser(description="Launches a browser.")
    parser.add_argument('-e', '--environment', metavar='Environments', type=str, nargs='?',
                        help='the environment to launch into.', default="PROD")
    parser.add_argument('-b', '--browser', metavar='Browser', type=str, nargs='?',
                        help='the browser to launch. (Only firefox works without added effort)', default="firefox",
                        choices=["firefox", "chrome", "ie"])
    args = parser.parse_args()

    launchy = Launchy(args.environment, args.browser)
    launchy.launch()

# Executes the Terminator when run on it's own.
if __name__ == '__main__':
    main()
