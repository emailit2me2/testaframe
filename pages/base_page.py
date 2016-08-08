
"""Basic page and form creation and manipulation classes and functionality.

This file should be clear of project specific code.
C{std_page.py} should have project specifics in it.
"""

import re
import sys
import time
import urllib
import inspect
import urlparse
import traceback

import selenium
# from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import UnexpectedTagNameException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import Select

import locate


class UnexpectedPageError(Exception):
    pass


class ElementNotFoundError(Exception):
    pass


class OperationTimedOutError(Exception):
    pass


class NoSuchElementError(Exception):
    pass


class WebDriverError(Exception):
    pass


class PageFactory(object):

    """A top level factory for creating page objects.

    All tests have an instance variable named C{start} so the tests can cleverly say
    C{self.start.at(PageObjectClass}).

    Window/tab stuff has to go up here at the factory level because
    only it has the cross page context.
    """
    MAIN_WINDOW = 'main'

    def __init__(self, driver, env, preclean, page_modules, platform_suffix, default_highlight_delay):
        """constructor

        @param driver: The selenium driver instance

        @param env: the environment mixin (really the test instance)

        @param preclean: Does the page need its cookie precleaned (needed for IE).

        @param page_modules: A list of all page modules for dealing with platform specific pages
                            (see L{make_page}).

        @param platform_suffix: String from the Selenium mixin class (see L{make_page}).

        @param default_highlight_delay: Default is settable via C{my_cfg.config['HIGHLIGHT_DELAY']}.
        """
        self.driver = driver
        self.env = env
        self.handles = {}
        self.preclean = preclean
        self.platform_suffix = platform_suffix
        self.classes = {}
        self.extra_data = {}  # can be used for custom verify_on_page() functions
        self.find_page_classes(page_modules)
        self.default_highlight_delay = default_highlight_delay
        self.set_highlight_delay(self.default_highlight_delay)
        self.tracker = None
        self.avoid_where_hangs = False

    def set_highlight_delay(self, highlight_delay=-1):
        """Set the blink time for L{BaseForm.highlight} and L{BaseForm.highlight_all}.

        @param highlight_delay: seconds to highlight or no value to return to default.
        """
        if highlight_delay < 0:
            self.highlight_delay = self.default_highlight_delay
        else:
            self.highlight_delay = highlight_delay
        print "Setting highlight delay to %r" % self.highlight_delay

    def find_page_classes(self, modules):
        """Find all the classes in the given page modules

        This is here to help with the platform_suffix problem.  Since it is here
        it can autodiscover all the page classes in each file, and then if a
        test requests a new page, the factory can look at all page classes and see
        if there is a platform specific one and instantiate it, otherwise just
        use the regular page class.

        @see: L{make_page}
        """
        # TODO can you protect from collisions in different gui files?
        # don't think so because BasePage you be duplicated by import in all files
        for module in modules:
            self.classes.update(dict(inspect.getmembers(sys.modules[module.__name__], inspect.isclass)))

    def make_form(self, form_class, parent, params=''):
        """Instantiate a new form"""
        new_form = form_class(parent, params)
        self.tracker.track(self.tracker.Record.NEW_FORM, form_class.__name__, value=params)
        return new_form

    def show_form(self, form_class, parent, params=''):
        """Make a new form object, verify it is being displayed, and set it as current"""
        print "show form %s" % (form_class.__name__)
        new_form = self.make_form(form_class, parent, params)
        new_form.verify_form_showing()
        parent.form = new_form

    def make_page(self, page_class, params, substitutions, **args_for_page):
        """Instantiate a new page object

        Check to see if there is a platform specific page class and use it.
        Instantiate the appropriate page object.
        """
        plat_cls_name = page_class.__name__ + self.platform_suffix
        plat_class = self.classes.get(plat_cls_name, page_class)
        if page_class != plat_class:
            print "Making a platform specific page: %s" % (plat_cls_name)
        # end if a platform specific class exists
        new_page = plat_class(self, params, substitutions, **args_for_page)

        self.tracker.on_new_page()

        print "-Created page object", new_page.__class__.__name__, params
        self.tracker.track(self.tracker.Record.NEW_PAGE, str(new_page), value="%r & %r" % (new_page.full_url(), params))
        return new_page

    def on_page(self, page_class, params='', substitutions=(), **args_for_page):
        """Out with the old, in with the new, and verify it too."""
        print "on page %s" % (page_class.__name__), params
        new_page = self.make_page(page_class, params, substitutions, **args_for_page)
        new_page.on_load()
        new_page.verify_on_page()
        return new_page

    def in_window(self, page_class, params, window_name):
        """Window management code is old and for early selenium 2.x.

        TODO revisit and make new testaframe tests as examples.
        """
        print "on page %s using %s" % (window_name, page_class.__name__)
        new_page = page_class(self, params)
        new_page.window_name = window_name
        all_handles = self.driver.window_handles
        # It doesn't switch to it so we have to deduce which one
        self.handles[window_name] = all_handles[-1]  # assume the last one
        print "Current handles %r" % self.handles.items()
        self.switch_to_window_name(window_name)
        new_page.verify_on_page()
        return new_page

    def switch_to_window_name(self, window_name):
        print "Switching to %s window by %r" % (window_name, self.handles[window_name])
        self.driver.switch_to_window(self.handles[window_name])

    def close_window_name(self, window_name):
        # then go back to the main window, do I really want to autoswitch to main.
        self.switch_to_window_name(window_name)
        self.driver.close()
        self.switch_to_window_name(self.MAIN_WINDOW)

    def at(self, page_class, params='', substitutions=(), skip_verify=False, **args_for_page):
        """Start C{at} the supplied page.

        The starting place for most tests.  Instantiate a page class,
        clean it, if needed, and verify that specific page is being displayed.
        """
        self.tracker.track(self.tracker.Record.START_AT, "start at", value=page_class.__name__)
        new_page = self.make_page(page_class, params, substitutions, **args_for_page)
        print "-Going to get %r" % (new_page.full_url())
        self.driver.get(new_page.full_url())
        new_page.on_load()
        if self.preclean:  # TODO only needed for IE, since ensureCleanSession doesn't work.
            # print self.driver.get_cookies()
            self.driver.delete_all_cookies()
            # print self.driver.get_cookies()
            self.driver.refresh()
            self.preclean = False  # only do preclean for initial page hit
        # end if preclean needed
        if not skip_verify:
            new_page.verify_on_page()
        self.handles[self.MAIN_WINDOW] = self.driver.window_handles[0]
        return new_page

    def save_snap_file(self, snap_path):
        print "saving snap file as: %s" % snap_path
        self.driver.get_screenshot_as_file(snap_path)


