
======================================
Testaframe - Test Automation Framework
======================================

.. contents:: Table of Contents


Overview
--------

Testaframe can be used for driving Selenium tests and/or API/service tests.
Two of its main features are the ability to run tests on multiple OS/browsers
across multiple environments (e.g. localhost, CI, QA) at once,
and polling asserts, which is especially useful for testing Ajaxy web sites
and asynchronous services.

There is still a bit of work and documentation to do before this is all pretty and
easily used and learned by new people, but it is better to get it committed and public
rather than wait until it is perfect.

This README can be converted to html using the ``Makefile``

.. code::

 sudo pip install docutils  # if not already installed
 make docs

Getting started
---------------

System configuration
~~~~~~~~~~~~~~~~~~~~

You will need Python 2.7 installed.

Clone the `testall repo <https://github.com/seomoz/testall>`_ to your local box.

Required libraries (optional packages are commented out) in ``pip_requirements.txt``
Install them using

.. code::

 sudo pip install -r pip_requirements.txt

You will need to create a personal ``my_cfg.py`` on your local machine by
using ``my_cfg_example.py`` as an example.  Create one using

.. code::

 cp my_cfg_example.py my_cfg.py

The ``my_cfg.py`` file should be .ignored in your source control.

Running the tests
~~~~~~~~~~~~~~~~~
The tests must be run inside nosetests using a specific ``run_*.py`` file.  For example

.. code::

 nosetests run_local.py -s -v -a Wiki

will run all the Wikipedia tests in ``wiki_test.py``.

Other useful nose options::

  -v shows the test names as they run
  -s shows output even if the test passes
  -m test_just_this_one  (-m has full regex matching)
  -a ThisAttribute

The selenium source repository contains many html pages that are used by the Selenium
self tests to test various features of Selenium itself.  We can use these pages to
show more features of Testaframe.  Look in ``sample_test.py`` for the examples.

To run the the "Sample" tests you will need to

#.  Clone the `selenium repo <https://code.google.com/p/selenium/>`_ locally
#.  Open a terminal and ``cd`` to ``selenium/common/src/web``
#.  Start a simple http server then run the tests

.. code::

 python -m SimpleHTTPServer 8000
 nosetests run_local.py -s -v -a Sample

The ``test_ajaxy`` method in ``sample_test.py`` documents, in detail, several of the key
features, options, and gotchas when working with Testaframe, Selenium and especially
pages containing Ajax.  You can run it using

.. code::

 nosetests run_local.py -s -v -m test_ajaxy


Testaframe can also be used for API or service tests.  Examples are in ``api_test.py``
Run them using

.. code::

 nosetests run_local.py -s -v -a Api


Helpful trick
~~~~~~~~~~~~~
While tests are running, the browser will be opening and closing and basically
making your desktop machine unusable for anything else.  So start up a VNC server
and a VNC viewer and then run the tests pointing to that display

.. code::

 DISPLAY=localhost:7 nosetests run_local.py -v

Files
~~~~~
See ``*_test.py`` for examples of GUI and API tests.  Your tests
should go in ``wiki|sample_test.py`` or ``api_test.py``.  You can rename them or add more files,
then modify the ``run_*.py`` files to use the new test files.

Test files should end in ``_test.py`` if they should be discovered, and ``*_tst.py``
if they should not be discovered (e.g. ``base_tst.py``).

``base_tst.py``, ``base_page.py``, and ``locate.py`` should contain no project code for arch and F/OSS reasons.
``base_tst.py``, ``base_page.py``, and ``locate.py`` should be the only places with Selenium calls.
Ideally ``base_tst.py`` would not have any selenium code in it, but it seems
pretty tied into the polling asserts.

The ``our_envs.py`` file will need to be customized for your project/company.

In a perfect world this framework could be completely separated from user's test code.
but we are not quite at that stage yet.

Classes
~~~~~~~
Test classes should start with ``Test`` and untimately inherit from ``TestCaseBase``.

Tests
~~~~~
Test functions should begin with ``test_``
Test functions should not have a doc string because the first line is used as
the test description (a pyunit oddity).  However a comment can be used safely.

