
import sys
import time
import inspect
#import urllib
#import urlparse

#from nose.plugins.skip import SkipTest

from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

from base_page import BasePage,PageFactory

import our_envs

# There should never be any asserts in pages
# All asserts should be in the tests.

class MyPageFactory(PageFactory):
  ''' This is here to help with the platform_suffix problem.  Since it is here
      it can autodiscover all the page classes in this file, and then if a
      test requests a new page, the factory can look at all page classes and see
      if there is a platform specific one and instantiate it, otherwise just
      use the regular page class.
  '''
  # TODO what would we do if there needed to be multiple *_pages.py files?
  def __init__(self, driver, env, preclean, platform_suffix, default_highlight_delay):
    PageFactory.__init__(self, driver, env, preclean, platform_suffix, default_highlight_delay)
    self.classes = dict(inspect.getmembers(sys.modules[__name__], inspect.isclass))

class StdPage(BasePage):
  LOGIN_LINK_TEXT = 'Log In'
  def _prep_finders(self):
    self.login_link = self.by_link_text(self.LOGIN_LINK_TEXT)

  def do_login(self):
    self.click_on(self.login_link)
    return self.now_on(LoginPage)


class AjaxyPage(StdPage):
  HOST_ENUM = our_envs.SE_HOST_ENUM
  PAGE = "/ajaxy_page.html"
  def _prep_finders(self):
    StdPage._prep_finders(self)
    self.verify_element = self.by_css('#update_butter')
    # Every page needs a unique verify element to make sure we are on the correct page
    self.new_label_field = self.by_name('typer')
    self.new_label_form = self.by_css('form')  # forms should have ID's for real code
    self.new_labels = self.by_css('.label')
    # setting log_type_into=False suppresses printing of the passed in text
    self.password_field = self.by_css('#input-password',log_type_into=False) #suppresses
  def fillout_form(self, new_label):
    self.type_into(self.new_label_field, new_label)
  # It is common to split filling out a form and submitting a form so you can test error cases
  # in form validation.
  def submit_fillout_form(self):
    self.submit_form(self.new_label_form)
  # For optional form fields, or to test missed fields, make a parameter default to None and
  # then add an if around the filling out part.
  def fake_fillout_login_form(self, username=None, password=None):
    if username:
      self.type_into(self.username_field, username)
    if password:
      self.type_into(self.password_field, password)


# example page object for a wikipedia.org article
class ArticlePage(StdPage):
  HOST_ENUM = our_envs.WIKI_HOST_ENUM
  # Every page needs a PAGE (or PAGE_SUB) or PAGE_RE (the _RE stands for regular expression,
  # like the re module) value to make sure the page URL is correct in verify_on_page().
  # If no PAGE_RE exists PAGE will be converted into one.
  PAGE_RE = "^/wiki/.*$"
  PAGE_SUB = "/wiki/%s"  # A PAGE_SUB creates a PAGE using python's % operator
  def _prep_finders(self):
    StdPage._prep_finders(self)
    self.verify_element = self.by_css('.mediawiki')
