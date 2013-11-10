
Testaframe
======

Test Automation Framework documentation

Testaframe can be used for driving Selenium tests and/or API/service tests.
Two of its main features are the ability to run tests on multiple OS/browsers
across multiple environments (e.g. localhost, CI, QA) at once,
and polling asserts, which is especially useful for testing Ajaxy web sites
and asynchronous services.

There is still a bit of work and documentation to do before this is all pretty and
easily used and learned by new people, but it is better to get it committed and public
rather than wait until it is perfect.

See gui_test.py and api_test.py for examples of GUI and API tests.  Your tests
should go in gui_test.py and/or api_test.py.  You can rename them or add more files,
then modify the run_*.py files to use the new test files.

Required libraries
  see pip_requirements.txt

Running the tests
The tests must be run inside nosetests using a specific run_*.py file.  For example
  nosetests run_local.py
Other useful nose options:
  -v shows the test names as they run
  -s shows output even if the test passes
  -m test_just_this_one  (-m has full regex matching)
  -a ThisAttribute

Helpful trick
While tests are running the browser will be opening and closing and basically
making your desktop machine unusable for anything else.  So start up a VNC server
and a VNC viewer and then run the tests pointing to that display.
  DISPLAY=localhost:7 nosetests run_local.py -v

Files
Test files should end in _test.py if they should be discovered, and _tst.py
if they should not be discovered (e.g. base_tst.py).

base_tst.py, base_page.py, and locate.py should contain no project code for arch and F/OSS reasons.
base_tst.py, base_page.py, and locate.py should be the only places with Selenium calls.
Ideally base_tst.py would not have any selenium code in it, but it seems
pretty tied into the polling asserts.

In a perfect world this framework could be completely seperated from user's test code
but we are not quite at that stage yet.

Classes
Test classes should start with Test and untimately inherit from TestCaseBase

Tests
Test functions should begin with 'test_'
Test functions should not have a doc string because the first line is used as
the test description (a pyunit oddity).  However a comment can be used safely.
 def test_name_problem(self):
   '''messes up the test description'''
 def test_name_ok(self):
   # This does not obscure the test name

Test attributes should be in initcap format (e.g. AttribName) so we have no
name collisions with PEP8 functions names (e.g. func_name) or constants (e.g. CONSTANT).
It appears the Nose Attrib plugin supports special chars (e.g. @attr('attrib:12'))
but let's not use that unless we need to.

Utility methods in test classes need leading underscores (e.g. _util_func())
so nosetest will not automatically 'discover' them.
There are also nosetest decorators for nottest and istest, but let's not use
them unless we need to.

If you have a test case management system (e.g. SpiraTest) you can use
attributes to connect test functions to test cases.  If this won't work for some
reason you can try the Spira standard of def test_func_name__<test id>().
Putting attributes in the test function is less desirable because to get inside the
test function the setup must be run which launches a browser.

Runners
The run_*.py files use the "execute the config" design pattern.  This is partly because
you can't inject command line paramaters into unit tests.
You want one test function to run on multiple different OS/Browsers combinations
against multiple different environments(e.g. CI, QA, localhost, Staging, Prod).
So the use of mixins allows the selected combinations to be added to dynamically
generated classes that get discovered by nose.

Only a default version of run_local.py should be checked in, since it is intended
to be changed often as tests are developed and debugged.

Test Data Builder Pattern
  Briefly described at http://c2.com/cgi/wiki?TestDataBuilder
  Which discussed by Steve Freeman at http://www.infoq.com/presentations/Sustainable-Test-Driven-Development

Many of the features were designed to make the logging output much easier to read
for less technical readers (e.g. managers, business people, manual testers).