.. code::

 def test_name_problem(self):
   '''messes up the test description'''
 def test_name_ok(self):
   # This does not obscure the test name

Test attributes should be in initcap format (e.g. ``AttribName``) so we have no
name collisions with PEP8 functions names (e.g. func_name) or constants (e.g. ``CONSTANT``).
It appears the Nose Attrib plugin supports special chars (e.g. ``@attr('attrib:12')``)
but let's not use that unless we need to.

Utility methods in test classes need leading underscores (e.g. ``_util_func()``)
so nosetest will not automatically 'discover' them.
There are also nosetest decorators for ``nottest`` and ``istest``, but let's not use
them unless we need to.

If you have a test case management system (e.g. SpiraTest) you can use
attributes to connect test functions to test cases.  If this won't work for some
reason you can try the Spira standard of ``def test_func_name__<test id>()``.
Putting attributes in the test function is less desirable because to get inside the
test function the setup must be run which launches a browser.

Asserts, polling and non-polling
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Testaframe provides polling asserts.  In fact, polling asserts and configuration injection
are its two main features.  These methods begin with ``try_``
(e.g. ``try_is_equal``, ``try_is_in``).  They are used in cases where the item(s)
might not be in the DOM yet or where the value might change without a page reload.
Imagine clicking the Follow button on a Twitter `profile <https://twitter.com/SeleniumHQ>`_ page.
The # of followers should increment but the page won't reload.
Also, sometimes the element doesn't exist in the DOM yet.  For instance you have
to pick a Country in a menu (e.g. US, Canada) and then another menu will appear
(e.g. States or Provinces respectively. So you have to wait for the second element to
appear and then make sure it is correct.


Runners
~~~~~~~
The ``run_*.py`` files use the "execute the config" design pattern.  This is partly because
you can't inject command line parameters into unit tests.
You usually want one test function to run on multiple different OS/Browser combinations
against multiple different environments (e.g. CI, QA, localhost, Staging, Prod).
So the use of mixins allows the selected combinations to be added to dynamically
generated classes that get discovered by nose.

Only a default version of ``run_local.py`` should be checked in, since it is intended
to be changed often as tests are developed and debugged.

Driving Browsers
~~~~~~~~~~~~~~~~
Firefox has Selenium support built in.  But Chrome and IE require an external driver.
There is a list on the `SeleniumHQ download`_ page

Additional information
----------------------

Target readers
~~~~~~~~~~~~~~

The target users (or user functions) of the framework and target readers are:

- Framework developer (feature work on the framework itself)
- Sr SDET (adding major company specific stuff)
- Test automator (creating, writing, and maintaining tests and pages)
- Helpers (adding to tests and pages (e.g. support team, manual testers))
- Domain expert (reads and audits the tests)

Notice the programming skill goes down as you go down the list.
The domain expertise likely goes up as you go down the list.



What these docs are and are not
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
- Are

  - An explanation and description of what features are included, how they are coded,
    and how to use them.
  - An explanation of how to create tests, pages, and framework features.

- Are not

  - Not a tutorial on testing or test automation
  - Not a tutorial on Selenium or web technologies


Knowledge assumed
~~~~~~~~~~~~~~~~~

- A working knowledge of Python is required.  However, the further down the list
  of target users, the less Python is required.  Considerable effort was put into
  the framework to make the tests as readable as possible for non-technical domain experts
  including Product Manager and CxO's.  See also: the Page Object pattern discussion below.
- A general understanding of HTML and CSS is needed for creating locators and
  knowing how to exercise the functionality on a page.
- A working knowledge of unit testing patterns is essential for SDET's and framework developers.
  See `Testing resources`_ below
  
  The Pragmatic Programmers also have an excellent book titled "Pragmatic Unit Testing
  in Java with JUnit".  Although it is currently out of print, many copies are available
  via Amazon, etc.

- OOP - Object Oriented Programming
- DRY - Don't Repeat Yourself
- Test automation
- Domain knowledge

Testing resources
~~~~~~~~~~~~~~~~~

- `Testing Heuristics Cheatsheet`_ (pdf)
- `jUnit Summary Card`_ (pdf)
- The `xUnit Patterns`_ site is an excellent resource.
  `xUnit Patterns`_ is the seminal work in that area.  The author, Gerard Meszaros, published drafts
  of the book as he was writing.  Those drafts are still available for viewing online,
  and his excellent book is available for purchase there as well.

I printed out the 2 PDF's, and they sit on the desk between my monitors.
I refer to them many times a week.  I also write on mine as I find new things to test.
For instance, we had a user who chose a user name of ``0123`` and Javascript interpreted that
as not only a number but an octal number, so I hand wrote that on my sheet.

.. _xUnit Patterns: http://xUnitPatterns.com
.. _jUnit: http://pragprog.com/book/utj/pragmatic-unit-testing-in-java-with-junit
.. _jUnit Summary Card: http://media.pragprog.com/titles/utj/StandaloneSummary.pdf
.. _Testing Heuristics Cheatsheet: http://testobsessed.com/wp-content/uploads/2011/04/testheuristicscheatsheetv1.pdf


Polling
~~~~~~~

Polling is the answer for how to get your tests to run quickly and reliably.
When a test needs to wait for something to happen, people often use some kind
of ``sleep`` or ``wait``.
Adding ``sleeps`` to your tests makes them slower than necessary, because the sleep needs
to be longer than the maximum time the event could take to complete.  But
how long is that going to be.  In the case of ``test_ajaxy``, we know the page has
Javascript that delays 5 seconds after submitting the form.  But if we put a ``5.0`` second
delay in our test, we will have a race condition, because the Javascript delay isn't
a guaranteed precise ``5.0`` seconds since it is just a web page, not an airplane
control system.  So we would need to wait a little longer in the test, say ``5.1`` seconds.
But if you run the tests 100 times, it will still probably fail at least once.  And if
you had 100 tests, each failing 1% of the time, you have a really unreliable system.

So the solution is to poll periodically.  In the case of GUI tests you need to wait for:

- the element(s) to exist in the DOM
- the assert to pass

Other reasons to poll are waiting for:

- an email to arrive in an inbox
- an API to respond
- a service to come up


Logging
~~~~~~~
Many of the features were designed to make the logging output much easier to read
for less technical readers (e.g. managers, business people, manual testers).

Beginning Ruby version
~~~~~~~~~~~~~~~~~~~~~~
There is the start to a Ruby implementation of Testaframe in the ``ruby/`` subdirectory.
There are pros and cons to each implementation, but the multiprocess support in
nosetests was a big factor in focusing on Python.

.. _SeleniumHQ download: http://seleniumhq.org/download
.. _C2: http://c2.com/cgi/wiki?TestDataBuilder
.. _video: http://www.infoq.com/presentations/Sustainable-Test-Driven-Development

Howtos
------

The code is commented to try to connect these howto docs and the code.

Add another test case to an existing test class
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For this example we will add a test for a Wikipedia article with parentheses in the name.
We will use `Python_(programming_language)` as an example.

#.  Go to ``wiki_test.py`` file
#.  Find ``test_wikipedia()``
#.  Copy the test, everything from the attribute descriptor [``@attr``]
    through the ``self.is_in()`` at the end of the test
#.  Paste that below ``test_wikipedia()``
#.  Change its name to ``test_article_with_parens``
#.  Change ``article_to_use`` to ``Python_(programming_language)``
#.  Save the test file
#.  Run the test using ``run_local.py -s -v -m test_article_with_parens`` (the ``-s -v``
    are very useful during test development and debugging)
