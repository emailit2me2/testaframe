
import re
import time
import urllib
import inspect
import urlparse
import traceback

import selenium
#from selenium.common.exceptions import NoSuchElementException
#from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import Select

from locate import *

class PageFactory(object):
  '''Window stuff has to go up to the factory level because
   only it has the cross page context
  '''
  MAIN_WINDOW = 'main'
  def __init__(self, driver, env, preclean, page_classes, platform_suffix, default_highlight_delay):
    self.driver = driver
    self.env = env
    self.handles = {}
    self.preclean = preclean
    self.platform_suffix = platform_suffix
    self.classes = {}
    self.find_page_classes(page_classes)
    self.default_highlight_delay = default_highlight_delay
    self.set_highlight_delay(self.default_highlight_delay)
  def set_highlight_delay(self, highlight_delay=-1):
    if highlight_delay < 0:
      self.highlight_delay = self.default_highlight_delay
    else:
      self.highlight_delay = highlight_delay
    print "Setting highlight delay to %r" % self.highlight_delay

  def find_page_classes(self, modules):
    '''This is here to help with the platform_suffix problem.  Since it is here
       it can autodiscover all the page classes in each file, and then if a
       test requests a new page, the factory can look at all page classes and see
       if there is a platform specific one and instantiate it, otherwise just
       use the regular page class.'''
      # TODO can you protect from collisions in different gui files?
      # don't think so because BasePage you be duplicated by import in all files
    for module in modules:
      self.classes.update(dict(inspect.getmembers(sys.modules[module.__name__], inspect.isclass)))

  def make_page(self, page_class, params, substitutions):
    plat_cls_name = page_class.__name__+self.platform_suffix
    plat_class = self.classes.get(plat_cls_name, page_class)
    if page_class != plat_class:
      print "Making a platform specific page: %s" % (plat_cls_name)
    # end if a platform specific class exists
    new_page = plat_class(self, params, substitutions)
    print "Created page object", new_page.__class__.__name__
    return new_page

  def on_page(self, page_class, params='', substitutions=()):
    print "on page %s" % (page_class.__name__)
    new_page = self.make_page(page_class, params, substitutions)
    new_page.verify_on_page()
    return new_page
  def in_window(self, page_class, params, window_name):
    # params later maybez
    print "on page %s using %s" % (window_name, page_class.__name__)
    new_page = page_class(self, params)
    new_page.window_name = window_name
    all_handles = self.driver.window_handles
    # It doesn't switch to it so we have to deduce which one
    self.handles[window_name] = all_handles[-1]  # assume the last one
    print "Current handles %r" % self.handles.items()
    self.switch_to_window_name(window_name)
    new_page.verify_on_page()
    return new_page
  def switch_to_window_name(self, window_name):
    print "Switching to %s window by %r" % (window_name, self.handles[window_name])
    self.driver.switch_to_window(self.handles[window_name])
  def close_window_name(self, window_name):
    # then go back to the main window, do I really want to autoswitch to main.
    self.switch_to_window_name(window_name)
    self.driver.close()
    self.switch_to_window_name(self.MAIN_WINDOW)
  def at(self, page_class, params='', substitutions=()):
    # params later maybe
    new_page = self.make_page(page_class, params, substitutions)
    print "Going to get %r" % (new_page.full_url())
    self.driver.get(new_page.full_url())
    if self.preclean:  # TODO only needed for IE, since ensureCleanSession doesn't work.
      #print self.driver.get_cookies()
      self.driver.delete_all_cookies()
      #print self.driver.get_cookies()
      self.driver.refresh()
      self.preclean = False  # only do preclean for initial page hit
    # end if preclean needed
    new_page.verify_on_page()
    self.handles[self.MAIN_WINDOW] = self.driver.window_handles[0]
    return new_page


