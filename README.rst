
======================================
Testaframe - Test Automation Framework
======================================

.. contents:: Table of Contents

Framework documentation
=======================

This README can be converted to html using the ``rst2html.py`` utility in docutils::

 sudo pip install docutils
 rst2html.py README.rst README.html


System configuration
--------------------
Testaframe can be used for driving Selenium tests and/or API/service tests.
Two of its main features are the ability to run tests on multiple OS/browsers
across multiple environments (e.g. localhost, CI, QA) at once,
and polling asserts, which is especially useful for testing Ajaxy web sites
and asynchronous services.

There is still a bit of work and documentation to do before this is all pretty and
easily used and learned by new people, but it is better to get it committed and public
rather than wait until it is perfect.

See ``*_test.py`` for examples of GUI and API tests.  Your tests
should go in ``wiki|sample_test.py`` or api_test.py.  You can rename them or add more files,
then modify the ``run_*.py`` files to use the new test files.

Required libraries
  see ``pip_requirements.txt``

You will need to create a personal ``my_cfg.py`` on your local machine by
using ``my_cfg_example.py`` as an example.
The ``my_cfg.py`` file should be .ignored in your source control.

Running the tests
~~~~~~~~~~~~~~~~~
The tests must be run inside nosetests using a specific ``run_*.py`` file.  For example 
``nosetests run_local.py``

Other useful nose options::

  -v shows the test names as they run
  -s shows output even if the test passes
  -m test_just_this_one  (-m has full regex matching)
  -a ThisAttribute

Helpful trick
~~~~~~~~~~~~~
While tests are running, the browser will be opening and closing and basically
making your desktop machine unusable for anything else.  So start up a VNC server
and a VNC viewer and then run the tests pointing to that display 
``DISPLAY=localhost:7 nosetests run_local.py -v``

The ``our_envs.py`` file will need to be customized for your project/company.

Files
~~~~~
Test files should end in ``_test.py`` if they should be discovered, and ``*_tst.py``
if they should not be discovered (e.g. ``base_tst.py``).

``base_tst.py``, ``base_page.py``, and ``locate.py`` should contain no project code for arch and F/OSS reasons.
``base_tst.py``, ``base_page.py``, and ``locate.py`` should be the only places with Selenium calls.
Ideally ``base_tst.py`` would not have any selenium code in it, but it seems
pretty tied into the polling asserts.

In a perfect world this framework could be completely seperated from user's test code
but we are not quite at that stage yet.

Classes
~~~~~~~
Test classes should start with ``Test`` and untimately inherit from ``TestCaseBase``.

Tests
~~~~~
Test functions should begin with ``test_``
Test functions should not have a doc string because the first line is used as
the test description (a pyunit oddity).  However a comment can be used safely.::

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

Test Data Builder Pattern
Briefly described at http://c2.com/cgi/wiki?TestDataBuilder
Which discussed by Steve Freeman at http://www.infoq.com/presentations/Sustainable-Test-Driven-Development

Many of the features were designed to make the logging output much easier to read
for less technical readers (e.g. managers, business people, manual testers).

There is the start to a Ruby implementation of Testaframe in the ``ruby/`` subdirectory.
There are pros and cons to each implementation, but the multiprocess support in
nosetests was a big factor in focusing on Python.


Howtos
------

The code is commented to try to connect these howto docs and the code.

Add another test case to an existing test class
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For this example we will add a test for a Wikipedia article with parentheses in the name.
We will use `Python_(programming_language)` as an example.

-  Go to ``wiki_test.py`` file
-  Find ``test_wikipedia()``
-  Copy the test, everything from the attribute descriptor [``@attr``]
   through the ``self.is_in()`` at the end of the test
-  Paste that below ``test_wikipedia()``
-  Change its name to ``test_article_with_parens``
-  Change ``article_to_use`` to ``Python_(programming_language)``
-  Save the test file
-  Run the test using ``run_local.py -s -v -m test_article_with_parens`` (the ``-s -v``
   are very useful during test development and debugging)
-  This fails because the title has slightly different punctuation than the normal article
   and we will have to account for that
