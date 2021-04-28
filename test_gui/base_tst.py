
"""Basic test classes with polling and non-polling asserts.
"""

import time

# remote selenium is too chatty by default
import logging
l = logging.getLogger('selenium.webdriver.remote.remote_connection')
l.setLevel(logging.INFO)

import traceback
import sys

import pprint

from enum import Enum

from nose.tools import ok_
from nose.plugins.attrib import attr
from nose.plugins.skip import SkipTest

from selenium.common.exceptions import WebDriverException, StaleElementReferenceException

import config.my_cfg
from services.tracker_svc import TrackerSvc


class NullDriver(object):
    def quit(self):
        pass


class NullBrowser():
    def __init__(self):
        self.driver = NullDriver()


class AutomationBase(object):

    """Base class for use in all automation, regardless of execution."""

    # Test environment
    ENV = None
    OS_BROWSER = None

    # Automation Mode
    class AutomationMode(Enum):
        NONE = 0
        API = 1
        GUI = 2

    AUTO_MODE = AutomationMode.NONE

    NOT_CALLABLE_TEXT = "not callable"
    LAMBDA_TEXT = "lambda"  # in_order calls pass a lambda as actual arg.

    _TIME_TO_WAIT = 20  # default value
    _POLLING_DELAY = 0.1  # default value

    def __init__(self):
        self.default_poll_max = self._TIME_TO_WAIT
        self.poll_delay = 0
        self.default_poll_delay = self._POLLING_DELAY

        # Adding initialization for PEP-8
        self.data = None
        self.db_factory = None
        self.env = None
        self.os_browser = None
        self.start = None
        self.svc_factory = None

    def setUp(self):
        self.start = None
        self.default_poll_max = self._TIME_TO_WAIT
        self.set_poll_max(self.default_poll_max)
        self.default_poll_delay = self._POLLING_DELAY
        self.set_poll_delay(self.default_poll_delay)

        if self.AUTO_MODE is self.AutomationMode.NONE:
            print("WARNING: Automation Mode is unset. This should only be the case for Terminators.")

        try:
            self.prepare_tst_env(self.ENV, self.OS_BROWSER)

            # Set up environment
            self.init_environment()

        except Exception as exc:
            print(exc)
            try:
                if self.start.driver:
                    self.start.driver.quit()
                    # time.sleep(5) # getting Windows [32] error because process is not stopped, so lets wait a little
            except Exception as exc2:
                print(exc2)
            finally:
                raise exc
        # TODO do we really need a finally here, and if so what should it do?
        # finally:
        #     pass

    def set_automation_mode(self, mode):

        if mode is self.AutomationMode.GUI:
            self.start = self.os_browser.prep_for_se(self.env)
            self.start.poll_max = self.poll_max  # push it through for page object use
            self.start.poll_delay = self.poll_delay  # push it through for page object use
            self.start.avoid_where_hangs = config.my_cfg.config.get('AVOID_WHERE_HANGS', True)

    def setup_services(self):
        raise NotImplementedError("Must implement setup_services()")

    def setup_without_browser(self):
        '''Intended for use with test generators (i.e. those using yield)'''
        self.AUTO_MODE = self.AutomationMode.API
        self.prepare_tst_env(self.ENV, NullBrowser)
        self.init_environment()
        self.setup_services()

    def tearDown(self):
        try:
            self.print_attributes()  # at the end so tests, pages, and services can add them during the test
        except AssertionError:
            print("Warning: Failed to find test attributes. This may be because of the test generator")

        try:
            self.tracker.track(self.tracker.Record.SNAP, "teardown")

            if self.start:
                self.os_browser.teardown_for_se(self.find_automation_name())
        except:
            traceback.print_exc()
            raise
        finally:
            self.svc_factory.teardown_all()

        self.env.teardown_for_svc()

    def prepare_tst_env(self, env, os_browser):
        assert env is not None, "The system under test environment env must exist."
        assert os_browser is not None, "The Selenium OS and Browser combo os_browser must exist."
        self.env = env()
        self.os_browser = os_browser()

        self.set_automation_mode(self.AUTO_MODE)

    def init_environment(self):
        try:
            self.data = self.env.create_data_builder()
            self.svc_factory = self.env.prep_common_services(self.data, default_ident=str(self))
            self.db_factory = self.env.prep_common_databases()
            recorder_svc = self.svc_factory.make_recorder_svc(self)
            self.tracker = self.svc_factory.make_tracker(self, recorder_svc)

            if self.start:
                self.start.tracker = self.tracker
        except Exception as exc:
            traceback.print_exc()
            try:
                pass
            finally:
                raise exc

    def set_poll_max(self, poll_max=-1, message=''):
        """Set max polling delay or return to default."""
        if poll_max < 0:
            self.poll_max = self.default_poll_max
        else:
            self.poll_max = poll_max

        print("Setting poll max to %r %s" % (self.poll_max, message))

    def set_poll_delay(self, poll_delay=-1, message=''):
        """Set polling delay or return to default."""
        if poll_delay < 0:
            self.poll_delay = self.default_poll_delay
        else:
            self.poll_delay = poll_delay

        print("Setting poll delay to %r %s" % (self.poll_delay, message))

    @staticmethod
    def find_automation_shortname():
        assert False, "Must be defined by inheriting class."

    def find_automation_name(self):
        assert False, "Must be defined by inheriting class."

    def find_automation_func_name(self):
        assert False, "Must be defined by inheriting class."

    def find_automation_complete_name(self):
        assert False, "Must be defined by inheriting class."

    FILTERED_ATTRS = ('setUp', 'tearDown')
    VALUE_ATTRIBUTE = 'ValueAttribute'
    VALUE_ATTRIBUTE_LEN = len(VALUE_ATTRIBUTE)

    def set_value_attributes(self, **kwargs):
        '''Sometimes we need a value not just the attribute name (e.g. ProdSafe).
           Passing the key as a keyword arg forces it to be valid variable characters.
        '''
        for (k, v) in list(kwargs.items()):
            self.__dict__[self.VALUE_ATTRIBUTE + k] = v

    def print_attributes(self):
        print('test function name:', self.find_automation_name().split('.')[-1])
        for a in dir(self):
            # i.e. not mixed case
            if a[0] != '_' and not a.islower() and not a.isupper() and a not in self.FILTERED_ATTRS:
                if a.startswith(self.VALUE_ATTRIBUTE):
                    self.tracker.track(self.tracker.Record.ATTRIBUTE_CLASS_VALUE, a[self.VALUE_ATTRIBUTE_LEN:],
                                       self.__dict__[a])
                else:
                    self.tracker.track(self.tracker.Record.ATTRIBUTE_CLASS, a)
        for a in dir(getattr(self, self.find_automation_func_name())):
            # i.e. not mixed case
            if a[0] != '_' and not a.islower() and not a.isupper() and a not in self.FILTERED_ATTRS:
                if a.startswith(self.VALUE_ATTRIBUTE):
                    self.tracker.track(self.tracker.Record.ATTRIBUTE_FUNC_VALUE, a[self.VALUE_ATTRIBUTE_LEN:],
                                       self.__dict__[a])
                else:
                    self.tracker.track(self.tracker.Record.ATTRIBUTE_FUNC, a)

    def write(self, *args, **kwargs):
        """Write some info to the tracker"""
        self.tracker.track(self.tracker.Record.INFO, *args, **kwargs)

    def pprint(self, *stuff, **things):
        for item in stuff:
            pprint.pprint(item)
        for (name, value) in sorted(things.items()):
            print(name, "=")
            pprint.pprint(value)

    def wait(self, seconds, comment):
        """You shouldn't call C{sleep} in a test.  So call this so it is logged with a reason.

        You should be using events for synchronization to avoid flakey tests.
        """
        print("     !!! waiting %.1f second(s) because %s !!!" % (seconds, comment))
        time.sleep(seconds)

    def print_pass(self, msg):
        print("PASS: %s" % msg)
        self.tracker.track(self.tracker.Record.PASS, msg)

    def print_fail(self, msg):
        print("FAIL: %s" % msg)
        self.tracker.track(self.tracker.Record.FAIL, msg)

    def is_op(self, expected_val, operation, symbol, actual_val_or_gen_or_func, msg, only_if):
        """Base function for all the C{is_*} non-polling asserts.

        @param expected_val: What the result should be.
        @param operation: The comparision operation to perform.
        @param symbol: The symbol to display for the comparison operator
        @param actual_val_or_gen_or_func: The actual value, which can be a value, generator,
                                          or a callable function or lambda.
        @param msg: The optional assert explanation message to display in log messages.
        @param only_if: An optional check to see if the assert should even be performed.
                        This could be used to skip an assert if you are testing against Prod
                        or on a specific browser (e.g. Firefox on Windows).
        actual and expected params fail identically with a TypeError if you try to execute a value (e.g. an int)
            and if you call a function with a missing/typo'ed parameter. So look for "not callable"
            in the exception message which is the expected TypeError exception. Wish we had overloading.
        """
        if not only_if:
            print("  Skipping ?%s because only_if=%r\n" % (symbol, only_if,))
            return

        try:
            actual_val_or_gen = actual_val_or_gen_or_func()
        except TypeError as exc:
            if self.NOT_CALLABLE_TEXT not in str(exc) and self.LAMBDA_TEXT not in str(exc):
                raise exc
            # implied else
            actual_val_or_gen = actual_val_or_gen_or_func  # if it isn't callable that is OK
        #
        try:
            actual_val = next(actual_val_or_gen)
        except (AttributeError, TypeError):  # must just be a value
            actual_val = actual_val_or_gen
        #
        print("  %r: %r ?%s %r" % (operation(expected_val, actual_val), expected_val, symbol, actual_val))
        if msg:
            print(msg)

        try:
            fail_msg = "FAIL: %r not %s %r %s" % (expected_val, symbol, actual_val, msg)
            ret = ok_(operation(expected_val, actual_val), fail_msg)
        except Exception as exc:
            self.print_fail(fail_msg)
            raise
        #
        if msg == '':
            msg = "%r %s %r" % (expected_val, symbol, actual_val)
        self.print_pass(msg)
        return ret

    def try_is(self, expected_val_or_gen_or_func, operation, symbol, actual_val_or_gen_or_func, msg, only_if):
        """Base function for all the C{try_is_*} polling asserts.

        The try_is asserts are polling due to ajax.  Imagine clicking on the Follow
        button in twitter, then the # of followers should increment but the page doesn't reload.
        Also sometimes the element doesn't exist in the DOM yet.  So you have to wait for it to
        appear and then make sure it is correct.

        @param expected_val_or_gen_or_func: The expected value, which can be a value, generator,
                                            or a callable function or lambda.
        @param operation: The comparision operation to perform.
        @param symbol: The symbol to display for the comparison operator
        @param actual_val_or_gen_or_func: The actual value, which can be a value, generator,
                                          or a callable function or lambda.
        @param msg: The optional assert explanation message to display in log messages.
        @param only_if: An optional check to see if the assert should even be performed.
                        This could be used to skip an assert if you are testing against Prod
                        or on a specific browser (e.g. Firefox on Windows).
        actual and expected params fail identically with a TypeError if you try to execute a value (e.g. an int)
            and if you call a function with a missing/typo'ed parameter. So look for "not callable"
            in the exception message which is the expected TypeError exception. Wish we had overloading.

        """
        if not only_if:
            print("  Skipping ?%s because only_if=%r\n" % (symbol, only_if,))
            return

        self.tracker.track(self.tracker.Record.POLL_START, 'Try is')
        start = time.time()
        last_exc = None
        while time.time() - start < self.poll_max:
            try:
                try:
                    expected_val_or_gen = expected_val_or_gen_or_func()
                except TypeError as exc:
                    if self.NOT_CALLABLE_TEXT not in str(exc) and self.LAMBDA_TEXT not in str(exc):
                        last_exc = exc
                        raise exc
                    # implied else
                    expected_val_or_gen = expected_val_or_gen_or_func  # if it isn't callable that is OK
                #
                try:
                    actual_val_or_gen = actual_val_or_gen_or_func()
                except TypeError as exc:
                    if self.NOT_CALLABLE_TEXT not in str(exc) and self.LAMBDA_TEXT not in str(exc):
                        last_exc = exc
                        raise exc
                    # implied else
                    actual_val_or_gen = actual_val_or_gen_or_func  # if it isn't callable that is OK
                #
                try:
                    expected_val = next(expected_val_or_gen)
                except (AttributeError, TypeError):  # must just be a value
                    expected_val = expected_val_or_gen
                #
                try:
                    actual_val = next(actual_val_or_gen)
                except (AttributeError, TypeError):  # must just be a value
                    actual_val = actual_val_or_gen
                #
                print("-  %r: %r ?%s %r" % (operation(expected_val, actual_val), expected_val, symbol, actual_val))
                try:
                    fail_msg = "FAIL: %r not %s %r %s" % (expected_val, symbol, actual_val, msg)
                    ret = ok_(operation(expected_val, actual_val), fail_msg)
                except Exception as exc:
                    self.print_fail(fail_msg)
                    raise
                #

                if msg == '':
                    msg = "%r %s %r" % (expected_val, symbol, actual_val)
                self.print_pass(msg)
                self.tracker.track(self.tracker.Record.POLL_END, 'Try is')
                return ret
            except WebDriverException as exc:
                last_exc = exc
                print("  Waiting for element(s): %5.2fsecs" % (time.time() - start))
                time.sleep(self.poll_delay)
            except StaleElementReferenceException as exc:
                last_exc = exc
                print("  Stale element Exception: %5.2fsecs - %s" % ((time.time() - start), exc))
                time.sleep(self.poll_delay)
            except AssertionError as exc:
                last_exc = exc
                print("  Waiting for try_is(%s): %5.2fsecs" % (symbol, time.time() - start))
                time.sleep(self.poll_delay)
            except StopIteration as exc:
                last_exc = exc
                # once a generator raises an exception you can't call it again, so fail.
                print("  Strange Exception broke a generator")
                raise
            except SkipTest:
                print("  Skipping test from try_is()")
                raise
            except Exception as exc:
                last_exc = exc
                # catchall for any other things that might go wrong
                print("  General Exception: %5.2fsecs - %s" % ((time.time() - start), exc))
                time.sleep(self.poll_delay)
            #
            # TODO pull sleep out to here?
        # end while
        self.tracker.track(self.tracker.Record.POLL_END, 'Try is')
        raise last_exc

    def is_equal(self, expected, actual, msg='', only_if=True):
        self.is_op(expected, lambda expected, actual: expected == actual, '==', actual, msg, only_if)

    def is_not_equal(self, expected, actual, msg='', only_if=True):
        self.is_op(expected, lambda expected, actual: expected != actual, '!=', actual, msg, only_if)

    def is_lt(self, expected, actual, msg='', only_if=True):
        self.is_op(expected, lambda expected, actual: expected < actual, '<', actual, msg, only_if)

    def is_le(self, expected, actual, msg='', only_if=True):
        self.is_op(expected, lambda expected, actual: expected <= actual, '<=', actual, msg, only_if)

    def is_gt(self, expected, actual, msg='', only_if=True):
        self.is_op(expected, lambda expected, actual: expected > actual, '>', actual, msg, only_if)

    def is_ge(self, expected, actual, msg='', only_if=True):
        self.is_op(expected, lambda expected, actual: expected >= actual, '>=', actual, msg, only_if)

    def is_in(self, expected, actual, msg='', only_if=True):
        self.is_op(expected, lambda expected, actual: expected in actual, 'in', actual, msg, only_if)

    def is_not_in(self, expected, actual, msg='', only_if=True):
        self.is_op(expected, lambda expected, actual: expected not in actual, 'not in', actual, msg, only_if)

    def is_subset(self, expected, actual, msg='', only_if=True):
        self.is_op(expected, lambda expected, actual: set(expected).issubset(set(actual)),
                   'subset', actual, msg, only_if)

    def is_set_equal(self, expected, actual, msg='', only_if=True):
        self.is_op(expected, lambda expected, actual: set(expected) == set(actual), 'set ==', actual, msg, only_if)

    def is_in_order_inc(self, expected, actual=None, msg='', only_if=True):
        if actual:
            self.is_op(expected, lambda expected, actual: expected == sorted(expected, key=actual),
                   'in order inc', actual, msg, only_if)
        else:
            self.is_op(expected, lambda expected, actual: expected == sorted(expected),
                   'in order inc', actual, msg, only_if)

    def is_in_order_dec(self, expected, actual=None, msg='', only_if=True):
        if actual:
            self.is_op(expected, lambda expected, actual: expected == sorted(expected, key=actual, reverse=True),
                   'in order dec', actual, msg, only_if)
        else:
            self.is_op(expected, lambda expected, actual: expected == sorted(expected, reverse=True),
                   'in order dec', actual, msg, only_if)

    def try_is_equal(self, expected, actual, msg='', only_if=True):
        self.try_is(expected, lambda expected, actual: expected == actual, '==', actual, msg, only_if)

    def try_is_lt(self, expected, actual, msg='', only_if=True):
        self.try_is(expected, lambda expected, actual: expected < actual, '<', actual, msg, only_if)

    def try_is_le(self, expected, actual, msg='', only_if=True):
        self.try_is(expected, lambda expected, actual: expected <= actual, '<=', actual, msg, only_if)

    def try_is_gt(self, expected, actual, msg='', only_if=True):
        self.try_is(expected, lambda expected, actual: expected > actual, '>', actual, msg, only_if)

    def try_is_ge(self, expected, actual, msg='', only_if=True):
        self.try_is(expected, lambda expected, actual: expected >= actual, '>=', actual, msg, only_if)

    def try_is_lt_all(self, expected, actual, msg='', only_if=True):
        self.try_is(expected, lambda expected, actual: expected < min(actual), '<min', actual, msg, only_if)

    def try_is_le_all(self, expected, actual, msg='', only_if=True):
        self.try_is(expected, lambda expected, actual: expected <= min(actual), '<=min', actual, msg, only_if)

    def try_is_gt_all(self, expected, actual, msg='', only_if=True):
        self.try_is(expected, lambda expected, actual: expected > max(actual), '>max', actual, msg, only_if)

    def try_is_ge_all(self, expected, actual, msg='', only_if=True):
        self.try_is(expected, lambda expected, actual: expected >= max(actual), '>=max', actual, msg, only_if)

    def try_is_in(self, expected, actual, msg='', only_if=True):
        self.try_is(expected, lambda expected, actual: expected in actual, 'in', actual, msg, only_if)

    def try_is_not_in(self, expected, actual, msg='', only_if=True):
        self.try_is(expected, lambda expected, actual: expected not in actual, 'not in', actual, msg, only_if)

    def try_is_subset(self, expected, actual, msg='', only_if=True):
        self.try_is(expected, lambda expected, actual: set(expected).issubset(set(actual)),
                    'subset', actual, msg, only_if)

    def try_is_set_equal(self, expected, actual, msg='', only_if=True):
        self.try_is(expected, lambda expected, actual: set(expected) == set(actual), 'set ==', actual, msg, only_if)

    def try_is_in_order_inc(self, expected, actual=None, msg='', only_if=True):
        if actual:
            self.try_is(expected, lambda expected, actual: expected == sorted(expected, key=actual),
                    'in order inc', actual, msg, only_if)
        else:
            self.try_is(expected, lambda expected, actual: expected == sorted(expected),
                    'in order inc', actual, msg, only_if)

    def try_is_in_order_dec(self, expected, actual=None, msg='', only_if=True):
        if actual:
            self.try_is(expected, lambda expected, actual: expected == sorted(expected, key=actual, reverse=True),
                    'in order dec', actual, msg, only_if)
        else:
            self.try_is(expected, lambda expected, actual: expected == sorted(expected, reverse=True),
                    'in order dec', actual, msg, only_if)

    def dict_lookup(self, dct, lookup):
        """Convenience function for accessing data in deeply nested dictionaries.

        For example:
            >>> dct = {'a': {'b': {'c': 3}}}
            >>> TestCaseBase().dict_lookup(dct, 'a.b.c')
            3
        """
        for k in lookup.split('.'):
            dct = dct[k]
        return dct

    # TODO change from doctest to unittest style
    # TODO add wildcard option.  e.g. 'one.*.three' or maybe 'one..three'
    def dict_lookups(self, dct, *lookups):
        """Convenience function for accessing data in deeply nested dictionaries.

        For example:
            >>> dct = {'a': {'b': {'c1': 31, 'c2':32}}}
            >>> TestCaseBase().dict_lookups(dct, 'a.b.c1')
            [31]
            >>> TestCaseBase().dict_lookups(dct, 'a.b.c1', 'a.b.c2')
            [31, 32]
        """
        return tuple([self.dict_lookup(dct, lookup) for lookup in lookups])

    def is_dict_match(self, dict_a, dict_b, key_pairs):
        """See if 2 dictionaries match for certain keys
        For example:
            >>> dct_a = {'a': {'b': {'c': 3, 'd':4}}}
            >>> dct_b = {'x': {'y': {'z': 3, 'w':999}}}
            >>> TestCaseBase().is_dict_match(dct_a, dct_b, [('a.b.c','x.y.z'),])
            PASS: 3 # a.b.c == 3 # x.y.z
              True: [] ?== []
            PASS: [] == []
            >>> TestCaseBase().is_dict_match(dct_a, dct_b, [('a.b.d','x.y.w'),])
            Traceback (most recent call last):
                ignored traceback details removed for test clarity.
            AssertionError: FAIL: ['4 # a.b.d'] not == ['999 # x.y.w']
        """
        result_a = []
        result_b = []
        for (key_a, key_b) in key_pairs:
            value_a = self.dict_lookup(dict_a, key_a)
            value_b = self.dict_lookup(dict_b, key_b)
            print_a = "%r # %s" % (value_a, key_a)
            print_b = "%r # %s" % (value_b, key_b)
            if value_a == value_b:
                print("PASS: %s == %s" % (print_a, print_b))
            else:  # FAILED
                print("FAIL: %s not == %s" % (print_a, print_b))
                result_a.append(print_a)
                result_b.append(print_b)
        self.is_equal(result_a, result_b)

    def warn_is_equal(self, expected, actual, msg='', only_if=True):
        try:
            self.try_is(expected, lambda expected, actual: expected == actual, '==', actual, msg, only_if)
            return True
        except Exception as exc:
            traceback.print_exc()
            print("\nERROR: assertion error\n")
            return False
        #

    def warn_is_contained(self, expected, actual, msg='', only_if=True):
        try:
            self.try_is(expected, lambda expected, actual: expected in actual, 'contained in', actual, msg, only_if)
            return True
        except Exception as exc:
            traceback.print_exc()
            print("\nERROR: assertion error\n")
            return False
        #

    def does_raise(self, error, callable_obj=None, *args, **kwargs):
        try:
            callable_obj(*args, **kwargs)
            msg = "{0!r} with args {1!r} completed without errors.".format(callable_obj, args)
            self.print_fail(msg)
        except error as e:
            msg = "Expected {0!r} occurred with {1!r} with args {2!r}.".format(error, callable_obj, args)
            self.pprint("Expected Exception Info: {0}".format(e.message))
            self.print_pass(msg)
        except Exception as exception:
            self.pprint("Unexpected Exception Info: {0}".format(exception.message))
            raise