class ObsoletePage(object):
  '''This object is an example of the NullObject pattern.
     Any attempt to use the driver attribute from an old page causes an exception.
  '''
  def __getattr__(self, attr_name):
    raise Exception("Attempt to use obsolete page")

class BaseForm(object):
  TIME_TO_WAIT = 10  # TODO factor out all the constants and delays and retries.
  POLLING_DELAY = 0.1  # TODO factor out all the constants and delays and retries.
  KEYS = Keys
  def __init__(self, parent, params, substitutions):
    print "initing form %s with %r" % (self.__class__.__name__, params)
    self.factory = parent.factory
    self.driver = self.factory.driver
    self.params = params
    self.substitutions = substitutions
    self.parent = parent
    self._prep_finders()
  def __repr__(self):
    return self.__class__.__name__
  def _prep_finders(self):
    raise Exception('_prep_finders() must be defined by derived Pages and Forms.')
  def wait(self, seconds, comment):
    print "     !! waiting %d second(s) because %s !!" % (seconds, comment)
    time.sleep(seconds)

  def by_css(self, locator, log_type_into=True):
      return ByCssSelector(self, locator, log_type_into)
  def by_id(self, locator, log_type_into=True):
      return ByID(self, locator, log_type_into)
  def by_name(self, locator, log_type_into=True):
      return ByName(self, locator, log_type_into)
  def by_tag_name(self, locator, log_type_into=True):
      return ByTagName(self, locator, log_type_into)
  def by_class_name(self, locator, log_type_into=True):
      return ByClassName(self, locator, log_type_into)
  def by_link_text(self, locator, log_type_into=True):
      return ByLinkText(self, locator, log_type_into)
  def by_partial_link_text(self, locator, log_type_into=True):
      return ByPartialLinkText(self, locator, log_type_into)
  def by_xpath(self, locator, log_type_into=True):
    return ByXpath(self, locator, log_type_into)
  def highlight(self, element):
      """Highlights (blinks) a Selenium Webdriver element"""
      if not self.factory.highlight_delay: return
      def apply_style(s):
          self.driver.execute_script("arguments[0].setAttribute('style', arguments[1]);",
                                element, s)
      original_style = element.get_attribute('style')
      apply_style("background: yellow; border: 2px solid red;")
      time.sleep(self.factory.highlight_delay)
      apply_style(original_style)
  def highlight_all(self, elements):
      """Highlights (blinks) a Selenium Webdriver element"""
      if not self.factory.highlight_delay: return
      def apply_style(s):
          self.driver.execute_script("arguments[0].setAttribute('style', arguments[1]);",
                                element, s)
      original_styles = []
      for element in elements:
        original_styles.append(element.get_attribute('style'))
        apply_style("background: yellow; border: 2px solid red;")
      time.sleep(self.factory.highlight_delay)
      for element in elements:
        apply_style(original_styles.pop(0))

  def find_the(self, element_spec, start_with=None):
    # time.sleep(1)  # slow down the script for demos
    sub = 'sub'
    if start_with:
      sub = "sub-"
    else:  # start at the root
      start_with = self.driver
      sub = ""
    #
    print "find %selement %s" % (sub, element_spec)
    start = time.time()
    while time.time() - start < self.TIME_TO_WAIT:
      try:
        ret = start_with.find_element(element_spec.by, element_spec.spec)
        self.highlight(ret)
        #print "  found", ret
        if ret:
          return ret
        else:  # must be None
          exc = Exception("  not found")
          time.sleep(self.POLLING_DELAY)
      except selenium.common.exceptions.NoSuchElementException:
        print "  Waiting for element: %5.2f secs" % (time.time() - start)
        exc = Exception(" no such element")
        time.sleep(self.POLLING_DELAY)
      except selenium.common.exceptions.WebDriverException:
        print "  Waiting for element: %5.2f secs" % (time.time() - start)
        exc = Exception(" web driver exception")
        time.sleep(self.POLLING_DELAY)
      except Exception, exc:
        raise
      #
    # end while not timed out
    raise exc  # TODO exc is not defined, but can't get the message to read pretty when fixed

  def find_all(self, element_spec, start_with=None):
    sub = 'sub'
    if start_with:
      sub = "sub-"
    else:  # start at the root
      start_with = self.driver
      sub = ""
    #
    print "find %selements %s" % (sub, element_spec)
