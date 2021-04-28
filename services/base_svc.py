
import json
import requests
import logging

# This is strange having nose stuff here, but it works best here.
from nose.plugins.skip import SkipTest

from utilities.urlutils import join


class BaseService(object):

    SUCCESSFUL_TEARDOWN = True
    ERRORS_IN_TEARDOWN = False

    def __init__(self):
        self.factory = None
        self.pubsub_items = {}

    def teardown(self):
        assert False, "Teardown must be defined for this Service"

    def __repr__(self):
        return "{self.__class__.__name__}".format(**locals())


class BaseWebService(BaseService):
    """Base API handler for all services"""

    def __init__(self, base_url, verbose=True, writes_allowed=True):
        BaseService.__init__(self)
        self.base_url = base_url
        self.verbose = verbose
        self.writes_allowed = writes_allowed
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging.INFO)

        # Enable the following line for service call debugguing output if the sevice uses requests.
###        self.setup_requests_debugging()

    def output(self, message, *args, **kwargs):
        if self.verbose:
            print(message.format(*args, **kwargs))

    def assert_env_allows_writes(self):
        # print "checking if writes are allowed"
        if not self.writes_allowed:
            raise SkipTest("no writes allowed in this env")
        print("writes are allowed in this env")

    def setup_requests_debugging(self):
        """Wrap up the logic to cause requests to provide deep debug logging of input & output."""

        # These two lines enable debugging at httplib level (requests->urllib3->http.client)
        # You will see the REQUEST, including HEADERS and DATA, and RESPONSE with HEADERS but without DATA.
        # The only thing missing will be the response.body which is not logged.
        try:
            import http.client as http_client
        except ImportError:
            # Python 2
            import http.client as http_client
        http_client.HTTPConnection.debuglevel = 1

        # You must initialize logging, otherwise you'll not see debug output.
        self.logger.setLevel(logging.DEBUG)
        requests_log = logging.getLogger("requests.packages.urllib3")
        requests_log.setLevel(logging.DEBUG)
        requests_log.propagate = True

    @staticmethod
    def _trim_output(output_string, length):
        """Trim output to at most length characters and maybe add an ellipsis."""
        if len(output_string) > length:
            return output_string[:length] + '...'
        else:
            return output_string

    def handle_request(self, requester, svc, data=None, headers=None, params=None, throw_on_error=False, verify=True):
        """Base method used by all of the _*_request methods."""
        url = join(self.base_url, svc)

        args = dict()
        if data:
            args['data'] = data
            self.output("Packaging content: {0}", data)
        if headers:
            args['headers'] = headers
            self.output("Packaging headers: {0}", headers)
        if params:
            args['params'] = params
            self.output("params: {0}", repr(params))

        args['verify'] = verify

        self.output("Prepping URL as {0}", url)
        res = requester(url, **args)
        if throw_on_error:
            self.success(res)
        self.output("Used URL as {0}", res.url)
        self.output("Status: {0}", res.status_code)
        self.output("Content: {0}", self._trim_output(str(res.text.encode('ascii', errors='replace')), 200))
        self.output("Headers: {0}", res.headers)
        return res

    def post_request(self, svc, data=None, headers=None, params=None, throw_on_error=False, verify=True):
        return self.handle_request(requests.post, svc, data, headers, params, throw_on_error, verify=verify)

    def post_json_request(self, svc, data=None, headers=None, params=None, throw_on_error=False, verify=True):
        return json.loads(self.post_request_content(svc, json.dumps(data), headers, params, throw_on_error,
                                                    verify=verify))

    def post_request_content(self, svc, data=None, headers=None, params=None, throw_on_error=False, verify=True):
        return self.post_request(svc, data, headers, params, throw_on_error, verify=verify).content

    def put_request(self, svc, data=None, headers=None, params=None, throw_on_error=False, verify=True):
        return self.handle_request(requests.put, svc, data, headers, params, throw_on_error, verify=verify)

    def put_json_request(self, svc, data=None, headers=None, params=None, throw_on_error=False, verify=True):
        return json.loads(self.put_request_content(svc, json.dumps(data), headers, params, throw_on_error,
                                                   verify=verify))

    def put_request_content(self, svc, data=None, headers=None, params=None, throw_on_error=False, verify=True):
        return self.put_request(svc, data, headers, params, throw_on_error, verify=verify).content

    def get_request(self, svc, headers=None, params=None, throw_on_error=False, verify=True):
        return self.handle_request(requests.get, svc, headers=headers, params=params, throw_on_error=throw_on_error,
                                   verify=verify)

    def get_json_request(self, svc, headers=None, params=None, throw_on_error=False, verify=True):
        return json.loads(self.get_request_content(svc, headers=headers, params=params, throw_on_error=throw_on_error,
                                                   verify=verify))

    def get_request_content(self, svc, headers=None, params=None, throw_on_error=False, verify=True):
        return self.get_request(svc, headers=headers, params=params, throw_on_error=throw_on_error,
                                verify=verify).content

    def delete_request(self, svc, headers=None, params=None, throw_on_error=False, verify=True):
        return self.handle_request(requests.delete, svc, headers=headers, params=params, throw_on_error=throw_on_error,
                                   verify=verify)

    def delete_json_request(self, svc, headers=None, params=None, throw_on_error=False, verify=True):
        return json.loads(self.delete_request_content(svc, headers=headers, params=params,
                                                      throw_on_error=throw_on_error, verify=verify))

    def delete_request_content(self, svc, headers=None, params=None, throw_on_error=False, verify=True):
        return self.delete_request(svc, headers=headers, params=params, throw_on_error=throw_on_error,
                                   verify=verify).content

    def __repr__(self):
        return "{self.__class__.__name__} at {self.base_url}".format(**locals())

    @staticmethod
    def success(response):
        print(BaseWebService._trim_output(response.text, 200))

        if 400 <= response.status_code < 500:
            raise ClientError(response.status_code, response.text)
        elif 500 <= response.status_code < 600:
            raise ServerError(response.status_code, response.text)

        return True


class NetworkError(Exception):
    def __init__(self, response_code, msg):
        Exception.__init__(self, msg)
        self.response_code = response_code

    def __str__(self):
        return "{0}\nHTTP Status Code: {1}".format(Exception.__str__(self), self.response_code)


class ClientError(NetworkError):
    pass


class ServerError(NetworkError):
    pass
