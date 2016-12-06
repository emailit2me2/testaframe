
"""Page classes for things common across all project pages.

"""
from pages.base_page import BaseForm, BasePage

import config.our_envs

# There should never be any asserts in pages
# All asserts should be in the tests.

class UnexpectedStateError(Exception):
    pass

class StdForm(BaseForm):

    def _prep_finders(self):
        pass


class StdPage(BasePage):

    IS_STATE_SUPPORTED = False

    def _prep_finders(self):
        pass

    def now_on(self, page_class, params='', substitutions=(), **args_for_page):
        new_page = BasePage.now_on(self, page_class, params, substitutions, **args_for_page)

        # Set the appropriate login state
        from pages.wiki_state_component import LoginStateComponentSelector, LoginStateComponentBase
        
        is_logged_in = False
        if LoginStateComponentBase.ID in self.components:
            is_logged_in = self.components[LoginStateComponentBase.ID].is_logged_in

        new_page.now_showing_component(
            LoginStateComponentSelector.get_appropriate_login_component(
                is_logged_in,
                fake=not new_page.IS_STATE_SUPPORTED))

        return new_page


class StdStatefulPage(StdPage):
    IS_STATE_SUPPORTED = True

    def _prep_finders(self):
        StdPage._prep_finders(self)

    def goto_login(self):
        from pages.wiki_state_component import LoginStateComponentBase
        login_component = self.components[LoginStateComponentBase.ID]
        if not login_component.is_logged_in:
            logged_in_page = login_component.goto_login()
            return logged_in_page
        else:
            raise UnexpectedStateError("The login link is not available in this state.")

    def goto_logout(self):
        from pages.wiki_state_component import LoginStateComponentBase
        login_component = self.components[LoginStateComponentBase.ID]
        if login_component.is_logged_in:
            login_component.is_logged_in = False
            logged_out_page = login_component.goto_logout()
            return logged_out_page
        else:
            raise UnexpectedStateError("The logout link is not available in this state.")
