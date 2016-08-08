

import gc
import re
import sys
# import time
# import selenium
# from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.by import By


class ByBase(object):
    NON_NAMES = ['self', 'element_spec']
    by = None  # must be defined by subclasses

    # TODO support indexing, thing[2].the_text() or thing.the_text(2)

    def __init__(self, page, spec, log_type_into):
        self.page = page
        self.spec = spec
        self.log_type_into = log_type_into
        assert self.by, "self.by must be defined by subclasses"

    def __log_action(self, action):
        item_name = self.find_name()
        print "%s on item %s" % (action, item_name)

    def find_name(self):
        """Find the name of a variable via introspection.

         This is kind of odd but we want to know what this variable is named in
         the outside world, rather than having to pass in a string name.
         This is done to make the logs more readable and reduce the DRY in prep_finders().
         For example, in gui_pages.py:AjaxyPage._prep_finders() the following line::
               self.new_label_field = self.by_name('typer')
         would need to have a name passed in to yield the logging verboseness we want::
               self.new_label_field = self.by_name('new_label_field','typer')
         The logs for this are super clear and the code is DRY::
               find element 'new_label_field' using name='typer'
               type into 'new_label_field' using name='typer' = u'...'
         TODO we should cache this value once we look it up.
        """
        frame = sys._getframe()
        for frame in iter(lambda: frame.f_back, None):
            frame.f_locals
        result = []
        for referrer in gc.get_referrers(self):
            if isinstance(referrer, dict):
                for var_name, variable in referrer.iteritems():
                    if variable is self and var_name not in self.NON_NAMES:
                        result.append(var_name)
    # TODO this is a good assert normally
    # assert len(result) == 1, "Problem finding a name for %r, found %r" % (self.spec, result)
        return result[0]

    def __str__(self):
        # pos = "@%(x)dx%(y)d,%(width)dx%(height)d" % self.xylw()
        # return "%r using %s=%r %s" % (self.find_name(), self.by, self.spec, pos)
        return "%r using %s=%r" % (self.find_name(), self.by, self.spec)

    def stringify(self, **kwparams):
        ret = str(self)
        if kwparams:
            ret += " using: %r" % kwparams
        return ret

    def _find_get_track(self, record, getter, **kwparams):
        self.last_element_found = self.page.find_the(self, self.page.tracker.Record.DEFERRED)
        ret = getter(self.last_element_found)
        self.page.tracker.track(record, message=self.stringify(**kwparams), value=ret,
                                location=self.where(self.last_element_found))
        return ret

    def _find_all_get_track(self, record, getter, **kwparams):
        self.last_elements_found = self.page.find_all(self, self.page.tracker.Record.DEFERRED)
        ret = [getter(e) for e in self.last_elements_found]
        self.page.tracker.track_all(record, message=self.stringify(**kwparams), values=ret,
                                    locations=self.where_all(self.last_elements_found))
        return ret

    def the_text(self):
        """Find the element and return the text"""
        return self._find_get_track(self.page.tracker.Record.THE_TEXT, lambda e: e.text)

    def the_text_stripped(self):
        """Find the element and return the stripped text"""
        return self._find_get_track(self.page.tracker.Record.THE_TEXT_STRIPPED, lambda e: e.text.strip())

    def the_text_lower(self):
        """Find the element and return the lowercased text"""
        return self._find_get_track(self.page.tracker.Record.THE_TEXT_LOWER, lambda e: e.text.lower())

    def all_the_text(self):
        """Find all matching elements and return all the text"""
        return self._find_all_get_track(self.page.tracker.Record.ALL_THE_TEXT, lambda e: e.text)

    def all_the_text_lower(self):
        """Find all matching elements and return all the lowercased text"""
        return self._find_all_get_track(self.page.tracker.Record.ALL_THE_TEXT_LOWER, lambda e: e.text.lower())

    def rows_of_text(self, cell_spec):
        all = []
        for e in self.page.find_all(self):
            all.append([e.text for e in self.page.find_all(cell_spec, e)])
        return all

    def the_attribute(self, attrib):
        """Find an element and get a specific attribute."""
        return self._find_get_track(self.page.tracker.Record.THE_ATTRIBUTE,
                                    lambda e: e.get_attribute(attrib), attribute=attrib)

    def all_the_attributes(self, attrib):
        """Find all the matching element and get a specific attribute."""
        return self._find_all_get_track(self.page.tracker.Record.ALL_THE_ATTRIBUTES,
                                        lambda e: e.get_attribute(attrib), attribute=attrib)

    def is_this_enabled(self):
        """Find an element and check if it is currently enabled."""
        # assert self.page.find_the(self).is_displayed()
        return self._find_get_track(self.page.tracker.Record.IS_THIS_ENABLED, lambda e: e.is_enabled())

    def is_this_selected(self):
        """Find an element and check if it is currently selected or checked for a checkbox."""
        # assert self.page.find_the(self).is_displayed()
        return self._find_get_track(self.page.tracker.Record.IS_THIS_SELECTED, lambda e: e.is_selected())

    def is_this_displayed(self):
        """Find an element and check if it is currently displayed."""
        return self._find_get_track(self.page.tracker.Record.IS_THIS_DISPLAYED, lambda e: e.is_displayed())

    def int_of(self):
        """Find an element and return the integer value of the text.

        Returns None on failure, which will happen for int('').
        """
        try:
            return self._find_get_track(self.page.tracker.Record.INT_OF, lambda e: int(e.text))
        except ValueError:
            self.page.tracker.track(self.page.tracker.Record.INT_OF, message=self.stringify(), value=None,
                                    location=self.where(self.last_element_found))
            return None

    def all_ints_of(self):
        """Find all the matching elements and return the integer values of all the text."""
        try:
            return self._find_all_get_track(self.page.tracker.Record.ALL_INTS_OF,
                                            lambda e: int(e.text.replace(',', '')))
        except ValueError:
            self.page.tracker.track_all(self.page.tracker.Record.ALL_INTS_OF, message=self.stringify(),
                                        values=[], locations=self.where_all(self.last_elements_found))
            return []  # this will happen for int('')

    def int_by_regex(self, text):
        int_regex = re.compile(r"(\d+)")
        res = int_regex.search(text)
        if res:
            return int(res.group(1))
        else:
            return None

    def int_of_regex(self):
        """Find an element and return the integer value of the first int parsed from the text.

        Returns None on failure, which will happen for int('').
        """
        try:
            return self._find_get_track(self.page.tracker.Record.INT_OF_REGEX, lambda e: self.int_by_regex(e.text))
        except ValueError:
            self.page.tracker.track(self.page.tracker.Record.INT_OF_REGEX, message=self.stringify(),
                                    value=None, location=self.where(self.last_element_found))
            return None

    def all_ints_of_regex(self):
        """Find all the matching elements and return the integer values of all the text."""
        try:
            return self._find_all_get_track(self.page.tracker.Record.ALL_INTS_OF_REGEX,
                                            lambda e: self.int_by_regex(e.text))
        except ValueError:
            self.page.tracker.track_all(self.page.tracker.Record.ALL_INTS_OF_REGEX, message=self.stringify(),
                                        values=[], locations=self.where_all(self.last_elements_found))
            return []  # this will happen for int('')

    def int_of_attribute_of(self, attrib):
        """Find an element and return the integer of a specific attribute."""
        try:
            return self._find_get_track(self.page.tracker.Record.INT_OF_ATTRIBUTE,
                                        lambda e: int(e.get_attribute(attrib)), attribute=attrib)
        except ValueError:
            self.page.tracker.track(self.page.tracker.Record.INT_OF_ATTRIBUTE, message=self.stringify(attribute=attrib),
                                    value=None, location=self.where(self.last_element_found))
            return None  # this will happen for int('')

    def length_of(self):
        """Return the length of, really count of, of matching elements."""
        print "  Checking length of %s" % (self)
        all = self.page.find_all(self, self.page.tracker.Record.DEFERRED)
        # print "   found all of %r" % all
        length = len(all)
        print "    -got len = %r" % length
        self.page.tracker.track_all(self.page.tracker.Record.LENGTH_OF, message=self.stringify(),
                                    values=[length], locations=self.where_all(all))
        return length

    def length_of_displayed(self):
        """Return the length of, really count of, of matching elements that are displayed."""
        print "  Checking length of displayed %s" % (self)
        all = self.page.find_all(self, self.page.tracker.Record.DEFERRED)
        # print "   found all of %r" % all
        length = len(all)
        print "    -got len = %r" % length
        count = 0
        for element in all:
            if element.is_displayed():
                print "-is displayed", element
                count += 1
        self.page.tracker.track_all(record, message=self.stringify(), values=[count], locations=self.where_all(all))
        return count

    def value_of(self):
        """Return the "value" attribute of the element."""
        return self.the_attribute("value")

    def get_name(self):
        """Return the "name" attribute of the element."""
        return self.the_attribute("name")

    def the_y_position(self):
        """Return the vertical position of the element."""
        # print "  -The location of %s is %s" % (self, self.page.find_the(self).location)
        return self._find_get_track(self.page.tracker.Record.Y_POSITION, lambda e: e.location["y"])

    def where(self, element):
        """Return the x,y position and length,width of the element."""
        if self.page.factory.avoid_where_hangs:
            return {}
        ret = element.size
        ret.update(element.location)
        return ret

    def where_all(self, elements):
        if self.page.factory.avoid_where_hangs:
            return {}
        ret = [self.where(element) for element in elements]
        return ret

# Utility classes for all the different locator techniques.


class ByXpath(ByBase):
    by = By.XPATH


class ByID(ByBase):
    by = By.ID


class ByName(ByBase):
    by = By.NAME


class ByTagName(ByBase):
    by = By.TAG_NAME


class ByCssSelector(ByBase):
    by = By.CSS_SELECTOR


class ByClassName(ByBase):
    by = By.CLASS_NAME

    def __init__(self, page, spec):
        # no compund class names are allowed, at least for remote. TODO fix me
        assert (not re.compile('[\.\ ]').search(spec)), "Compound class name %r" % spec
        ByBase.__init__(self, page, spec)


class ByLinkText(ByBase):
    by = By.LINK_TEXT


class ByPartialLinkText(ByBase):
    by = By.PARTIAL_LINK_TEXT
