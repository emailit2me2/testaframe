"""Test our urlutils"""

from utilities import urlutils

from nose.tools import eq_


class TestJoin(object):

    def test_join(self):
        eq_(urlutils.join('http://example.com/path', 'end'), 'http://example.com/path/end')

    def test_join_no_double_slashes(self):
        eq_(urlutils.join('http://example.com/', '/path'), 'http://example.com/path')


class TestRootDomain(object):

    def test_get_root_domain(self):
        # test.uk.com is a public suffix
        eq_(urlutils.get_root_domain('test.uk.com'), 'test.uk.com')
        eq_(urlutils.get_root_domain('host.test.uk.com'), 'test.uk.com')
        eq_(urlutils.get_root_domain('sub.host.test.uk.com'), 'test.uk.com')
