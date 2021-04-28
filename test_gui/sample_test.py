
# -*- coding: utf-8 -*-

from data.databuilder import *
from nose.plugins.attrib import attr
from nose.plugins.skip import SkipTest
from pages.sample_pages import *
from test_gui.std_tst import *


@attr('Sample')
class SampleTestBase(StdGuiTestBase):

    def setUp(self):
        StdGuiTestBase.setUp(self)
        self.example_db = self.db_factory.make_example_db()

    def tearDown(self):
        StdGuiTestBase.tearDown(self)


class TestSeGui(SampleTestBase):
    # These tests use the test pages from the selenium repo
    # Clone the selenium repo locally
    # cd to selenium/common/src/web
    # then start a simple http server using
    #   python -m SimpleHTTPServer 8000
    # then run these tests.  Add the -s option to see the logs.

    # See docs for: How to read log output containing polling
    # See docs for: Asserts, polling and non-polling
    @attr("Example", "Ajax")
    def test_ajaxy(self):
        ajaxy_page = self.start.at(AjaxyPage)
        new_label1 = self.data.uniq_comment()['stripped_comment']
        ajaxy_page.fillout_form(new_label1)
        ajaxy_page.submit_fillout_form()
        # The assert has to check several times while waiting for the page, so blink quickly
        # and this is also here as an example.  See also my_cfg.py HIGHLIGHT_DELAY option
        self.start.set_highlight_delay(1)
        self.try_is_equal(new_label1, ajaxy_page.new_labels.the_text)
        self.start.set_highlight_delay()  # set delay back to default.
        # set_poll_max() and set_poll_delay() use this same idiom.

        new_label2 = self.data.uniq_comment()['stripped_comment']
        ajaxy_page.fillout_form(new_label2)
        ajaxy_page.submit_fillout_form()
        # you need to pass functions or lambdas to try_is_* if they need to be reevaluated
        # For instance if you change the following line of code to end with
        #    .all_the_text())
        # then python will call all_the_text before it calls try_is_equal and the test
        # will fail because the value will not change when the new label appears in the DOM.
        self.try_is_equal([new_label1, new_label2], ajaxy_page.new_labels.all_the_text)

        # Use a lambda if you need to pass parameters (although this is a lame example)
        self.try_is_equal('label', lambda: ajaxy_page.new_labels.the_attribute('class'))

        # A couple things to note in the logs.
        # The first try_is_equal calls .the_text and fails initially because there are
        # no .label elements in the DOM yet.  The second try_is_equal fails initially because
        # the expected and actual values are not yet equal.

    @attr("Example", "Alerts")
    def test_alerts(self):
        alerts_page = self.start.at(AlertsPage)
        alerts_page.do_alert()

    @attr("Example", "DataBase")
    def test_queries(self):
        results = self.example_db.get_employees()
        print(results)

        self.example_db.dump_db()
