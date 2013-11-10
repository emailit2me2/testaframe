
import sys
import time
import inspect
#import urllib
#import urlparse

#from nose.plugins.skip import SkipTest

from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

from base_page import BasePage,PageFactory

# There should never be any asserts in pages
# All asserts should be in the tests.

class MyPageFactory(PageFactory):
  def __init__(self, driver, base_url, preclean, platform_suffix):
    PageFactory.__init__(self, driver, base_url, preclean, platform_suffix)
    self.classes = dict(inspect.getmembers(sys.modules[__name__], inspect.isclass))

class StdPage(BasePage):
  LOGIN_LINK_TEXT = 'Log In'
  def _prep_finders(self):
    self.login_link = self.by_link_text(self.LOGIN_LINK_TEXT)

  def do_login(self):
    self.click_on(self.login_link)
    return self.now_on(LoginPage)


class AjaxyPage(StdPage):
  PAGE = "/ajaxy_page.html"
  def _prep_finders(self):
    StdPage._prep_finders(self)
    self.verify_element = self.by_css('#update_butter')
    # Every page needs a unique verify element to make sure it is displaying the correct content
    self.new_label_field = self.by_name('typer')
    self.new_label_form = self.by_css('form')  # forms should have ID's for real code
    self.new_labels = self.by_css('.label')
  def fillout_form(self, new_label):
    self.type_into(self.new_label_field, new_label)
  def submit_fillout_form(self):
    self.submit_form(self.new_label_form)


class ArticlePage(StdPage):
  # Every page needs a PAGE or PAGE_RE, value to make sure the page URL is correct.
  # If no PAGE_RE exists PAGE will be converted into one.
  PAGE = "/wiki/"
  PAGE_RE = "^/wiki/.*$"
  def _prep_finders(self):
    StdPage._prep_finders(self)
    self.verify_element = self.by_css('.mediawiki')