class ObsoletePage(object):

    """When a new page is created, the old one is obsolete and should not be reused.

    This object is an example of the NullObject pattern.

    @Note: Any attempt to use the driver attribute from an old page causes an exception.
    """

    def __getattr__(self, attr_name):
        raise Exception("Attempt to use obsolete page")


class BaseUiObject(object):
    """The base UI Object implementation class. Inherited by L{BaseForm}.

    Methods for dealing with the DOM are here, and page specifc methods are up on L{BasePage}.

    @note: element_spec: A common parameter used throughout the L{BaseForm} and L{BasePage}
                       classes for element selection.
                       An instance of a L{locate.ByBase} derived class locator.

    @note: start_with: A common optional parameter used throughout the L{BaseForm} and L{BasePage}
                       classes for cascading element selection
                       For instance, find the correct row in a table, then select a cell
                       starting with that row element.

    @note: log_type_into: A common optional parameter used for the by_* functions in L{BaseForm}.
                          This allows password and key field locators to not
                          log the values typed into them during L{type_into} calls..
                          The value C{**supressed**} is displayed instead.
    """
    KEYS = Keys

    def __init__(self, parent, params, substitutions=()):
        """Form objects are instantiated in L{PageFactory.make_form}.

        @param parent: The parent page.

        @param params: a string of extra stuff to be concatenated onto L{BasePage.PAGE}. Likely unused.

        @param substitutions: An array of values to be applied to L{BasePage.PAGE_SUB}. Likely unused.
        """
        print "-initing form %s with %r" % (self.__class__.__name__, params)
        self.factory = parent.factory
        self.tracker = self.factory.tracker
        self.driver = self.factory.driver
        self.params = params
        self.substitutions = substitutions
        self.parent = parent
        self._prep_finders()

    def __repr__(self):
        return self.__class__.__name__

    def _prep_finders(self):
        """All derived pages and forms must define one of these (ala Java interfaces).

        All classes derived from L{BasePage} must contain a C{self.verify_element} for use
        by L{BasePage.verify_on_page}.

        All classes derived from L{BaseForm} must contain a C{self.verify_form_element} for use
        by L{BasePage.verify_form_showing}.
        """
        raise Exception('_prep_finders() must be defined by derived Pages and Forms.')

    def wait(self, seconds, comment):
        """It is a test smell to have C{sleeps} in test code, so use polling or at least this wait. Still yucky though!

        @see: L{BasePage.make_waiter}
        """
        # TODO all delays should be done so we can scale them up or down, ala squish's SCALE_FACTOR.
        print "     !! waiting %d second(s) because %s !!" % (seconds, comment)
        time.sleep(seconds)

    def anno(*args, **kwargs):
        """Tests have @attr() and pages have anno()."""
        for name in args:
            print "ATTR page:", name
        for name, value in kwargs.iteritems():
            print "ATTR page:", name, "=", repr(value)

    def by_css(self, locator, log_type_into=True):
        """A DRY wrapper so we don't have to pass the page/form class in every locator definition."""
        return locate.ByCssSelector(self, locator, log_type_into)

    def by_id(self, locator, log_type_into=True):
        return locate.ByID(self, locator, log_type_into)

    def by_name(self, locator, log_type_into=True):
        return locate.ByName(self, locator, log_type_into)

    def by_tag_name(self, locator, log_type_into=True):
        return locate.ByTagName(self, locator, log_type_into)

    def by_class_name(self, locator, log_type_into=True):
        return locate.ByClassName(self, locator, log_type_into)

    def by_link_text(self, locator, log_type_into=True):
        return locate.ByLinkText(self, locator, log_type_into)

    def by_partial_link_text(self, locator, log_type_into=True):
        return locate.ByPartialLinkText(self, locator, log_type_into)

    def by_xpath(self, locator, log_type_into=True):
        return locate.ByXpath(self, locator, log_type_into)

    def highlight(self, element):
        """Highlights (blinks) an element.

        The highlight time is configurable via L{PageFactory.set_highlight_delay}

        @note: The css formatting can be off by a pixel or two during highlighting.
        """
        if not self.factory.highlight_delay:
            return

        def apply_style(s):
            self.driver.execute_script("arguments[0].setAttribute('style', arguments[1]);",
                                       element, s)
        original_style = element.get_attribute('style')
        apply_style("background: yellow; border: 2px solid red;")
        time.sleep(self.factory.highlight_delay)
        apply_style(original_style)

    def highlight_all(self, elements):
        """Highlights (blinks) a group of elements.

        @see: L{highlight}
        """
        if not self.factory.highlight_delay:
            return

        def apply_style(s):
            self.driver.execute_script("arguments[0].setAttribute('style', arguments[1]);",
                                       element, s)
        original_styles = []
        for element in elements:
            original_styles.append(element.get_attribute('style'))
            apply_style("background: yellow; border: 2px solid red;")
        time.sleep(self.factory.highlight_delay)
        for element in elements:
            apply_style(original_styles.pop(0))

    def find_the(self, element_spec, record_type=None, start_with=None, doit=None):
        """Poll to find an element in the DOM based on an element_spec

        This function is at the heart of the framework, along with the polling asserts.

        The polling timeout maximum (L{set_poll_max <test_gui.base_tst.TestCaseBase.set_poll_max>})
        and the delay (L{set_poll_delay <test_gui.base_tst.TestCaseBase.set_poll_delay>}) are settable.
        """
        sub = ''
        if start_with:
            sub = "sub-"
        else:  # start at the root
            start_with = self.driver
        #
        msg = "{0} {1}".format(sub + "element", element_spec)
        print "Find " + msg
        start = time.time()
        exc = OperationTimedOutError("find_the timed out without error. This should NOT happen.")
        while time.time() - start < self.factory.poll_max:
            try:
                ret = start_with.find_element(element_spec.by, element_spec.spec)
                if not record_type:
                    print "\n!!!ERROR missing record type!!!\n"
                    raise Exception("missing record type")
                if record_type == self.tracker.Record.DEFERRED:
                    print "info: deferred for %s" % element_spec
                else:  # track it here and now
                    self.tracker.track(record_type=record_type, message=msg, location=self.where(ret))
                #
                self.highlight(ret)
                print "  found", element_spec    # TODO
                if ret:
                    if doit:
                        print "  trying to do %r" % (doit,)
                        doit(ret)  # ret.click()
                    return ret
                else:  # must be None
                    exc = ElementNotFoundError("  not found")
                    time.sleep(self.factory.poll_delay)
            except selenium.common.exceptions.NoSuchElementException:
                print "  Waiting for element (%s): %5.2f secs" % (element_spec, time.time() - start)
                exc = NoSuchElementError(" no such element matching {0}".format(element_spec))
                time.sleep(self.factory.poll_delay)
            except selenium.common.exceptions.WebDriverException:
                print "  Waiting for element (%s): %5.2f secs" % (element_spec, time.time() - start)
                exc = WebDriverError(" web driver exception")
                time.sleep(self.factory.poll_delay)
            except Exception as exc:
                print "  Took general exception in find_the: %s" % (exc)
                raise
            #
        # end while not timed out
        raise exc

    def find_all(self, element_spec, record_type=None, start_with=None):
        """Poll to find all matching elements in the DOM based on an element_spec.

        @see: L{find_the}
        """
        sub = 'sub'
        if start_with:
            sub = "sub-"
        else:  # start at the root
            start_with = self.driver
            sub = ""
        #
        print "find %selements %s" % (sub, element_spec)
