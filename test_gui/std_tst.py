
from nose.plugins.attrib import attr

from base_tst import *

@attr('Api')
class StdApiTestBase(TestCaseBase):
  def setUp(self):
    self.env_prep_for_svc()
    TestCaseBase.setUp(self)


@attr('Gui')
class StdGuiTestBase(GuiTestCaseBase):
  pass
  def setUp(self):
    self.env_prep_for_se()
    GuiTestCaseBase.setUp(self)
  def tearDown(self):
    self.env_teardown()
    GuiTestCaseBase.tearDown(self)