#    raw_input('waiting to find')
    start = time.time()
    while time.time() - start < self.TIME_TO_WAIT:
      try:
        ret = start_with.find_elements(element_spec.by, element_spec.spec)
        print "  found %d element(s)" % len(ret)
        self.highlight_all(ret)
        return ret
      except selenium.common.exceptions.WebDriverException:
        print "  Waiting for elements: %5.2f secs" % (time.time() - start)
        exc = Exception(" no such elements")
        time.sleep(self.POLLING_DELAY)
      except Exception, exc:
        traceback.print_exc()
        raise
      #
    # end while
    raise exc  # TODO exc is not defined, but can't get the message to read pretty when fixed

  def should_not_find_the(self, element_spec):
    try:
      self.driver.find_element(element_spec.by, element_spec.spec)
      print "Element not expected to have been found: %s" % (element_spec)
      return False  #raise Exception("Element not expected to have been found")
    except selenium.common.exceptions.NoSuchElementException:
      print "should not find element %s" % (element_spec)
      return True

  def should_not_find_any(self, element_spec):
    # find_elements returns [] on failure, it doesn't throw so reuse above
    self.should_not_find_the(element_spec)


  def click_on(self, element_spec, start_with=None):
    e = self.find_the(element_spec, start_with)
    print "click on %s" % (element_spec)
    e.click()
  def click_one_of(self, element_spec, index, start_with=None):
    start = time.time()
    while time.time() - start < self.TIME_TO_WAIT:
      e = self.find_all(element_spec, start_with)
      if len(e) >= index+1:
        break
      else:
        print "  Waiting for %d >= %d elements: %5.2f secs" % (len(e), index+1, time.time() - start)
        time.sleep(self.POLLING_DELAY)
      #
    #
    print "click on %s[%d]" % (element_spec,index)
    e[index].click()
  def select_the(self, element_spec, start_with=None):
    e = self.find_the(element_spec, start_with)
    print "select the %s" % (element_spec)
    e.select()
  def select_from(self, element_spec, text, start_with=None):
    e = self.find_the(element_spec, start_with)
    print "select from %s choosing %r" % (element_spec,text)
    from selenium.webdriver.support.ui import Select
    select = Select(e)
    select.select_by_visible_text(text)
  def type_into(self, element_spec, text, clear_first=False, start_with=None):
    e = self.find_the(element_spec, start_with=None)
    if clear_first:
        e.clear()
    e.send_keys(text)
    if not element_spec.log_type_into:  # Don't log passwords and such
      text = "**suppressed**"
    print "type into %s = %r" % (element_spec, text)
  def clear_field(self, element_spec):
    e = self.find_the(element_spec)
    print "clear field %s" % (element_spec)
    e.clear()
  def submit_form(self, element_spec):
    form = self.find_the(element_spec)
    print "submit form " % (element_spec)
    form.submit()


