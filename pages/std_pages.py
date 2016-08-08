
"""Page classes for things common across all project pages.

"""
from pages.base_page import BaseForm, BasePage

import config.our_envs

# There should never be any asserts in pages
# All asserts should be in the tests.


class StdForm(BaseForm):

    def _prep_finders(self):
        pass


class StdPage(BasePage):

    def _prep_finders(self):
        pass

    def now_on(self, page_class, params='', substitutions=(), **args_for_page):
        new_page = BasePage.now_on(self, page_class, params, substitutions, **args_for_page)
        return new_page