-  For now let's just use the ``replace()`` method on ``article_to_use`` to change the ``_`` to a space
-  Enter ``article_title = article_to_use.replace('_',' ')``
-  Change the assert to use article title ``self.is_in(article_title, ...)``
-  Rerun the test
-  The test passed

We will leave the example this way, but the article and title manipulation should
be done in the Databuilder, which we will show later.

There is a small opportunity to reduce DRY here.
We could factor out the lines involving going to an article page and making sure the
title matches by making of another function in ``WikiTestGui`` called ``goto_wiki_article()``
which would go to the page and verify the title.



Add a locator to a page object
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Now we're going to add a locator to a page and then verify the element is on the page.

-  First go look at the `Wikipedia YAML <http://en.wikipedia.org/wiki/YAML>`_ page
-  Look at the footer, clear at the bottom of the page

Let's imagine we need to verify that an article page has the "Powered by MediaWiki" logo displayed.
We need to find something in the HTML that will help us verify and locate that item

-  In your browser do inspect element (right click, inspect element in Chrome and Firefox)
-  Notice that the anchor tag doen't have an ID, but the parent is ``<li id="footer-poweredbyico">``
-  We will use this as the basis of our locator
-  The locator will start with ``#footer-poweredbyico``. The ``#`` indicates its an ID see also: CSS locators
-  We don't want the list item, since it isn't clickable (which we will likely want to do some day),
   we want the actual anchor tag so add "`` a``" and it will find you the actual anchor
-  Go to the ``ArticlePage`` in ``wiki_pages.py`` and see ``_prep_finders()``
-  Make a new locator ``self.powered_by_link = self.by_css(#footer-poweredbyico a')``
-  Check if the locator if found on the page

-  Go to '`wiki_test.py`` and add to ``test_wikipedia()``
-  Add ``self.is_equal(True, article_page.powered_by.is_this_displayed)``
-  For this is example we will just see if it is `True`, if it's True then it is displayed
-  Notice there is no ``()`` after ``is_this_displayed``, this is explained, with examples,
   in ``sample_test.py`` in ``test_ajaxy``.  Since we are using ``is_equal`` here, it doesn't effect
   the test, but is good to get in the habit of passing functions to Testaframe's asserts.
-  For that matter, we probably should be using the polling assert version, ``try_is_in`` since
   there is no cost to doing so and it often is necessary based on how pages actually render.
-  Run the test



Add a function to a page object
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Let's create a function to use the search form in the top right corner of a Wikipedia article page
First let's write what we need for the test we want the test to read
article_page.do_search, with the parameter being the search term,
and this should return another article page object.

-  Go to ``test_wikipedia.py`` and create a new test method based on ``test_wikipedia()``
-  Add the search part ``new_article_page = self.article_page.do_search(search_term)``
-  Add the verification part ``self.is_in(search_term, new_article_page.get_title)``

The naming convention is ``do_*()`` (e.g. ``do_login()``) which means perform an action
which will result in you being taken to a new page, like searching behaves here.
The other convention is to use ``goto_*()`` (e.g. ``goto_edit_page()``)  were
the point is to trust that a simple click on a link or a button on the current page
will take you somewhere new.

We see how we want the test to look so let's add the ``do_search`` function on the article page
This will take one parameter which is the search term
Now we need to know the locator so we can type the search term into the search box

-  In your browser go to an article page and choose inspect element on the search box
-  In this case the ID for that is ``searchInput`` so we will create a new locator
   using ``#searchInput``
-  Next we type something into the search using ``self.type_into(self.search_input, search_term)``

Then we need to submit the form. The ``input`` tag is a child of ``#searchform``

-   We need a new locator ``self.search_form = self.by_css('#searchform')``
-  Add to ``do_search`` so it submits the form

When the form has been submitted we will wind up on a different article page.

-  So we must do ``return self.now_on(ArticlePage)``.

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

-  Create a link text variable
-  Create the locator using by_link_text
-  Add the ``click_on`` for the ``mobile_view_link`` to ``goto_mobile_view()``
-  After we have clicked on this we will be on new page so we must tell Testaframe
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