class BasePage(BaseForm):
  # NO asserts in the page objects!  Except verify_on_page()
  PAGE = ''
  PAGE_RE = ''
  PAGE_SUB = ''
  BASE_URL = None
  EVIL_STABLE_PAGE_WAIT = 1
  def __init__(self, factory, params, substitutions, parent=None):
    #print "initing page %s with %s" % (self.__class__.__name__, params)
    self.factory = factory
    self.driver = factory.driver
    self.params = params
    self.substitutions = substitutions
    self.parent = parent
    self.window_name = self.factory.MAIN_WINDOW
    self.wait1 = WebDriverWait(self.driver, self.TIME_TO_WAIT)
    if self.PAGE_SUB and substitutions:
        self.PAGE = self.PAGE_SUB % substitutions
    if not self.PAGE_RE:
      self.PAGE_RE = '^' + self.PAGE + '$'
    self._prep_finders()
  def full_url(self):
    base_url = self.factory.env.env_get_url(self.HOST_ENUM)
    url = urlparse.urljoin(base_url, self.PAGE+self.params)
    #print "full url is %s" % url
    return url
  def refresh_page(self):
    print "Refreshing page"
    self.driver.refresh()
  def go_back(self, page_class):
    self.driver.back()
    return self.now_on(page_class)
  def execute_javascript(self, javascript):
    return self.driver.execute_script(javascript)
  def scroll_right(self):
    return self.driver.execute_script(
      'scrollTo(document.body.scrollWidth,0);return document.body.scrollWidth')
  def scroll_down(self):
    return self.driver.execute_script(
      'scrollTo(0,document.body.scrollHeight);return document.body.scrollHeight')
  def scroll_up(self):
    return self.driver.execute_script('scrollTo(0,0);return document.body.scrollHeight')
  def goto_page(self, page_class, params):
    print "Goto page %s using %s" % (page_class.__name__, params)
    return self.factory.at(page_class, params)
  def now_on(self, page_class, params=''):
    new_page = self.factory.on_page(page_class, params)
    # we should inherit the window name
    if (self.window_name != self.factory.MAIN_WINDOW):
      new_page.window_name = self.window_name
    print "Now on %s with window_name %s" % (page_class.__name__, new_page.window_name)
    self.driver = ObsoletePage()
    return new_page
  def new_window(self, page_class, window_name):
    print "Now on %s window using %s" % (window_name, page_class.__name__)
    return self.factory.in_window(page_class, '', window_name)
  def get_path(self):
    url = self.driver.current_url
    obj = urlparse.urlparse(url)
    path = obj.path
    print "Current url %r" % url, path,obj.fragment
    return path
  def get_title(self):
    title = self.driver.title
    print "Current title %r" % title
    return title
  def verify_on_page(self):
    start = time.time()
    while time.time() - start < (self.TIME_TO_WAIT/2):
      try:
        path_is = self.get_path()
        pattern = self.PAGE_RE % self.__dict__
        to_match = re.compile(pattern)
        print "Verifying %s path pattern %r matches %r" % (
             self.__class__.__name__, self.PAGE_RE, path_is)
        assert to_match.search(path_is), "FAIL: %r does NOT match %r" % (self.PAGE_RE, path_is)
        assert hasattr(self,'verify_element'), 'All pages must have a verify_element defined'
        self.find_the(self.verify_element)
        self.wait(self.EVIL_STABLE_PAGE_WAIT,'stupid wait due to stale element problems')
        return
      except AssertionError, exc:
        print "  Waiting for verify on page: %5.2f secs" % (time.time() - start)
        time.sleep(self.POLLING_DELAY)
      except:
        raise
      #
    # end while
    raise exc
  def switch_to_it(self):
    self.factory.switch_to_window_name(self.window_name)
  def close_it(self):
    print "Closing window %s" % self.window_name
    self.factory.close_window_name(self.window_name)

  def get_cookie(self, cookie):
    cookie = self.driver.get_cookie(cookie)
    ser = urllib.unquote(cookie['value'])
    return ser

  def set_cookie(self, cookie, value):
    self.driver.add_cookie({'name' : cookie, 'value' : value})

  def get_alert(self):
    self.wait1.until(expected_conditions.alert_is_present())
    return AlertObj(self.driver)

# This AlertObj is not great.  TODO make it better.
class AlertObj(object):
  def __init__(self, driver):
    self.alert = Alert(driver)
    print "Creating alert"
  def choose_accept(self):
    print "Choosing accept on alert"
    self.alert.accept()
    print "Accept chosen on alert"
