
# -*- coding: utf-8 -*-

from nose.plugins.attrib import attr

from wiki_pages import *

from base_tst import *

from databuilder import *

@attr('Wiki')
class WikiTestBase(GuiTestCaseBase):
  def setUp(self):
    self.env_prep_for_se()
    GuiTestCaseBase.setUp(self)
  def tearDown(self):
    self.env_teardown()

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