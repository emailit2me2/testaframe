

from nose.tools import eq_,ok_
from nose.plugins.attrib import attr

from base_tst import *

from databuilder import *

@attr('Api')
class MyApiTestBase(TestCaseBase):

  def setUp(self):
    self.env_prep_for_svc()

  def tearDown(self):
    pass  # shouldn't need a teardown for API tests


class TestMyApi(MyApiTestBase):
  @attr("Example")
  def test_api(self):
    # Using FreeGeoIP service as a example
    geo_location = self.svc.json()
    self.is_in('ip', geo_location.keys)