#.  This fails because the title has slightly different punctuation than the normal article
    and we will have to account for that
#.  For now let's just use the ``replace()`` method on ``article_to_use`` to change the ``_`` to a space
#.  Enter ``article_title = article_to_use.replace('_',' ')``
#.  Change the assert to use article title ``self.is_in(article_title, ...)``
#.  Rerun the test
#.  The test passed

We will leave the example this way, but the article and title manipulation should
be done in the Databuilder, which we will show later.

There is a small opportunity to reduce DRY here.
We could factor out the lines involving going to an article page and making sure the
title matches by making of another function in ``WikiTestGui`` called ``goto_wiki_article()``
which would go to the page and verify the title.


How to read the output of a successful test
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

We will use log output of ``test_search_success`` as our example.

With run_local.py using browser ``Local_FF``, run the test with logging turned on.

.. code::

  nosetests run_local.py -s -v -m test_search_success

Which should result in roughly the following log output.

.. code::

  run_local.wiki_test_Local_FF_on_Localhost_TestWikiGui.test_search_success
  Setting highlight delay to 0
  Setting poll max to 10
  Setting poll delay to 0.1
  Making a platform specific page: ArticlePageFF
  Created page object ArticlePageFF
  Going to get 'http://wikipedia.org/wiki/YAML'
  Current url u'http://en.wikipedia.org/wiki/YAML' /wiki/YAML
  Verifying ArticlePageFF path pattern '^/wiki/.*$' matches u'/wiki/YAML'
  find element 'verify_element' using css selector='.collapsible-nav'
       !! waiting 1 second(s) because stupid wait due to stale element problems !!
  find element 'powered_by_link' using css selector='#footer-poweredbyico a'
      Is 'powered_by_link' using css selector='#footer-poweredbyico a' displayed?: True
    True: True ?== True
  PASS: True == True
  find element 'search_input' using css selector='#searchInput'
  type into 'search_input' using css selector='#searchInput' = 'XML'
  find element 'search_form' using css selector='#searchform'
  submit form
  on page ArticlePage
  Making a platform specific page: ArticlePageFF
  Created page object ArticlePageFF
  Current url u'http://en.wikipedia.org/wiki/XML' /wiki/XML
  Verifying ArticlePageFF path pattern '^/wiki/.*$' matches u'/wiki/XML'
  find element 'verify_element' using css selector='.collapsible-nav'
       !! waiting 1 second(s) because stupid wait due to stale element problems !!
  Now on ArticlePage with window_name main
  Current title u'XML - Wikipedia, the free encyclopedia'
    True: 'XML' ?in u'XML - Wikipedia, the free encyclopedia'
  PASS: 'XML' in u'XML - Wikipedia, the free encyclopedia'
  ok

  ----------------------------------------------------------------------
  Ran 1 test in 11.054s

  OK

