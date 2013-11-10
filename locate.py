

import gc
import re
import sys
#import time
#import selenium
#from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.by import By

class ByBase(object):
  NON_NAMES = ['self','element_spec']
  by = None  # must be defined by subclasses

  # TODO support indexing, thing[2].the_text() or thing.the_text(2)

  def __init__(self, page, spec):
    self.page = page
    self.spec = spec
    assert self.by, "self.by must be defined by subclasses"
  def __log_action(self, action):
    item_name = self.find_name()
    print "%s on item %s" % (action, item_name)

  def find_name(self):
    # This is kind of odd but we want to know what this variable is named in
    # the outside world.  Rather than having to pass in a string name.
    frame = sys._getframe()
    for frame in iter(lambda: frame.f_back, None):
      frame.f_locals
    result = []
    for referrer in gc.get_referrers(self):
      if isinstance(referrer, dict):
        for k, v in referrer.iteritems():
          if v is self and k not in self.NON_NAMES:
            result.append(k)
  # TODO this is a good assert normally
  # assert len(result) == 1, "Problem finding a name for %r, found %r" % (self.spec, result)
    return result[0]
  def __str__(self):
    return "%r using %s=%r" % (self.find_name(), self.by, self.spec)
  def the_text(self):
    return self.page.find_the(self).text
  def all_the_text(self):
    return [e.text for e in self.page.find_all(self)]
  def rows_of_text(self, cell_spec):
      all =[]
      for e in self.page.find_all(self):
        all.append([e.text for e in self.page.find_all(cell_spec, e)])
      return all
  def the_attribute(self, attrib, index=0):
    #return self.page.find_all(self)[index].get_attribute(attrib)
    return self.page.find_the(self).get_attribute(attrib)
  def all_the_attributes(self, attrib):
    all = self.page.find_all(self)
    return [e.get_attribute(attrib) for e in all]
  def is_this_enabled(self):
    #assert self.page.find_the(self).is_displayed()
    return self.page.find_the(self).is_enabled()
  def is_this_displayed(self):
    is_it = self.page.find_the(self).is_displayed()
    print "    Is %s displayed?: %s" % (self,is_it)
    return is_it

  def int_of(self):
    try:
      print "         text for int %r" % self.page.find_the(self).text
      i = int(self.page.find_the(self).text)
      return i
    except ValueError:
      return None  # this will happen for int('')

  def all_ints_of(self):
    try:
      all = [e.text for e in self.page.find_all(self)]
      print "         text for all int %r" % all
      ints = [int(t) for t in all]
      return ints
    except ValueError:
      return []  # this will happen for int('')

  def int_of_attribute_of(self, attrib):
    try:
      i = int(self.page.find_the(self).get_attribute(attrib))
      return i
    except ValueError:
      return None  # this will happen for int('')

  def length_of(self):
    print "  Checking length of %s" % (self)
    all = self.page.find_all(self)
    #print "   found all of %r" % all
    l = len(all)
    print "    got len = %r" % l
    return l
  def length_of_displayed(self):
    print "  Checking length of displayed %s" % (self)
    all = self.page.find_all(self)
    #print "   found all of %r" % all
    l = len(all)
    print "    got len = %r" % l
    count = 0
    for e in all:
      if e.is_displayed():
        print "is displayed", e
        count += 1
    return count
  def value_of(self):
    return self.the_attribute("value")
  def get_name(self):
    return self.the_attribute("name")
  def the_y_position(self):
    print "  The location of %s is %s" % (self,self.page.find_the(self).location)
    return self.page.find_the(self).location["y"]

class ByXpath(ByBase):
  by = By.XPATH
class ByID(ByBase):
  by = By.ID
class ByName(ByBase):
  by = By.NAME
class ByTagName(ByBase):
  by = By.TAG_NAME
class ByCssSelector(ByBase):
  by = By.CSS_SELECTOR
class ByClassName(ByBase):
  by = By.CLASS_NAME
  def __init__(self, page, spec):
    # no compund class names are allowed, at least for remote. TODO fix me
    assert (not re.compile('[\.\ ]').search(spec)), "Compound class name %r" % spec
    ByBase.__init__(self, page, spec)
class ByLinkText(ByBase):
  by = By.LINK_TEXT
class ByPartialLinkText(ByBase):
  by = By.PARTIAL_LINK_TEXT


