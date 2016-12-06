
import config.our_envs
from std_pages import StdPage, StdStatefulPage

# There should never be any asserts in pages
# All asserts should be in the tests.


class WikiHomePage(StdPage):
    HOST_ENUM = config.our_envs.Host.WIKIPEDIA
    PAGE = "/"

    def _prep_finders(self):
        StdPage._prep_finders(self)
        self.verify_element = self.by_css('#www-wikipedia-org')
        self.english_link = self.by_css('a#js-link-box-en')

    def goto_english(self):
        self.click_on(self.english_link)
        return self.now_on(ArticlePage)


# example page object for a wikipedia.org article
class ArticlePage(StdStatefulPage):
    HOST_ENUM = config.our_envs.Host.WIKIPEDIA
    # Every page needs a PAGE (or PAGE_SUB) or PAGE_RE (the _RE stands for regular expression,
    # like the re module) value to make sure the page URL is correct in verify_on_page().
    # If no PAGE_RE exists PAGE will be converted into one.
    PAGE_RE = "^/wiki/.*$"
    PAGE_SUB = "/wiki/%s"  # A PAGE_SUB creates a PAGE using python's % operator
    MOBILE_VIEW_LINK_TEXT = 'Mobile view'

    def _prep_finders(self):
        StdStatefulPage._prep_finders(self)
        self.verify_element = self.by_css('.mw-wiki-logo')
        # See docs for: Add a new page class

        # See docs for: Add a locator to a page
        self.powered_by_link = self.by_css('#footer-poweredbyico a')
        self.mobile_view_link = self.by_link_text(self.MOBILE_VIEW_LINK_TEXT)
        self.search_input = self.by_css('#searchInput')
        self.search_form = self.by_css('#searchform')
        self.close_fundraising_link = self.by_css('#frbanner-close')

    def on_load(self):
        if self.can_find_the(self.close_fundraising_link):
            self.click_on(self.close_fundraising_link)

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
    DESKTOP_LINK_TEXT = "Desktop"

    def _prep_finders(self):
        ArticlePage._prep_finders(self)
        self.verify_element = self.by_link_text(self.DESKTOP_LINK_TEXT)


class WikiIndexBasePage(StdStatefulPage):
    HOST_ENUM = config.our_envs.Host.WIKIPEDIA

    PAGE = "/w/index.php"

    def _prep_finders(self):
        StdStatefulPage._prep_finders(self)

class WikiLoginPage(WikiIndexBasePage):

    def _prep_finders(self):
        WikiIndexBasePage._prep_finders(self)
        self.login_form = self.by_css('form[name="userlogin"]')
        self.verify_element = self.login_form
        self.name_field = self.by_css("#wpName1")
        self.password_field = self.by_css("#wpPassword1")

    def do_login(self, username, password):
        self.type_into(self.name_field, username)
        self.type_into(self.password_field, password)
        self.submit_form(self.login_form)

        from pages.wiki_state_component import LoginStateComponentBase
        self.components[LoginStateComponentBase.ID].is_logged_in = True

        return self.now_on(ArticlePage)


class WikiLogoutPage(WikiIndexBasePage):

    def _prep_finders(self):
        WikiIndexBasePage._prep_finders(self)
        self.verify_element = self.by_css('body.page-Special_UserLogout')