The first thing shown is the test title which has the runner name, in this case ``run_local``,
the test file (i.e. ``wiki_test.py``), the OS/browser chosen, in this case ``Local_FF``
(i.e. Firefox running on the local box), on what environment (``Localhost``),
the test class name (i.e. ``TestWikiGui``) and finally the test method name itself
(i.e. ``test_search_success``).

The environment of ``Localhost`` is a little strange here, because we are actually
hitting ``wikipedia.org``.  But the example tests need to be able to run with limited
setup by new users.  If you look in ``our_envs.py``, in the ``LOCALHOST_ENV`` section,
you will see a comment that this is set up with some real live sites for demo purposes.

The next thing is setting default values for highlight delay, polling max, and polling delay

This was all been preparatory work before we got to the first real line of the test
which is ``start.at`` the ``ArticlePage``.

It creates a platform specific page, ``ArticlePageFF``, showing the platform suffix feature,
then it tells you that it created the page object, ``ArticlePageFF``.
If you used ``Local_Chrome`` or any of the other browsers it would just say
created page object ``ArticlePage`` (see also page object platform suffix elsewhere).

The page object is created, now we go get the web page with Selenium.
Go get the actual web page.
The current URL ``wikipedia.org/wiki/YAML``, and the second value there is the just the path
``/wiki/YAML``.
Then ``verify_on_page`` does its work.
It sees the current URL, verifying that the path pattern, in this case ``/wiki/<anything>``, matches
then it attempts to locate the ``verify_element``, in this case using the css selector ``.collapsible-nav``.
There are sometimes problems with stale page elements during page transitions
so there is currently a brief delay to account for that.

Then we begin the real portion of the test.
In this case we are checking to see if the ``powered_by_link`` is displayed.
Yes it is.
so the text frame find the element ``powered_by_link`` using that CSS selector
then it's settled
then it tells you it's doing a check if powered_by_link using CSS selector, is displayed,
it tells you the value of that (i.e. True)
then the following line shows you that it is true that True is equal to True.
That is a little confusing, there is another example at the end of that test which is more clear.

