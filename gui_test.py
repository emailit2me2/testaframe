
# -*- coding: utf-8 -*-

import traceback
#import random
#import datetime
#import urllib
import urlparse
import urllib2
import requests

#from nose.tools import eq_,ok_
from nose.plugins.attrib import attr
from nose.plugins.skip import SkipTest

from gui_pages import *

from base_tst import *

from databuilder import *

# caller() is for use by try_is_*() asserts since the value should not be evaluate
#   try_is_equal(10, func(x,y))
# will only evaluate func() once.  But an ajaxy app needs to keep rechecking.
# It is possible that lambda's will work in this capacity too but there might
# be issues with Skipped tests.  TODO find out if lambda obsoletes this.
#    try_is_equal(10, lambda: func(x,y))
#
def caller(func, *args):
  print func, args
  for i in xrange(TestMyGui.TRIES):
    try:
      y = func(*args)
    except SkipTest:
      print "    Skipping test from caller()"
      raise
    except:
      traceback.print_exc()
      y = None  # TODO returning None is dangerous since it could be a valid value
    #
    yield y
  #


@attr('MyProject','Gui')
class MyTestBase(GuiTestCaseBase):
  TRIES = 10

  def setUp(self):
    self.env_prep_for_se()

  def tearDown(self):
    self.env_teardown()

  def execute_js_on(self, page):
    print "Executing my js for %s" % self.env_sut_host()
    page.execute_javascript(self.env_get_my_js())


class TestMyGui(MyTestBase):
  # These tests use the test pages from the selenium repo
  # Clone the selenium repo locally
  # cd to selenium/common/src/web
  # then start a simple http server using
  #   python -m SimpleHTTPServer 8000
  # then run these tests.  Add the -s option to see the logs.
  @attr("Example","Ajax")
  def test_ajaxy(self):
    ajaxy_page = self.start.at(AjaxyPage)
    new_label1 = self.data.uniq_comment()['stripped_comment']
    ajaxy_page.fillout_form(new_label1)
    ajaxy_page.submit_fillout_form()
    self.try_is_equal(new_label1, ajaxy_page.new_labels.the_text)

    new_label2 = self.data.uniq_comment()['stripped_comment']
    ajaxy_page.fillout_form(new_label2)
    ajaxy_page.submit_fillout_form()
    # you need to pass functions or lambdas to try_is_* if they need to be reevaluated
    # For instance if you change the following line to end with
    #    .all_the_text())
    # then python will call all_the_text before it calls try_is_equal and the test
    # will fail because the value will not change when the new label appears in the DOM.
    self.try_is_equal([new_label1,new_label2], ajaxy_page.new_labels.all_the_text)

    # A couple things to note in the logs.
    # The first try_is_equal calls .the_text and fails initially because there are
    # no .label elements in the DOM yet.  The second try_is_equal fails because
    # the expected and actual values are not yet equal.

