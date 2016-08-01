
from base_page import BasePage

# There should never be any asserts in pages
# All asserts should be in the tests.

class StdPage(BasePage):
  LOGIN_LINK_TEXT = 'Log In'
  def _prep_finders(self):
    pass
