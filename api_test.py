

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
    geo_location = self.svc.api('4.2.2.4')
    self.is_in('ip', geo_location.keys)

class TestAsserts(StdApiTestBase):
  def test_in_order(self):
    inc = [1,2,3]
    dec = [10,9,9,5]
    incs = ['1','2','4']
    decs = ['10','9','7']

    self.try_is_in_order_inc(inc)
    self.try_is_in_order_dec(dec)
    self.try_is_in_order_inc(incs, lambda a,b: cmp(int(a),int(b)))
    self.try_is_in_order_dec(decs, lambda a,b: cmp(int(a),int(b)))
    #self.try_is_in_order_inc(dec)
    #self.try_is_in_order_dec(inc)
    self.try_is_gt_all(11, dec)
    self.try_is_lt_all(4, dec)
    self.try_is_ge_all(10, dec)
    self.try_is_le_all(5, dec)