class TestCaseBase(AutomationBase):

    """All API tests should inherit from this base class."""
    __test__ = True  # needed for nose matching without inheriting from unittest.TestCase
    AUTO_MODE = AutomationBase.AutomationMode.API
    FIELD_SEP = "__"

    def __init__(self):
        AutomationBase.__init__(self)
        self.fb_test_users = {}

    def XFAIL(self, msg, function, args, kwargs):
        """Expect a failure (aka the devil you know) and mark test as skipped if it fails.

        If the SUT is broken we want a test that shows the problem, but we want our tests to be 100% green
        and we don't want to disable/comment out the test or the assert.
        The solution is to put in an L{XFAIL} call so the test runs, fails as expected,
        and is marked as skipped.

        If the first line fails, change to the second until the bug is fixed::
            self.is_equal(expected_total, api_data['total'])

            self.XFAIL("BUG-1234: Missing total", self.is_equal, (expected_total, api_data['total']))
        """
        try:
            function(*args, **kwargs)
        except AssertionError as exc:
            raise SkipTest("XFail: %s: %s" % (msg, exc))
        raise AssertionError("Test was expected to fail but passed: %s" % msg)

    def skip_tst(self, msg):
        """Wrapper for skipping a test."""
        raise SkipTest(msg)

    def __str__(self):
        middle, test_name = self.find_automation_shortname().split('.', 1)
        klass_name = middle.split(self.FIELD_SEP)[2]
        return "%s.%s" % (klass_name, test_name)

    @staticmethod
    def find_tst_fullname():
        frame = sys._getframe()
        for frame in iter(lambda: frame.f_back, None):
            # grab the test class and name for regular test methods
            tn = frame.f_locals.get('testMethod', None)
            if tn:
                ret = str(tn.__self__)
                return ret
            # grab test case names for generator tests.
            tn = frame.f_locals.get('g', None)
            if tn:
                ret = "%s.%s.%s" % (tn.__self__.__class__.__module__, tn.__self__.__class__.__name__, str(tn.__name__))
                return ret
        assert False, "Could not determine test name"

    @staticmethod
    def find_automation_shortname():
        full = TestCaseBase.find_tst_fullname()
        runner, middle, test_name = full.split('.', 2)
        os_browser, env, klass_name = middle.split(TestCaseBase.FIELD_SEP)[1:4]
        return "%s__%s__%s.%s" % (os_browser, env, klass_name, test_name)

    def find_automation_name(self):
        full_name = self.find_tst_fullname()
        return full_name.split('(')[0].split('.')[-1]

    def find_automation_func_name(self):
        # example: run_local.ma_test__OSX_FF__Prod__TestMa.tst_name({'param':'value'})
        # example: run_local.ma_test__OSX_FF__Prod__TestMa__1.tst_name({'param':'value'})
        return self.find_automation_name()

    def find_automation_complete_name(self):
        # example: TestMa.tst_name({'param':'value'})
        # example: TestMa__1.tst_name({'param':'value'})
        complete_name = self.find_tst_fullname().split('__', 3)[-1]
        return complete_name


@attr('Gui')
class GuiTestCaseBase(TestCaseBase):

    """All browser tests should inherit from this base class."""
    AUTO_MODE = AutomationBase.AutomationMode.GUI

    def setUp(self):
        TestCaseBase.setUp(self)

    def tearDown(self):
        TestCaseBase.tearDown(self)

    def execute_js_on(self, page):
        # for use with bookmarklets
        print("Executing my js")
        return page.execute_javascript(self.env_get_my_js())

if __name__ == "__main__":
    import doctest
    doctest.testmod()
