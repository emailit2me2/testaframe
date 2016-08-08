"""
To add new test files:
- add to imports
- add to the appropriate test array (i.e add gui tests to gui_tests)
    - add in the same order as imports to aid in readability

runner.check_no_missing_files uses this file to verify all tests are added correctly and allows tests to be picked
    up and run
"""

import test_gui.sample_test
import test_gui.wiki_test
import test_api.email_test
import test_api.self_test
import test_api.wikipedia_test

# TODO remove DRY ^v somehow
gui_tests = [test_gui.sample_test, test_gui.wiki_test, ]

api_tests = [test_api.email_test, test_api.self_test, test_api.wikipedia_test, ]

