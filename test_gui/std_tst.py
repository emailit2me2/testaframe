
from nose.plugins.attrib import attr

from . import base_tst

import services.svc_factory


@attr('Api')
class StdApiTestBase(base_tst.TestCaseBase):

    def setUp(self):
        base_tst.TestCaseBase.setUp(self)
        print("Setup ^^^^^^^^^^^^^^^^^^^^^^^^")

    def tearDown(self):
        print("Teardown vvvvvvvvvvvvvvvvvvvvv")
        base_tst.TestCaseBase.tearDown(self)


@attr('Gui')
class StdGuiTestBase(base_tst.GuiTestCaseBase):

    def setUp(self):
        base_tst.GuiTestCaseBase.setUp(self)
        print("Setup ^^^^^^^^^^^^^^^^^^^^^^^^")

    def tearDown(self):
        print("Teardown vvvvvvvvvvvvvvvvvvvvv")
        base_tst.GuiTestCaseBase.tearDown(self)


class StdGuiStandAloneBase(base_tst.AutomationBase):
        pass
