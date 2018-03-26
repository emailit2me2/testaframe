#!/usr/bin/env nosetests
assert __name__ != '__main__', "Must be run with nosetests"

import runner
import tsts_to_run

excludes = []  # 'package.module'

count = 1
environments = [
    # 'Localhost',
    #  'LocalVM',
    'Staging',
    #  'Dev',
    #  'CI',
    #  'QA',
    # 'Prod',
]

browsers = [
    #  'Local_FF',
      'Local_Chrome',
    #  'Local_PhantomJS',
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

runner.check_no_missing_files('test_gui', tsts_to_run.gui_tests, excludes)
runner.check_no_missing_files('test_api', tsts_to_run.api_tests, excludes)

exec(runner.make_derived(tsts_to_run.gui_tests, environments, browsers, count=count))
exec(runner.make_derived(tsts_to_run.api_tests, environments, ['API', ], count=count))
