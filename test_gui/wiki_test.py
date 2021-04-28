
# -*- coding: utf-8 -*-

from data.databuilder import *
from nose.plugins.attrib import attr
from pages.wiki_pages import *
from .std_tst import *


@attr('Wiki')
class WikiTestBase(StdGuiTestBase):
    def setUp(self):
        StdGuiTestBase.setUp(self)

    def tearDown(self):
        StdGuiTestBase.tearDown(self)

    def execute_js_on(self, page):
        # for use with bookmarklets
        print("Executing my js for %s" % self.env_sut_host())
        page.execute_javascript(self.env_get_my_js())


class TestWikiGui(WikiTestBase):
    @attr("Example", 'Article')
    def test_wikipedia(self):
        article_to_use = 'YAML'
        article_page = self.start.at(ArticlePage, substitutions=(article_to_use))
        self.is_in(article_to_use, article_page.get_title)
        # See docs for: Add a locator to a page
        self.is_equal(True, article_page.powered_by_link.is_this_displayed)
        # See docs for: How to read log output containing failures
        # Uncomment one or the other of the lines of code below to force the demo errors
        # force an assert failure
        # self.is_in(article_to_use+'-FORCE FAILURE FOR DEMO PURPOSES', article_page.get_title)
        # force a coding error
        # self.is_in(article_to_use, article_page.FAIL_CUZ_THIS_FUNCTION_DOES_NOT_EXIST)

    # See docs for: Add another test case to an existing test class
    @attr("Example", 'Article')
    def test_article_with_parens(self):
        article_to_use = 'Python_(programming_language)'
        article_title = article_to_use.replace('_', ' ')
        article_page = self.start.at(ArticlePage, substitutions=(article_to_use))
        self.is_in(article_title, article_page.get_title)

    @attr("Example", 'Article', 'Search', 'Generator')
    def test_search_success(self):
        # An example of a generator test.
        articles = ['YAML', 'JSON']
        for article in articles:
            yield self._check_search_success, article

    def _check_search_success(self, article_to_use):
        '''This can't have the word test in the name or Nose will auto-duiscover it.'''
        self.set_value_attributes(ArticleName=article_to_use)
        article_page = self.start.at(ArticlePage, substitutions=(article_to_use))
        self.is_equal(True, article_page.powered_by_link.is_this_displayed)
        # See docs  for: Add a function to a page
        search_term = 'XML'
        new_article_page = article_page.do_search(search_term)
        self.is_in(search_term, new_article_page.get_title)

    # See docs for: Add a new page class
    @attr("Example", 'Article')
    def test_goto_mobile_view(self):
        article_to_use = 'YAML'
        article_page = self.start.at(ArticlePage, substitutions=(article_to_use))
        self.is_in(article_to_use, article_page.get_title)
        mobile_page = article_page.goto_mobile_view()

    @attr("Example", "Login")
    def test_login_logout(self):
        landing_page = self.start.at(WikiHomePage)
        main_page = landing_page.goto_english()
        login_page = main_page.goto_login()
        wiki_creds = self.env.get_credentials('wiki_creds')  # Make sure you provide these in my_cfg.py
        main_page = login_page.do_login(wiki_creds['user'], wiki_creds['password'])
        logout_page = main_page.goto_logout()
