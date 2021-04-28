
import sys
import time

import config.our_envs
from .std_pages import StdPage

# There should never be any asserts in pages
# All asserts should be in the tests.


class StdSamplePage(StdPage):
    def _prep_finders(self):
        pass


class AjaxyPage(StdSamplePage):
    HOST_ENUM = config.our_envs.Host.SAMPLE
    PAGE = "/ajaxy_page.html"

    def _prep_finders(self):
        StdSamplePage._prep_finders(self)
        self.verify_element = self.by_css('#update_butter')
        # Every page needs a unique verify element to make sure we are on the correct page
        self.new_label_field = self.by_name('typer')
        self.new_label_form = self.by_css('form')  # forms should have ID's for real code
        self.new_labels = self.by_css('.label')
        # setting log_type_into=False suppresses printing of the passed in text
        self.password_field = self.by_css('#input-password', log_type_into=False)  # suppresses

    def fillout_form(self, new_label):
        self.type_into(self.new_label_field, new_label)

    # It is common to split filling out a form and submitting a form so you can test error cases
    # in form validation.
    def submit_fillout_form(self):
        self.submit_form(self.new_label_form)

    # For optional form fields, or to test missed fields, make a parameter default to None and
    # then add an if around the filling out part.
    def fake_fillout_login_form(self, username=None, password=None):
        if username:
            self.type_into(self.username_field, username)
        if password:
            self.type_into(self.password_field, password)


class AlertsPage(StdSamplePage):
    HOST_ENUM = config.our_envs.Host.SAMPLE
    PAGE = "/alerts.html"

    def _prep_finders(self):
        StdSamplePage._prep_finders(self)
        self.verify_element = self.alert_link = self.by_css('#alert')

    def do_alert(self):
        self.click_on(self.alert_link)
        alert_dialog = self.get_alert()
        alert_dialog.choose_accept()