Then it tells you the assert passed.
Many of the assert frameworks will only show you if things fail, but Testaframe
was designed to have better logging to show you precisely what it is checking and what the results are.
This creates better trust among non-coders as well as really easy to read repro steps.

Next we want to perform the do_search
We go find the ``search_input`` element and type into the element the value ``"XML"``.
Then we find the ``search_form`` element and submit the form.

The new page should be another ``ArticlePage`` (again it makes a platform specific page).
The page object is created and the current URL is now ``/wiki/XML``.
Verify that, yes, that's still a match and the ``verify_element`` is correct.

Now we're on the ``ArticlePage`` with ``window_name`` of ``main``.
There is functionality for handling pages (pages opening in other tabs and windows).
See also multiple windows/tab handling.

Then we verify that the ``search_term`` is in the title, so we get the current title
which is ``"XML - Wikipedia..."`` we check if ``"XML" ?in "XML Wikipedia..."``.
And we see the successful result of the assert.

The ``"ok"`` is from the test framework saying that the test passed.

Then it displays the number of tests that ran and how long they took.


How to read log output containing polling
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

How polling element finding and asserts look in the logs.  The ``test_ajaxy`` method
makes extensive use of both.  Let's examine the log snippet below.  You can run
the test yourself (after some prep work described in the ``test_ajaxy`` doc string)
by running the following:

.. code::

  nosetests run_local.py -s -v -m test_ajaxy


Which should result in roughly the following log output (with some non-essential lines removed).

.. code::

  ...
  find element 'new_label_field' using name='typer'
  type into 'new_label_field' using name='typer' = u'15a3e383'
  find element 'new_label_form' using css selector='form'
  submit form
  Setting highlight delay to 1
  find element 'new_labels' using css selector='.label'
    Waiting for element:  1.02 secs
    Waiting for element:  2.14 secs
    Waiting for element:  3.26 secs
    Waiting for element:  4.38 secs
    True: u'883bedca' ?== u'883bedca'
  PASS: u'883bedca' == u'883bedca'
  Setting highlight delay to 0
  find element 'new_label_field' using name='typer'
  type into 'new_label_field' using name='typer' = u'304b0eb4'
  find element 'new_label_form' using css selector='form'
  submit form
  find elements 'new_labels' using css selector='.label'
    found 1 element(s)
    False: [u'883bedca', u'304b0eb4'] ?== [u'883bedca']
    Waiting for try_is(==):  0.02secs
  find elements 'new_labels' using css selector='.label'
    found 1 element(s)
    False: [u'883bedca', u'304b0eb4'] ?== [u'883bedca']
    Waiting for try_is(==):  0.15secs
  find elements 'new_labels' using css selector='.label'
    found 1 element(s)
    False: [u'883bedca', u'304b0eb4'] ?== [u'883bedca']
    Waiting for try_is(==):  0.26secs
  ...
  find elements 'new_labels' using css selector='.label'
    found 1 element(s)
    False: [u'883bedca', u'304b0eb4'] ?== [u'883bedca']
    Waiting for try_is(==):  4.92secs
  find elements 'new_labels' using css selector='.label'
    found 2 element(s)
    True: [u'883bedca', u'304b0eb4'] ?== [u'883bedca', u'304b0eb4']
  PASS: [u'883bedca', u'304b0eb4'] == [u'883bedca', u'304b0eb4']
           attribute 'class' for 'new_labels' using css selector='.label'
  find elements 'new_labels' using css selector='.label'
    found 2 element(s)
    True: 'label' ?== u'label'
  PASS: 'label' == u'label'
  ...

The sample page ``ajaxy_page.html`` has a form, where you type in a new "label" and submit
the form.  Then some javascript code embedded in the page, waits 5 seconds and then places the
previously entered label text into the DOM.

The ``test_ajaxy`` method exercises this page by

