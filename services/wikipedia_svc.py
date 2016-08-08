
from services.base_svc import BaseWebService


class WikipediaService(BaseWebService):
    '''The Wikipedia API is somewhat unique in that it uses only one endpoint with lots of parameters.'''

    def __init__(self, base_url, writes_allowed=True):
        BaseWebService.__init__(self, base_url, writes_allowed=writes_allowed)
        self.default_params = dict(format='json')

    def teardown(self):
        return self.SUCCESSFUL_TEARDOWN

    def _make_params(self, test_args, **query_args):
        params = dict(self.default_params)
        params.update(query_args)
        params.update(test_args)
        return params

    def query(self, **test_args):
        return self.get_json_request('/', params=self._make_params(test_args, action='query'))

