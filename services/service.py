
import sys
import json
import inspect
import urllib2

import requests

# This is strange having nose stuff here, but it works best here.
from nose.plugins.skip import SkipTest

class MyService(object):
  def __init__(self, base_url, writes_allowed=False, verbose=True, username='', password=''):
    self.base_url = base_url
    self.writes_allowed = writes_allowed
    self.verbose = verbose
    self.username = username
    self.password = password
    self.cookies = None

  def post_request(self, svc, body, headers=None):
    ''' Here is a generic post service using the requests library'''
    url = self.base_url + svc
    print "Prepping URL on %s for %s"  % (self.base_url, svc)
    data=json.dumps(body)
    print data
    print headers
    res = requests.post(url, data=data, headers=headers)
    print res.status_code
    print res.content
    print res.headers
    ret = json.loads(res.content)
    return ret
  # post_request and _call_svc are similar ways to call a service.
  # Pick one or combine them based on your needs.
  def _call_svc(self, data):
    # the service name is derived from the caller's function name
    # For example: person_create would get turned into person/create
    # Sometimes this is useful.
    callers_name = inspect.stack()[1][3]  # get calling function's name
    service = "/".join(callers_name.split('_',1))
    print "Prepping URL on %s for %s"  % (self.base_url, service)
    url = '%s/%s/%s' % (self.base_url, service, data)
    req = urllib2.Request(url)
    print "Trying %s %s" % (service,url)
    req.add_header("Content-Type", "application/json")
    res = urllib2.urlopen(req)
    r = res.read()
    #print r
    ret = json.loads(r)
    # TODO Check data structures, and all return types
    print "Got back %s" % repr(ret)[:100*2]
    return ret

  def assert_env_allows_writes(self):
    #print "checking if writes are allowed"
    if not self.writes_allowed:
      raise SkipTest("no writes allowed in this env")
    print "writes are allowed in this env"

  # A real project might subclass the base service class, but this function is here as an example.
  # Real projects often have multiple services.
  def api(self, ip=None):
    # Using a Geo IP service as an example.
    # http://geoip.nekudo.com/api/{ip}/{language}/{type}
    # This function is named json, so _call_svc will pull out the "json" and use it as the service name.
    return self._call_svc(ip)
