

from nose.plugins.attrib import attr
import test_gui.std_tst


@attr('Api')
class EmailTestBase(test_gui.std_tst.StdApiTestBase):

    def setUp(self):
        test_gui.std_tst.StdApiTestBase.setUp(self)
        self.email_svc = self.svc_factory.make_email_svc()

    def tearDown(self):
        test_gui.std_tst.StdApiTestBase.tearDown(self)


@attr("GMail")
class TestEmail(EmailTestBase):
    """Simple email test to show how it works
    """

    def test_simple_email_query(self):
        # lame example but likely some in everyone's inbox
        contains = 'Unsubscribe'  

        were_any_found = self.email_svc.find_emails_with_body_containing(contains)

        self.is_equal(True, were_any_found)