#. Entering a label and submitting the form
#. Waiting to make sure the list of labels is equal to the entered label

   a.  Although for the list of labels to be equal, the labels must first show up in the DOM (i.e. ``Waiting for element:...``)
   #.  The ``find_all`` method has to wait for 5 seconds for the ``/label`` element to appear asserting the label text matches

#. Entering a second label and submitting the form
#. For this assert, there is already one ``.label`` element, so it only has to wait the 5 seconds
   for the assert on the values to pass.


How to read log output containing failures
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

We can force a test failure by uncommenting the following line in ``test_wikipedia``.

.. code::

  self.is_in(article_to_use+'-FORCE FAILURE FOR DEMO PURPOSES', article_page.get_title)

If you run ``test_wikipedia`` with that line enabled and the ``-s`` option
you should see roughly the following log output.  Without the ``-s`` option the
traceback portion will display first, followed by the log output.

.. code::

  run_local.wiki_test_Local_FF_on_Localhost_TestWikiGui.test_wikipedia
  Setting highlight delay to 0
  Setting poll max to 10
  Setting poll delay to 0.1
  Making a platform specific page: ArticlePageFF
  Created page object ArticlePageFF
  Going to get 'http://wikipedia.org/wiki/YAML'
  Current url u'http://en.wikipedia.org/wiki/YAML' /wiki/YAML
  Verifying ArticlePageFF path pattern '^/wiki/.*$' matches u'/wiki/YAML'
  find element 'verify_element' using css selector='.collapsible-nav'
       !! waiting 1 second(s) because stupid wait due to stale element problems !!
  Current title u'YAML - Wikipedia, the free encyclopedia'
    True: 'YAML' ?in u'YAML - Wikipedia, the free encyclopedia'
  PASS: 'YAML' in u'YAML - Wikipedia, the free encyclopedia'
  Current title u'YAML - Wikipedia, the free encyclopedia'
    False: 'YAML-FORCE FAILURE FOR DEMO PURPOSES' ?in u'YAML - Wikipedia, the free encyclopedia'
  FAIL

  ======================================================================
  FAIL: run_local.wiki_test_Local_FF_on_Localhost_TestWikiGui.test_wikipedia
  ----------------------------------------------------------------------
  Traceback (most recent call last):
    File "/usr/local/lib/python2.7/dist-packages/nose/nose/case.py", line 197, in runTest
      self.test(*self.arg)
    File "/home/markg/real/Testaframe/wiki_test.py", line 32, in test_wikipedia
      self.is_in(article_to_use+'-FORCE FAILURE FOR DEMO PURPOSES', article_page.get_title)
    File "/home/markg/real/Testaframe/base_tst.py", line 161, in is_in
      self.is_op(a, lambda a,b: a in b, 'in', b, msg, only_if)
    File "/home/markg/real/Testaframe/base_tst.py", line 72, in is_op
      ret = ok_(op(a,b), "FAIL: %r not %s %r" % (a, sym, b))
  AssertionError: FAIL: 'YAML-FORCE FAILURE FOR DEMO PURPOSES' not in u'YAML - Wikipedia, the free encyclopedia'

  ----------------------------------------------------------------------
  Ran 1 test in 7.229s

  FAILED (failures=1)

You can see the failing assert in the middle of the above log snippet,
just above the ``FAIL`` at the bottom of the log output.

Then it displays the failure, in this case an ``AssertError``. The assert message tells
exactly what condition was not met.  In this case it is easy to see what the error is.
But if the error were ``AssertionError: FAIL: 1 not == 2`` it isn't as obvious.
By following the coding convention of always putting the expected value first in an
assert, followed by the actual result, the output is much more understandable.

Good variable naming in the test makes the traceback more readable. as well.  In the middle
of the traceback, the assert line (i.e. ``self.try_is_in``) is displayed.

.. code::

  self.is_in(article_to_use+'-FORCE FAILURE FOR DEMO PURPOSES', article_page.get_title)

Ignoring the ``FORCE FAILURE...`` portion, the above line, and thus the ``AssertionError`` message,
are quite understandable (i.e. the article to use should have been in the page title)
even with no other context.

You can also see a coding error assert by enabling the following line in ``test_wikipedia``.

