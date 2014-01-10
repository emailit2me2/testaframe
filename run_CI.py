#!/usr/bin/env nosetests
assert __name__ != '__main__', "Must be run with nosetests"

import runner
import env

import gui_test
import api_test
# TODO remove DRY ^v somehow
gui_tests = [gui_test,]
api_tests = [api_test,]

environments = [
#  'Localhost',
#  'Staging',
#  'Dev',
  'CI',
#  'QA',
  ]
browsers = [
#  'Local_FF',
  'Local_Chrome',
#  'Local_IE',
#  'Linux_FF',
#  'Linux_Chrome',
#  'OSX_FF',
#  'OSX_Chrome',
#  'IPhone',
#  'Android',
#  'Win7_FF',
#  'Win7_Chrome',
#  'Win7_IE',
#  'WinXP_FF',
#  'WinXP_Chrome',
#  'WinXP_IE',
#  'WinXP_IE8',
#  'Grid_FF',
#  'Grid_Chrome',
#  'Grid_IE',
]

exec(runner.make_derived(gui_tests, environments, browsers))
exec(runner.make_derived(api_tests, environments, ['API',]))
