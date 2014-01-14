
# -*- coding: utf-8 -*-

from nose.plugins.attrib import attr

from wiki_pages import *

from std_tst import *

from databuilder import *

@attr('Wiki')
class WikiTestBase(StdGuiTestBase):
  def setUp(self):
    StdGuiTestBase.setUp(self)
  def tearDown(self):
    StdGuiTestBase.tearDown(self)

  def execute_js_on(self, page):
    # for use with bookmarklets
    print "Executing my js for %s" % self.env_sut_host()
    page.execute_javascript(self.env_get_my_js())


class TestWikiGui(WikiTestBase):
  @attr("Example",'Article')
  def test_wikipedia(self):
    article_to_use = 'YAML'
    article_page = self.start.at(ArticlePage, substitutions=(article_to_use))
    self.is_in(article_to_use, article_page.get_title)
    # See docs for: Add a locator to a page
    self.is_equal(True, article_page.powered_by_link.is_this_displayed)


  # See docs for: Add another test case to an existing test class
  @attr("Example",'Article')
  def test_article_with_parens(self):
    article_to_use = 'Python_(programming_language)'
    article_title = article_to_use.replace('_',' ')
    article_page = self.start.at(ArticlePage, substitutions=(article_to_use))
    self.is_in(article_title, article_page.get_title)

  @attr("Example",'Article','Search')
  def test_search_success(self):
    article_to_use = 'YAML'
    article_page = self.start.at(ArticlePage, substitutions=(article_to_use))
    self.is_equal(True, article_page.powered_by_link.is_this_displayed)
    # See docs  for: Add a function to a page
    search_term = 'XML'
    new_article_page = article_page.do_search(search_term)
    self.is_in(search_term, new_article_page.get_title)


  # See docs for: Add a new page class
  @attr("Example",'Article')
  def test_goto_mobile_view(self):
    article_to_use = 'YAML'
    article_page = self.start.at(ArticlePage, substitutions=(article_to_use))
    self.is_in(article_to_use, article_page.get_title)
    mobile_page = article_page.goto_mobile_view()


