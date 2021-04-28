
import json
import os
import datetime

from services.base_svc import BaseService
import config


class StubRecorderSvc(BaseService):
    """This is here as an example of how to implement a recorder service.
    """
    def __init__(self, auto, base_url, verbose, writes_allowed):
        self.auto = auto
        self.test_run_id = None
        self.test_pass_start_time = None
        self.username = self.auto.env.get_username()

    def teardown(self):
        return self.SUCCESSFUL_TEARDOWN

    def do_post(self, path, headers, data):
        print("POST to web service", path, headers, data)
        return {'test_run_id': 123}

    def new_test_run(self):
        # post '/test-run/new'

        if not self.test_pass_start_time:
            self.test_pass_start_time = config.my_cfg.config.get('TEST_PASS_START_TIME', datetime.datetime.now().isoformat())
        test_pass_name = os.environ.get('BUILD_TAG', "Dev-%s-%s" % (self.username, self.test_pass_start_time))

        print("new test run")

        u = self.do_post("/test-run/new", headers={"Content-Type": "application/json"},
                                        data={'test_name':self.auto.find_automation_complete_name(),
                                              'test_env':self.auto.env.ENV_NAME.value,
                                              'test_user_agent':self.auto.os_browser.OS_BROWSER,
                                              'test_pass':test_pass_name})
                                            #  TODO browser# for multi-browser tests
        return u

    def new_record(self, record_info):
        # post '/record/new'

        if not self.test_run_id:
            self.test_run_id = self.new_test_run()['test_run_id']

        try:
            encoded_values = json.dumps(record_info['values'])
        except TypeError:
            print("!!!!!!WARNING!!!!!!: Failed to Encode to JSON. Are you passing a class?")
            encoded_values = str(record_info['values'])

        u = self.do_post("/record/new", headers={"Content-Type": "application/json"},
                                      data={'type': record_info['type'],
                                            'message': record_info['message'],
                                            'values': encoded_values,
                                            'test_run_id': self.test_run_id,
                                            })
        return u
