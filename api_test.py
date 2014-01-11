

from nose.plugins.attrib import attr

from std_tst import *

from databuilder import *

class GeoIPApiTestBase(StdApiTestBase):
  pass
#  def setUp(self):
#    pass  # might need something here
#
#  def tearDown(self):
#    pass  # shouldn't need a teardown for API tests


@attr("GeoIP")
class TestMyApi(GeoIPApiTestBase):
  def test_api(self):
    # Using FreeGeoIP service as a example
    geo_location = self.svc.json()
    self.is_in('ip', geo_location.keys)