#    raw_input('waiting to find')
        start = time.time()
        exc = OperationTimedOutError("find_the timed out without error. This should NOT happen.")
        while time.time() - start < self.factory.poll_max:
            try:
                ret = start_with.find_elements(element_spec.by, element_spec.spec)
                print "  found %d element(s)" % len(ret)
                if not record_type:
                    print "\n!!!ERROR missing record type!!!\n"
                    raise Exception("missing record type")
                if record_type == self.tracker.Record.DEFERRED:
                    print "info: deferred for %s" % element_spec
                else:  # track it here and now
                    self.tracker.track_all(record_type=record_type, message=str(element_spec),
                                           locations=self.where_all(ret))
                #
                self.highlight_all(ret)
                return ret
            except selenium.common.exceptions.NoSuchElementException:
                print "  Waiting for elements (%s): %5.2f secs" % (element_spec, time.time() - start)
                exc = NoSuchElementError(" no such elements matching {0}".format(element_spec))
                time.sleep(self.factory.poll_delay)
            except selenium.common.exceptions.WebDriverException:
                print "  Waiting for elements (%s): %5.2f secs" % (element_spec, time.time() - start)
                exc = WebDriverError(" web driver exception")
                time.sleep(self.factory.poll_delay)
            except Exception as exc:
                traceback.print_exc()
                raise
            #
        # end while
        raise exc  # TODO exc is not defined, but can't get the message to read pretty when fixed

    def can_find_the(self, element_spec, start_with=None):
        """Wrap L{find_the} so it returns whether an item can be found rather than the element.

        This allows for a straight forward way to determine if an element is found without
        catching the exception yourself.
        @note: Be careful with negative assertions, if you mess up the locator
              you'll also find no elements in the DOM.
        """
        if not start_with:  # start at the root
            start_with = self.driver

        try:
            e = start_with.find_element(element_spec.by, element_spec.spec)
            print "Element can be found: %s" % (element_spec)
            ret = True
            location = self.where(e)
        except selenium.common.exceptions.NoSuchElementException:
            print "Element cannot be found: %s" % (element_spec)
            ret = False
            location = None
        self.tracker.track(self.tracker.Record.CAN_FIND_THE, message=str(element_spec), location=location)
        return ret

    def should_not_find_the(self, element_spec):
        """Wrap L{find_the} so it behaves nicely when no elements are expected to be found.

        This is often used after a delete call to ensure the item is no longer in the DOM.
        @note: Be careful with negative assertions, if you mess up the locator
              you'll also find no elements in the DOM.
        """
        try:
            e = self.driver.find_element(element_spec.by, element_spec.spec)
            print "Element not expected to have been found: %s" % (element_spec)
            ret = False
            location = self.where(e)
        except selenium.common.exceptions.NoSuchElementException:
            print "Should not find element and didn't %s" % (element_spec)
            ret = True
            location = None
        self.tracker.track(self.tracker.Record.SHOULD_NOT_FIND_THE, message=str(element_spec), location=location)
        return ret

    def should_not_find_any(self, element_spec):
        """A wrapper around the singluar form of L{should_not_find_the} for completeness and test readability."""
        # find_elements returns [] on failure, it doesn't throw so reuse above
        return self.should_not_find_the(element_spec)

    def where(self, element):
        if self.factory.avoid_where_hangs:
            return {}
        ret = element.size
        ret.update(element.location)
        return ret

    def where_all(self, elements):
        if self.factory.avoid_where_hangs:
            return {}
        ret = [self.where(element) for element in elements]
        return ret

    def click_on(self, element_spec, start_with=None, doit=None):
        """Simple find and click an element

        @param doit: An optional click mechanism added to deal with some ajaxy pages
                    (not sure its needed any more).
        """
        e = self.find_the(element_spec, self.tracker.Record.CLICK, start_with, doit)
        print "-click on %s" % (element_spec)
        if not doit:
            e.click()

    def move_to(self, element_spec, start_with=None):
        """Moves to an element."""
        print "move to %s" % element_spec
        elem = self.find_the(element_spec, self.tracker.Record.MOVE_TO, start_with)
        ActionChains(self.driver).move_to_element(elem).perform()

    def move_and_click(self, element_spec, start_with=None):
        """Alternate click method sometimes needed for ajaxy elements."""
        print "move and click on %s" % (element_spec)
        ActionChains(self.driver).move_to_element(self.find_the(element_spec, self.tracker.Record.MOVE_AND_CLICK,
                                                  start_with)).click().perform()

    def click_one_of_by_index(self, element_spec, index, start_with=None):
        """click an item from a list of items

        Use this for ajaxy pages that do not use the select tag and have
        no text is available to select by.

        @see: L{click_one_of}, L{select_from}
        """
        start = time.time()
        exc = Exception("  not found")
        while time.time() - start < self.factory.poll_max:
            elements = self.find_all(element_spec, self.tracker.Record.CLICK_ONE_OF_BY_INDEX_OPTIONS,
                                     start_with=start_with)
            if len(elements) >= index + 1:
                try:
                    print "click on by index %s[%d]" % (element_spec, index)
                    self.tracker.track(self.tracker.Record.CLICK_ONE_OF_BY_INDEX_CLICK, message=str(element_spec),
                                       value=index, location=self.where(elements[index]))
                    elements[index].click()
                    return
                except Exception as exc:
                    print " Waiting for %d >= %d elements: %5.2f secs" % (len(elements), index + 1, time.time() - start)
                    time.sleep(self.factory.poll_delay)
                #
            else:  # not enough elements found yet
                print "  Waiting for %d >= %d elements: %5.2f secs" % (len(elements), index + 1, time.time() - start)
                time.sleep(self.factory.poll_delay)
            #
        # end while not timed out
        raise exc

    def click_one_of_by_substring(self, element_spec, substring, start_with=None):
        return self.click_one_of_selectable(element_spec, substring,
                                            self.tracker.Record.CLICK_ONE_OF_OPTIONS_BY_SUBSTRING,
                                            exact=False, start_with=start_with)

    def click_one_of(self, element_spec, text, start_with=None):
        return self.click_one_of_selectable(element_spec, text, self.tracker.Record.CLICK_ONE_OF_OPTIONS,
                                            exact=True, start_with=start_with)

    def click_one_of_selectable(self, element_spec, text, record, exact, start_with=None):
        """non-standard select an item from a drop down list

        Use this for ajaxy pages that do not use the select tag

        @see: L{click_one_of_by_index}, L{select_from}
        """
        start = time.time()
        exc = Exception("  not found")
        while time.time() - start < self.factory.poll_max:
            elements = self.find_all(element_spec, self.tracker.Record.DEFERRED, start_with=start_with)
            options = [el.text for el in elements]
            self.tracker.track_all(record, message=str(element_spec),
                                   values=options, locations=self.where_all(elements))
            print options
            try:
                if exact:
                    found = options.index(text)
                else:  # by substring
                    for (index, opt) in enumerate(options):
                        if text in opt:
                            found = index
                            break
                        #
                    #
                #
                msg = "click on %s[%d=%r]" % (element_spec, found, text)
                self.tracker.track(self.tracker.Record.CLICK_ONE_OF_CLICK, msg, value=text,
                                   location=self.where(elements[found]))
                elements[found].click()
                return
            except Exception as exc:
                print "  Waiting for %r in %d elements: %5.2f secs" % (text, len(elements), time.time() - start)
                time.sleep(self.factory.poll_delay)
            #
        # end while not timed out
        raise exc

    def select_the(self, element_spec, start_with=None):
        """Standard select a radio button or checkbox item

        Use this for standard HTML pages that use input tags
        """
        e = self.find_the(element_spec, self.tracker.Record.SELECT_THE, start_with)
        print "select the %s" % (element_spec)
        e.select()

    def select_from(self, element_spec, text, start_with=None):
        """Standard select an item from a drop down list

        Use this for standard HTML pages that use the select tag

        @see: click_one_of
        """
        e = self.find_the(element_spec, self.tracker.Record.SELECT_FROM, start_with)
        print "select from %s choosing %r" % (element_spec, text)
        try:
            select = Select(e)
            select.select_by_visible_text(text)
        except UnexpectedTagNameException as exc:
            print "WARNING: Try using click_one_of", exc
            raise

    def find_one_of_by_index(self, element_spec, index, start_with=None):
        """find an item from a list of items

        Use this for ajaxy pages that do not use the select tag and have
        no text is available to select by.
        """
        start = time.time()
        exc = Exception("  not found")
        while time.time() - start < self.factory.poll_max:
            e = self.find_all(element_spec, self.tracker.Record.FIND_ONE_OF_BY_INDEX, start_with)
            if len(e) >= index + 1:
                try:
                    print "Found by index %s[%d]" % (element_spec, index)
                    return e[index]
                except Exception as exc:
                    print "  Waiting for %d >= %d elements: %5.2f secs" % (len(e), index + 1, time.time() - start)
                    time.sleep(self.factory.poll_delay)
                #
            else:  # not enough elements found yet
                print "  Waiting for %d >= %d elements: %5.2f secs" % (len(e), index + 1, time.time() - start)
                time.sleep(self.factory.poll_delay)
            #
        # end while not timed out
        raise exc

    def type_into(self, element_spec, text, clear_first=False, start_with=None):
        """Find text field, optionally clear it first, then type into it."""
        e = self.find_the(element_spec, self.tracker.Record.DEFERRED,  start_with=None)
        if clear_first:
            e.clear()
            self.tracker.track(self.tracker.Record.CLEAR, message=str(element_spec), location=self.where(e))
        e.send_keys(text)
        if not element_spec.log_type_into:  # Don't log passwords and such
            text = "**suppressed**"
        self.tracker.track(self.tracker.Record.TYPE_INTO, message=str(element_spec), value=text, location=self.where(e))
        print "-type into %s = %r" % (element_spec, text)

    def clear_field(self, element_spec):
        """Clear a text field"""
        e = self.find_the(element_spec, self.tracker.Record.CLEAR)
        print "clear field %s" % (element_spec)
        e.clear()

    def make_waiter(self):
        """Make a C{WebDriverWait} object

        This is how to do polling/waiting with settable timeout and delay in page objects.
        The driver variable is unused since it is included in the page object (i.e. self).

        Usually used like::
          self.make_waiter().until(lambda driver: self.name_in_message(name))
        """
        return WaiterWrapper(self)

    def switch_to_frame(self, css_selector):
        """ Switches the driver into a new frame
        @param css_selector: the css selector of the frame to switch into such as an iframe
        """
        css_selector = self.driver.find_elements_by_css_selector(css_selector)[0]
        self.driver = self.driver.switch_to.frame(css_selector)

    def switch_out_of_frame(self):
        """ Switches the driver back to the previous frame """
        self.driver = self.driver.switch_to.default_content()


