
import sys
import time
#import urllib
#import urlparse

#from nose.plugins.skip import SkipTest

from std_pages import StdPage

import our_envs

# There should never be any asserts in pages
# All asserts should be in the tests.


# example page object for a wikipedia.org article
class ArticlePage(StdPage):
  HOST_ENUM = our_envs.WIKI_HOST_ENUM
  # Every page needs a PAGE (or PAGE_SUB) or PAGE_RE (the _RE stands for regular expression,
  # like the re module) value to make sure the page URL is correct in verify_on_page().
  # If no PAGE_RE exists PAGE will be converted into one.
  PAGE_RE = "^/wiki/.*$"
  PAGE_SUB = "/wiki/%s"  # A PAGE_SUB creates a PAGE using python's % operator
  MOBILE_VIEW_LINK_TEXT = 'Mobile view'
  def _prep_finders(self):
    StdPage._prep_finders(self)
    self.verify_element = self.by_css('.mediawiki')
    # See docs for: Add a new page class
    self.verify_element = self.by_css('.collapsible-nav')

    # See docs for: Add a locator to a page
    self.powered_by_link = self.by_css('#footer-poweredbyico a')
    self.mobile_view_link = self.by_link_text(self.MOBILE_VIEW_LINK_TEXT)
    self.search_input = self.by_css('#searchInput')
    self.search_form = self.by_css('#searchform')
  # See docs for: add a function to a page
  def do_search(self, search_term):
    self.type_into(self.search_input, search_term)
    self.submit_form(self.search_form)
    return self.now_on(ArticlePage)
  # See docs for: Add a new page class
  def goto_mobile_view(self):
    self.click_on(self.mobile_view_link)
    return self.now_on(MobileArticlePage)


class ArticlePageFF(ArticlePage):
  '''This class is a trivial example of how to use platform specific classes.
     The use case that inspired this feature was Facebook login on iOS, which is
     different than for a desktop.  So we needed a different page object for iOS.
     In this case env.py:Local_FF_SeMixin has PLATFORM_SUFFIX set to 'FF' so
     if you run with browser Local_FF enabled it will create this page object (noted
     in the logs) but any other browser will just create the general ArticlePage above.
  '''
  pass


# See docs for: Add a new page class
class MobileArticlePage(ArticlePage):
  def _prep_finders(self):
    ArticlePage._prep_finders(self)
    self.verify_element = self.by_css('.section_heading')
  