.. code::

  self.is_in(article_to_use, article_page.FAIL_CUZ_THIS_FUNCTION_DOES_NOT_EXIST)


Info available to aid bug reporting and debugging
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

There are several things available for reporting and reproducing a bug:

-  The logging output shows precisely what is happening in terms of actions performed by
   Selenium, assert attempts, and any other information you choose to print out.
   Datetimestamps could be helpful in some cases, but are currently not part of the
   logging process.  However, they could be added quite quickly.
-  Different environments and/or OS/Browser combinations to use as comparisons.
-  Screenshots and HTML can be captured upon test completion.  You can also do captures mid-test
   using ``env_save_snapshot``.
-  Element highlighting, although mostly for test development, aids in understanding exactly
   how the test is interacting with the SUT.
-  Although external to Testaframe, ``vnc2swf`` can be used to capture full videos of test runs.


Add a locator to a page object
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Now we're going to add a locator to a page and then verify the element is on the page.

#.  First go look at the `Wikipedia YAML <http://en.wikipedia.org/wiki/YAML>`_ page
#.  Look at the footer, clear at the bottom of the page

    Let's imagine we need to verify that an article page has the "Powered by MediaWiki" logo displayed.
    We need to find something in the HTML that will help us verify and locate that item

#.  In your browser do inspect element (right click, inspect element in Chrome and Firefox)
#.  Notice that the anchor tag doen't have an ID, but the parent is ``<li id="footer-poweredbyico">``
#.  We will use this as the basis of our locator
#.  The locator will start with ``#footer-poweredbyico``. The ``#`` indicates its an ID see also: CSS locators
#.  We don't want the list item, since it isn't clickable (which we will likely want to do some day),
    we want the actual anchor tag so add "`` a``" and it will find you the actual anchor
#.  Go to the ``ArticlePage`` in ``wiki_pages.py`` and see ``_prep_finders()``
#.  Make a new locator ``self.powered_by_link = self.by_css(#footer-poweredbyico a')``
#.  Check if the locator if found on the page

#.  Go to '`wiki_test.py`` and add to ``test_wikipedia()``
#.  Add ``self.is_equal(True, article_page.powered_by.is_this_displayed)``
#.  For this is example we will just see if it is `True`, if it's True then it is displayed
#.  Notice there is no ``()`` after ``is_this_displayed``, this is explained, with examples,
    in ``sample_test.py`` in ``test_ajaxy``.  Since we are using ``is_equal`` here, it doesn't effect
    the test, but is good to get in the habit of passing functions to Testaframe's asserts.
#.  For that matter, we probably should be using the polling assert version, ``try_is_in`` since
    there is no cost to doing so and it often is necessary based on how pages actually render.
#.  Run the test



Add a function to a page object
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Let's create a function to use the search form in the top right corner of a Wikipedia article page
First let's write what we need for the test we want the test to read
article_page.do_search, with the parameter being the search term,
and this should return another article page object.

#.  Go to ``test_wikipedia.py`` and create a new test method based on ``test_wikipedia()``
#.  Add the search part ``new_article_page = self.article_page.do_search(search_term)``
#.  Add the verification part ``self.is_in(search_term, new_article_page.get_title)``

    The naming convention is ``do_*()`` (e.g. ``do_login()``) which means perform an action
    which will result in you being taken to a new page, like searching behaves here.
    The other convention is to use ``goto_*()`` (e.g. ``goto_edit_page()``)  were
    the point is to trust that a simple click on a link or a button on the current page
    will take you somewhere new.

    We see how we want the test to look so let's add the ``do_search`` function on the article page
    This will take one parameter which is the search term
    Now we need to know the locator so we can type the search term into the search box

#.  In your browser go to an article page and choose inspect element on the search box
#.  In this case the ID for that is ``searchInput`` so we will create a new locator
    using ``#searchInput``
#.  Next we type something into the search using ``self.type_into(self.search_input, search_term)``

    Then we need to submit the form. The ``input`` tag is a child of ``#searchform``

#.  We need a new locator ``self.search_form = self.by_css('#searchform')``
#.  Add to ``do_search`` so it submits the form

    When the form has been submitted we will wind up on a different article page.