class WaiterWrapper:
    def __init__(self, parent):
        self.parent = parent
        self.waiter = WebDriverWait(parent.driver, parent.factory.poll_max, parent.factory.poll_delay)

    def until(self, method, message=''):
        self.parent.tracker.track(self.parent.tracker.Record.POLL_START, 'Waiter')
        try:
            self.waiter.until(method, message)
        except Exception, exc:
            raise
        finally:
            self.parent.tracker.track(self.parent.tracker.Record.POLL_END, 'Waiter')


class BaseForm(BaseUiObject):

    """The base form implementation class. Inherited by L{BasePage}.

    All form objects must exist on a parent page object.

    Methods for dealing with the DOM are here, and page specifc methods are up on L{BasePage}.

    @note: element_spec: A common parameter used throughout the L{BaseForm} and L{BasePage}
                       classes for element selection.
                       An instance of a L{locate.ByBase} derived class locator.

    @note: start_with: A common optional parameter used throughout the L{BaseForm} and L{BasePage}
                       classes for cascading element selection
                       For instance, find the correct row in a table, then select a cell
                       starting with that row element.
                       An instance of a Selenium Element, not a L{locate.ByBase}.

    @note: log_type_into: A common optional parameter used for the by_* functions in L{BaseForm}.
                          This allows password and key field locators to not
                          log the values typed into them during L{type_into} calls..
                          The value C{**supressed**} is displayed instead.
    """
    def verify_form_showing(self):
        """Similar to L{BasePage.verify_on_page} but for forms."""
        return self.parent.make_waiter().until(lambda driver: self.verify_form_element.is_this_displayed())

    def submit_form(self, element_spec):
        """Submit a form"""
        form = self.find_the(element_spec, self.tracker.Record.SUBMIT_FORM)
        print "-submit form %s" % (element_spec)
        form.submit()


