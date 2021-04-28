

import itertools

from nose.plugins.attrib import attr
from nose.tools import assert_raises

import test_gui.base_tst


@attr('SelfTest')
class MySelfTestBase(test_gui.base_tst.TestCaseBase):

    def setUp(self):
        test_gui.base_tst.TestCaseBase.setUp(self)

    def tearDown(self):
        test_gui.base_tst.TestCaseBase.tearDown(self)


class TestSelf(MySelfTestBase):

    def setUp(self):
        MySelfTestBase.setUp(self)
        self.set_poll_max(0.1)
        self.set_poll_delay(0.01)

    def yieldor(self, lst):
        for item in lst:
            yield item

    def test_is_equal_true(self):
        an_int = 3
        a_string = '3'
        list_of_ints = [3,5]
        list_of_strings=['c','z']
        a_dict = {3:5, 'c':'z'}

        works = [(None,None),(an_int,an_int),(a_string,a_string),(list_of_ints,list_of_ints),
                 (list_of_ints,list(list_of_ints)),(list_of_strings,list_of_strings),
                 (list_of_strings,list(list_of_strings)),(a_dict,a_dict),(a_dict,dict(a_dict)),
                 (an_int, lambda: an_int),(a_string, lambda: a_string),(list_of_ints, lambda: list_of_ints),
                 (list_of_strings, lambda: list_of_strings),(a_dict, lambda: a_dict),
                 (an_int, itertools.chain([an_int])),(a_string, itertools.chain([a_string])),
                 (list_of_ints, itertools.chain([list_of_ints])),
                 (list_of_strings, itertools.chain([list_of_strings])),(a_dict, itertools.chain([a_dict])),
                 (an_int, self.yieldor([an_int])),
                ]

        for (a,b) in works:
            yield self.is_equal, a, b


    def _check_assert_fails(self, to_call, a, b):
        with assert_raises(AssertionError) as cm:
            to_call(self, a, b)

    def test_is_equal_false(self):
        an_int = 3
        a_string = '3'
        list_of_ints = [3,5]
        list_of_strings=['c','z']
        lt = tuple(list_of_strings)
        a_dict = {3:5, 'c':'z'}

        fails = [(an_int,a_string), (list_of_strings,lt),(list_of_ints,list_of_strings),
                 (an_int,lambda: a_string),(a_string,lambda: list_of_ints),(list_of_strings,lambda: lt),
                 (an_int, itertools.chain([a_string])),(a_dict, itertools.chain([list_of_ints])),
                ]

        for (a,b) in fails:
            #yield self._check_assert_fails, self.is_equal, a, b  # This won't work for failure cases. idk why not.
            yield self._check_assert_fails, TestSelf.is_equal, a, b  # So have to do it this way


    def test_try_is_equal_true(self):
        an_int = 3
        a_string = '3'
        list_of_ints = [3,5]
        list_of_strings=['c','z']
        a_dict = {3:5, 'c':'z'}

        works = [(None,None),(an_int,an_int),(a_string,a_string),(list_of_ints,list_of_ints),
                 (list_of_ints,list(list_of_ints)),(list_of_strings,list_of_strings),
                 (list_of_strings,list(list_of_strings)),(a_dict,a_dict),(a_dict,dict(a_dict)),
                 (an_int, lambda: an_int),(a_string, lambda: a_string),(list_of_ints, lambda: list_of_ints),
                 (list_of_strings, lambda: list_of_strings),(a_dict, lambda: a_dict),
                 (lambda: an_int, an_int),(lambda: a_string, a_string),(lambda: list_of_ints, list_of_ints),
                 (lambda: list_of_strings, list_of_strings),(lambda: a_dict, a_dict),
                 (lambda: an_int, lambda: an_int),(lambda: a_string, lambda: a_string),
                 (lambda: list_of_ints, lambda: list_of_ints),(lambda: list_of_strings, lambda: list_of_strings),
                 (lambda: a_dict, lambda: a_dict),
                 (an_int, itertools.chain([an_int])),(a_string, itertools.chain([a_string])),
                 (list_of_ints, itertools.chain([list_of_ints])),
                 (list_of_strings, itertools.chain([list_of_strings])),(a_dict, itertools.chain([a_dict])),
                ]

        for (a,b) in works:
            yield self.try_is_equal, a, b

    def test_try_is_equal_true_eventually_val_callable(self):
        an_int = 3
        iv = [an_int, 9,99,999]
        self.try_is_equal(an_int, lambda: iv.pop())

    def test_try_is_equal_true_eventually_callable_val(self):
        an_int = 3
        iv = [an_int, 9,99,999]
        self.try_is_equal(lambda: iv.pop(), an_int)

    def test_try_is_equal_true_eventually_callable_callable(self):
        an_int = 3
        iv = [an_int, 9,99,999]
        iv2 = [an_int, 8, 88, 888]
        self.try_is_equal(lambda: iv2.pop(), lambda: iv.pop())

    def test_try_is_equal_true_eventually_val_iter(self):
        an_int = 3
        iv = [9,99,999, an_int]
        self.try_is_equal(an_int, itertools.chain(iv))

    def test_try_is_equal_true_eventually_iter_val(self):
        an_int = 3
        iv = [9,99,999, an_int]
        self.try_is_equal(itertools.chain(iv), an_int)

    def test_try_is_equal_true_eventually_iter_iter(self):
        an_int = 3
        iv = [9,99,999, an_int]
        iv2 = [8, 88, 888, an_int]
        self.try_is_equal(itertools.chain(iv2), itertools.chain(iv))

    def test_try_is_equal_false(self):
        an_int = 3
        a_string = '3'
        list_of_ints = [3,5]
        list_of_strings=['c','z']
        lt = tuple(list_of_strings)
        a_dict = {3:5, 'c':'z'}

        fails = [(an_int,a_string),(list_of_strings,lt),(list_of_ints,list_of_strings),
                 (an_int,lambda: a_string),(a_string,lambda: list_of_ints),(list_of_strings,lambda: lt),
                 (lambda: an_int, a_string),(lambda: a_string, list_of_ints),(lambda: list_of_strings, lt),
                 (lambda: an_int,lambda: a_string),(lambda: a_string,lambda: list_of_ints),
                 (lambda: list_of_strings,lambda: lt),
                 (an_int, itertools.cycle([a_string])),##(a_string, itertools.cycle([list_of_ints])),(list_of_strings, itertools.cycle([lt])),
                ]

        for (a,b) in fails:
            #yield self._check_assert_fails, self.is_equal, a, b  # This won't work for failure cases. idk why not.
            yield self._check_assert_fails, TestSelf.try_is_equal, a, b  # So have to do it this way

    def test_is_subset_pass(self):
        l1 = [3,5]
        l2 = [7,5,3,1]
        s1 = "ac"
        s2 = "abcde"
        works = [(l1,l2),(l1,lambda : l2), (s1,s2),
                ]
        for (a,b) in works:
            yield self.is_subset, a, b

    def test_try_is_subset_pass(self):
        l1 = [3,5]
        l2 = [7,5,3,1]
        s1 = "ac"
        s2 = "abcde"
        works = [(l1,l2),(l1,lambda : l2),(lambda:l1, l2),(lambda:l1, lambda:l2),
                 (s1,s2),(s1,lambda : s2),(lambda:s1, s2),(lambda:s1, lambda:s2),
                ]
        for (a,b) in works:
            yield self.try_is_subset, a, b

    def test_is_subset_false(self):
        an_int = [3,]
        a_string = ['3',]
        list_of_ints = [3,5]
        list_of_strings=['c','z']

        fails = [(an_int,a_string),(a_string,list_of_ints),(a_string,list_of_strings),
                ]
        for (a,b) in fails:
            yield self._check_assert_fails, TestSelf.is_subset, a, b  # So have to do it this way
            yield self._check_assert_fails, TestSelf.try_is_subset, a, b  # So have to do it this way


    def test_is_set_equal_pass(self):
        l1 = [3,5]
        l2 = [5,3]
        s1 = "ac"
        s2 = "ca"
        works = [(l1,l2),(l1,lambda : l2), (s1,s2),
                ]
        for (a,b) in works:
            yield self.is_subset, a, b

    def test_try_is_set_equal_pass(self):
        l1 = [3,5]
        l2 = [5,3]
        s1 = "ac"
        s2 = "ca"
        works = [(l1,l2),(l1,lambda : l2),(lambda:l1, l2),(lambda:l1, lambda:l2),
                 (s1,s2),(s1,lambda : s2),(lambda:s1, s2),(lambda:s1, lambda:s2),
                ]
        for (a,b) in works:
            yield self.try_is_subset, a, b

    def test_is_set_equal_false(self):
        an_int = [3,]
        a_string = ['3',]
        list_of_ints = [3,5]
        list_of_strings=['c','z']
        a_dict = {3:5, 'c':'z'}

        fails = [(an_int,a_string),(list_of_ints, a_dict),(a_string,list_of_strings),
                ]
        for (a,b) in fails:
            yield self._check_assert_fails, TestSelf.is_subset, a, b  # So have to do it this way
            yield self._check_assert_fails, TestSelf.try_is_subset, a, b  # So have to do it this way


    def test_in_order(self):
        inc = [1, 2, 3]
        dec = [10, 9, 9, 5]
        incs = ['1', '2', '4']
        decs = ['10', '9', '7']

        self.is_in_order_inc(inc)
        self.is_in_order_dec(dec)
        self.try_is_in_order_inc(inc)
        self.try_is_in_order_dec(dec)
        self.is_in_order_inc(incs, lambda a: int(a))
        self.is_in_order_dec(decs, lambda a: int(a))
        self.try_is_in_order_inc(incs, lambda a: int(a))
        self.try_is_in_order_dec(decs, lambda a: int(a))
        self.try_is_gt_all(11, dec)
        self.try_is_lt_all(4, dec)
        self.try_is_ge_all(10, dec)
        self.try_is_le_all(5, dec)


    def test_set_asserts(self):
        vals = [1, 2, 3]
        self.try_is_subset(vals, vals)
        self.try_is_subset(vals[1:], vals)
        self.try_is_subset(vals[:-1], vals)
        self.try_is_set_equal(vals, vals)
        self.try_is_set_equal(vals, list(reversed(vals)))
        self.try_is_set_equal(set(vals), vals)

    def test_not_in(self):
        self.is_not_in('the key', {})
        self.is_not_in('b', 'hairy')
        self.is_not_in('item', ['items', 'plural', 'here'])