#.  So we must do ``return self.now_on(ArticlePage)``.

    Even though we're on an article page and going to another article page, we still must
    return a new ``ArticlePage`` object because of the way Selenium works.
    It pulls the rug out from under your page objects (due to the asynchronous nature
    of how Selenium interacts with the browser, it is really like an Observer pattern).
    So in order to avoid that we don't want to accidentally use an old page so when
    you go to a new page Testaframe obsoletes the previous page, thus protecting you
    from possible errors on the test side.

Now let's go back to the test and make sure  the search term is in the page
to verify that we successfully went to the search term's page.

Note when creating locators: you should generally search by CSS locators,
for performance (especially on IE), maintainability, and readability reasons.
It is common to have to switch between ID's, css classes, or an ID/class plus a tag game, so
the easiest thing to do is just use by_css() when defining a locator.
In this test our search will be successful and we will be taken to another article page.
Other searches may not be successful, so we may wind up with two search functions:
`do_search` and the other ``do_search_unsuccessful`` or ``do_search_fail`` which returns
a different page object.  You also see this pattern with logins: ``do_login_success``
and ``do_login_fail`` often take you to different pages.
Your test will know the difference in what's going to happen, of course, but you often
have to create two separate functions to make this happen.

This brings up an important point when naming test methods.  If you name one ``test_login``
and another ``test_login_no_password``, then if you try to run just ``test_login``
with ``run_local.py -m test_login`` you will get both tests since ``-m`` does
a regular expression match.  So it is better to name it ``test_login_success``.
Use increasing specificity from left to right (e.g.
``test_login_username_with_punctuation_success``)



Add a new page class
~~~~~~~~~~~~~~~~~~~~

For this example let's use the mobile view link from the footer of a Wikipedia article to
switch to the mobile version of the page we're on.
Let's add a new page class, and a function to the old page to go to mobile view.
No parameters are required for this function.

Inside the function we will want to click on the mobile view link.
We'll have to create the mobile link locator and we will access it by link text
We will use a class variable for the text of the link.

In general strings shouldn't be hard coded into tests or into page functions.
They should generally be class variables of the page class, sometimes as Constants,
as is the case here, and other times as templates (e.g. ``"Welcome, %(username}s"``).
These link text variables, expecially templates, are often used in the tests.

#.  Create a link text variable
#.  Create the locator using by_link_text
#.  Add the ``click_on`` for the ``mobile_view_link`` to ``goto_mobile_view()``
#.  After we have clicked on this we will be on new page so we must tell Testaframe
    we are on a new page using ``self.now_on`` and the mobile page class

In this case we can reuse some of the items from ``ArticlePage`` (e.g. ``PAGE_RE``,
``PAGE_SUB``) and likely more in a real world page class.

Create a ``MobileArticlePage`` which inherits from ``ArticlePage``.  This is just an example,
so we can ignore the extra locators and functions ``MobileArticlePage`` will have available.
In a real project we would probably create a ``StdWikiPage`` that both ``ArticlePage``
and ``MobileArticlePage`` inherited from.

We will need a ``_prep_finders()`` in the new page.  Make sure to change the parent class
in the call to the parent class's ``_prep_finders()``.

We will also need a new ``verify_element``.  Every page needs a unique ``verify_element``
to help ensure we are on the correct page.  Sometimes if a test or the site under test
doesn't work as expected, we will be expecting to be on one page, when in fact we
are on a different page.  When this happens it can be very confusing to understand
what the logs are telling you.  Testaframe helps to catch these cases by verifying
the current URL matches the ``PAGE`` variable and it also checks the DOM to find
the ``verify_element``.

We need to find an element in the mobile view page that is unique to mobile and not on
the desktop article page.  For this case it appears the expandable sections available
only on the mobile page use the ``section_heading`` class.  We should also notice
that our initial choice of ``.mediaWiki`` for the ``verify_element`` for ``ArticlePage``
was too generic.  So we really should change it to something better like ``.collapsible-nav``
which is the class for the left side pane in desktop view.  This is a very common issue
as the tests and site evolve.