class BasePage(BaseForm):

    """All page objects must inherit from this.



    All derived pages must have a L{PAGE} or L{PAGE_SUB} class constant.

    @cvar PAGE: The page path to use (e.g. C{/}, C{/about}).

    @cvar PAGE_SUB: Stands for page substitution.  A page path string template (e.g. C{//user/%s}).
                     The C{substitutions} parameter is applied during page creation.
                     An explicit L{PAGE_RE} is required when using this option.

    @cvar PAGE_RE: Stands for page regular expression (e.g. C{/user/d+}).
                    If there is no L{PAGE_RE} then one will be created by wrapping
                    L{PAGE} in C{^} and C{$}.
                    This regular expression is used in L{verify_on_page} to ensure
                    the correct page is appearing.

    @note: NO asserts in the page objects! They belong in the test.
           The few exceptions are L{verify_on_page}) and L{BasePage.make_waiter}.
    """
    PAGE = ''
    PAGE_RE = ''
    PAGE_SUB = ''
    EVIL_STABLE_PAGE_WAIT = 1

    def __init__(self, factory, params, substitutions, parent=None, **args_for_page):
        """Page objects are instantiated in L{PageFactory.make_page}.

        @param factory: The page factory instance

        @param params: a string of extra stuff to be concatenated onto L{PAGE}.

        @param substitutions: An array of values to be applied to L{PAGE_SUB}.

        @param parent: The (optional) parent page. TODO when can there be a parent?
        """
        # print "initing page %s with %s" % (self.__class__.__name__, params)
        self.factory = factory
        self.driver = factory.driver
        self.params = params
        self.substitutions = substitutions
        self.parent = parent
        self.tracker = self.factory.tracker
        self.args = args_for_page
        self.window_name = self.factory.MAIN_WINDOW
        if self.PAGE_SUB and substitutions:
            self.PAGE = self.PAGE_SUB % substitutions
        if not self.PAGE_RE:
            self.PAGE_RE = '^' + self.PAGE + '$'
        self._prep_finders()

    def full_url(self):
        """Create the full URL for this page."""
        base_url = self.factory.env.get_url(self.HOST_ENUM)
        url = urlparse.urljoin(base_url, self.PAGE + self.params)
        print "-Full url is %s" % url
        return url

    def refresh_page(self):
        """Wrapper to referesh the page."""
        print "-Refreshing page"
        self.tracker.track(self.tracker.Record.REFRESH_PAGE, 'same page')
        self.driver.refresh()

    def refresh_page_with_redir(self, redir_page):
        """Wrapper to referesh the page which causes a redirection to another page."""
        print "Refreshing page which should redir to %s" % redir_page
        self.tracker.track(self.tracker.Record.REFRESH_PAGE, 'redir to', value=str(redir_page))
        self.refresh_page()
        return self.now_on(redir_page)

    def go_back(self, page_class):
        """Wrapper to go back to the previous page."""
        print "Go back"
        self.driver.back()
        return self.now_on(page_class)

    def execute_javascript(self, javascript):
        """Wrapper to execute javascript code on the current page."""
        return self.driver.execute_script(javascript)

    def scroll_right(self):
        return self.driver.execute_script(
            'scrollTo(document.body.scrollWidth,0);return document.body.scrollWidth')

    def scroll_down(self):
        return self.driver.execute_script(
            'scrollTo(0,document.body.scrollHeight);return document.body.scrollHeight')

    def scroll_up(self):
        return self.driver.execute_script('scrollTo(0,0);return document.body.scrollHeight')

    def scroll_to(self, target):
        print "scrollTo(0, %f); return document.body.scrollHeight" % target.int_of_attribute_of('offsetTop')
        return self.driver.execute_script(
            'scrollTo(0, %f); return document.body.scrollHeight' % target.int_of_attribute_of('offsetTop'))

    def goto_page(self, page_class, params='', substitutions=()):
        """Used to go directly to another page."""
        print "Goto page %s using %s" % (page_class.__name__, params)
        return self.factory.at(page_class, params, substitutions)

    def goto_page_with_redir(self, page_class, redir_page, params='', substitutions=()):
        """Wrapper to go to the page which causes a redirection to another page."""
        print "Goto page %s which should redir to %s using %s" % (page_class.__name__, redir_page, params)
        self.factory.at(page_class, params, substitutions, skip_verify=True)
        return self.now_on(redir_page)

    def now_on(self, page_class, params='', substitutions=(), **args_for_page):
        """Make and return the now current page, obsoleteing the old page.

        This is often called as part of a click event that takes you to another page.

        For example::
          def goto_frobnication_page(self):
              self.click_on(self.frobnication_link)
              return self.now_on(FrobnicationPage)
        """
        new_page = self.factory.on_page(page_class, params, substitutions, **args_for_page)

        # we should inherit the window name
        if (self.window_name != self.factory.MAIN_WINDOW):
            new_page.window_name = self.window_name
        print "Now on %s with window_name %s" % (page_class.__name__, new_page.window_name)
        self.driver = ObsoletePage()
        return new_page

    def new_window(self, page_class, window_name):
        print "Now on %s window using %s" % (window_name, page_class.__name__)
        return self.factory.in_window(page_class, '', window_name)

    def get_path(self):
        """Get the path for the current page."""
        url = self.driver.current_url
        obj = urlparse.urlparse(url)
        path = obj.path
        print "-Current url %r" % url, path, obj.fragment
        return path

    def get_title(self):
        """Wrapper to get the page title"""
        title = self.driver.title
        print "Current title %r" % title
        return title

    def verify_on_page(self):
        """Polls to ensure the URL and DOM match the expected page.

        The asynchronous nature of Selenium means we can't guarantee the page objects match
        the actual pages displayed for a variety of reasons, usually bugs in the tests
        or the system under test.

        For instance if we are on the login page, we fill in the credentials, then click Login,
        but the login fails for some reason, we will not be on the expected page next page.
        So there is a problem but we won't know that until we try to do or check something
        and see a confusing error message.  This way we check and know right up front
        that we did not get to the expected page.

        One of the ways we guard against this is to verify the URL and an element in the DOM
        when we change to a different page.

        Every page object must have a L{PAGE_RE} defined as well as a C{verify_element}
        defined in L{_prep_finders}.
        """
        start = time.time()
        max_wait_time = self.factory.poll_max
        exc = OperationTimedOutError("Verify on page timed out without error. This should NOT happen.")
        while time.time() - start < (max_wait_time):
            try:
                path_is = self.get_path()
                pattern = self.PAGE_RE % self.__dict__
                to_match = re.compile(pattern)
                print "-Verifying %s path pattern %r matches %r" % (
                    self.__class__.__name__, self.PAGE_RE, path_is)
                if not to_match.search(path_is):
                    raise UnexpectedPageError("FAIL: Expected URL %r does NOT match actual URL %r" %
                                              (self.PAGE_RE, path_is))
                assert hasattr(self, 'verify_element'), 'All pages must have a verify_element defined'
                self.find_the(self.verify_element, self.tracker.Record.VERIFY)
                self.wait(self.EVIL_STABLE_PAGE_WAIT, 'stupid wait due to stale element problems')
                if hasattr(self, 'form'):  # TODO need a null object form here
                    self.form.verify_form_showing()
                # self.tracker.track(self.tracker.Record.SNAP, "Now On: verified", value=self.__class__.__name__)

                return
            except UnexpectedPageError as exc:
                print "  Waiting for verify on page: %5.2f secs of %5.2f" % (time.time() - start, max_wait_time)
                time.sleep(self.factory.poll_delay)
            except:
                raise
            #
        # end while
        raise exc

    def now_showing_form(self, form_class, params=''):
        """Set the currently displayed form.

        @see: L{now_on}
        """
        print "Now showing %s" % form_class.__name__
        self.factory.show_form(form_class, self, params)

    def switch_to_it(self):
        self.factory.switch_to_window_name(self.window_name)

    def close_it(self):
        print "Closing window %s" % self.window_name
        self.factory.close_window_name(self.window_name)

    def get_page_source(self):
        """Return the html of the DOM."""
        return self.driver.page_source

    def get_cookie(self, name):
        """Get named cookie and unquote it."""
        cookie = self.driver.get_cookie(name)
        ser = urllib.unquote(cookie['value'])
        print "-Getting cookie %r = %r" % (name, ser)
        self.tracker.track(self.tracker.Record.GET_COOKIE, name, ser)
        return ser

    def set_cookie(self, cookie, value):
        """Set cookie"""
        print "-Setting cookie %r = %r" % (cookie, value)

        # TODO extract the domain from this hard coded string
        cookie_script = 'document.cookie = "{cookie}={value}; path=/; domain=.example.com;"'.format(**locals())

        print "-Executing %r" % cookie_script
        self.tracker.track(self.tracker.Record.SET_COOKIE, cookie, value)
        self.driver.execute_script(cookie_script)

    def get_alert(self):
        """Wait for alert to display and return an L{AlertObj}."""
        self.make_waiter().until(expected_conditions.alert_is_present())
        return AlertObj(self.driver)

    def on_load(self):
        pass

    def save_snap(self):
        self.factory.save_snap_file()


# This AlertObj is not great.  TODO make it better.
class AlertObj(object):

    """An alert object, consistant with page objects."""

    def __init__(self, driver):
        self.alert = Alert(driver)
        print "Creating alert"

    def choose_accept(self):
        """Wrapper for accepting the alert."""
        print "Choosing accept on alert"
        self.alert.accept()
        print "Accept chosen on alert"
