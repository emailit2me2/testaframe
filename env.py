

import os
import sys
import json
import tempfile
import traceback
import requests

# This is strange having nose stuff here, but it works best here.
from nose.plugins.skip import SkipTest

from selenium import webdriver

#from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import selenium.common.exceptions

#import base_page
import gui_pages  # Wish this didn't have to be in here polluting
import databuilder
import service

try:
  import my_cfg
except ImportError:
  raise Exception("You must create 'my_cfg.py'.  See: my_cfg_example.py")
# my_cfg.py is specific to each personal (or environment (e.g. CI))

# our_envs.py is specific to a project or company (in general).
import our_envs

class BaseSutEnvMixin(object):
  # MY_JS is for bookmarklets like pinterest
  MY_JS = '''var s=document.createElement('script');s.id='my_script';s.type='text/javascript';s.src='http://%s/my_js';'''
  def env_data_builder(self, svc):
    assert False, "Must be overridden"
  def __repr__(self):
    return "%s_env" % self.ENV_NAME
  def env_get_host(self, host_enum):
    return our_envs.envs[self.ENV_NAME][our_envs.HOSTS_ENUM][host_enum][our_envs.HOST_SPEC_ENUM]
  def env_get_url(self, host_enum):
    return our_envs.envs[self.ENV_NAME][our_envs.HOSTS_ENUM][host_enum][our_envs.URL_TMPL_ENUM] % (self.env_get_host(host_enum))
  def env_allows_writes(self):
    assert our_envs.envs[self.ENV_NAME].has_key(our_envs.ALLOWS_WRITES_ENUM), "ALLOWS_WRITES_ENUM must be defined by each env: %r" % repr(self)
    return our_envs.envs[self.ENV_NAME][our_envs.ALLOWS_WRITES_ENUM]
  def assert_env_allows_writes(self):
    #print "checking if writes are allowed"
    if not self.env_allows_writes():
      raise SkipTest("no writes allowed in this env")
    print "writes are allowed in this env"
  def env_specific_setup(self):
    pass  # overridable
  def env_get_my_js(self):
    return self.MY_JS % (self.env_sut_host())
  def env_platform_suffix(self):
    return self.PLATFORM_SUFFIX
    # some projects have different pages displayed per OS/browser (usually mobile).
    # so the PLATFORM_SUFFIX allowed for IndexPage_IOS and IndexPage for others.
    # TODO make sure this still works

  ######### Facebook stuff ###########
  # TODO move this facebook stuff somewhere more appropriate
  # TODO DRY the facebook stuff
  # http://developers.facebook.com/docs/authentication/applications/
  # https://developers.facebook.com/docs/authentication/client-side/
  # https://developers.facebook.com/apps/APP_ID/permissions
  ACCESS_TOKEN_URL = 'https://graph.facebook.com/oauth/access_token?client_id=%s&client_secret=%s&grant_type=client_credentials'
  def env_get_fb_app_access_token(self):
    print "Getting FB app access token"
    # App access tokens do not expire unless you refresh your app's App Secret.
    access_token_url = self.ACCESS_TOKEN_URL % (self.FB_APP_ID,self.FB_APP_SECRET)
    r = requests.get(access_token_url)
    if r.status_code == 200:
      print r.content
      ret = r.content[len('access_token='):]
      print "Got back %s" % repr(ret)
      return ret
    else:
      print >> sys.stderr, "Error calling FB API - app access token: %s %s" % (r.status_code,
          r.content)
      return None

  TEST_USER_URL = 'https://graph.facebook.com/%s/accounts/test-users?installed=false&locale=en_US&permissions=read_stream&method=post&access_token=%s'
  CREATE_TRIES = 3
  CREATE_WAIT = 2
  def env_get_fb_tst_user(self):
    print "Creating FB test user"
    # https://developers.facebook.com/docs/test_users/
    test_user_url = self.TEST_USER_URL % (self.FB_APP_ID,self.FB_APP_TOKEN)
    print "Trying", test_user_url
    for tries in xrange(self.CREATE_TRIES):
      r = requests.get(test_user_url,headers={"Content-Type": "application/json"})
      if r.status_code == 200:
        break
      else:
        print >> sys.stderr, "Error calling FB API - try get test user: %s %s" % (r.status_code,
          r.content)
        self.wait(self.CREATE_WAIT,'Error calling FB API - try get test user')
    # end for create tries
    if r.status_code == 200:
      ret = json.loads(r.content)  # TODO Check data structures, and all return types
      self.fb_test_users[ret['id']] = ret
      print "Got back %s" % repr(ret)
      ret.update(self.env_get_fb_tst_user_info(ret['id']))
      ret['persistant_user'] = False
      ret['username'] = ret['first_name']+'-'+ret['last_name']
      ret['first_last'] = ret['first_name']+' '+ret['last_name']
      #ret['fullname'] = ret['first_name']+' '+ret['middle_name']+' '+ret['last_name']
      return ret
    else:
      print >> sys.stderr, "Error calling FB API - get test user: %s %s" % (r.status_code,
          r.content)
      return None

  TEST_USER_QUICK_URL = 'https://graph.facebook.com/%s/accounts/test-users?installed=true&locale=en_US&permissions=email,user_birthday,user_hometown,user_location,publish_stream,publish_actions,user_photos,read_mailbox&method=post&access_token=%s'
  CREATE_TRIES = 3
  CREATE_WAIT = 2
  def env_get_fb_tst_user_quick(self):
    print "Creating FB test user quick"
    # https://developers.facebook.com/docs/test_users/
    test_user_url = self.TEST_USER_QUICK_URL % (self.FB_APP_ID,self.FB_APP_TOKEN)
    print "Trying", test_user_url
    for tries in xrange(self.CREATE_TRIES):
      r = requests.get(test_user_url,headers={"Content-Type": "application/json"})
      if r.status_code == 200:
        break
      else:
        print >> sys.stderr, "Error calling FB API - try get test user quick: %s %s" % (r.status_code,
          r.content)
        self.wait(self.CREATE_WAIT,'Error calling FB API - try get test user quick')
    # end for create tries
    if r.status_code == 200:
      ret = json.loads(r.content)  # TODO Check data structures, and all return types
      self.fb_test_users[ret['id']] = ret
      print "Got back %s" % repr(ret)
      ret.update(self.env_get_fb_tst_user_info(ret['id']))
      ret['persistant_user'] = False
      ret['username'] = ret['first_name']+'-'+ret['last_name']
      ret['first_last'] = ret['first_name']+' '+ret['last_name']
      #ret['fullname'] = ret['first_name']+' '+ret['middle_name']+' '+ret['last_name']
      return ret
    else:
      print >> sys.stderr, "Error calling FB API - get test user quick: %s %s" % (r.status_code,
          r.content)
      return None

  RENAME_USER_URL = 'https://graph.facebook.com/%s/?name=%s%%20%s%%20%s&method=post&access_token=%s'
  def env_rename_fb_tst_user(self, fb_id, first, middle, last):
    print "Renaming FB test user info", fb_id, self.fb_test_users[fb_id]
    url = self.RENAME_USER_URL % (fb_id, first, middle, last, self.FB_APP_TOKEN)
    r = requests.get(url,headers={"Content-Type": "application/json"})
    if r.status_code == 200:
      ret = json.loads(r.content)
      # TODO Check data structures, and all return types
      print "Got back %s" % repr(ret)
      r = self.fb_test_users[fb_id]
      r['first_name'] = first
      r['middle_name'] = middle
      r['last_name'] = last
      r['first_last'] = ret['first_name']+' '+ret['last_name']
      print "Renamed FB test user info", fb_id, self.fb_test_users[fb_id]
      return ret
    else:
      print >> sys.stderr, "Error calling FB API - rename test user : %s %s" % (r.status_code,
          r.content)
      return None

  USER_INFO_URL = 'https://graph.facebook.com/%s'
  def env_get_fb_tst_user_info(self, fb_id):
    print "Getting FB test user info", fb_id, self.fb_test_users.get('fb_id',None)
    url = self.USER_INFO_URL % (fb_id)
    r = requests.get(url,headers={"Content-Type": "application/json"})
    if r.status_code == 200:
      ret = json.loads(r.content)
      # TODO Check data structures, and all return types
      print "Got back %s" % repr(ret)
      return ret
    else:
      print >> sys.stderr, "Error calling FB API - get test user info: %s %s" % (r.status_code,
          r.content)
      return None

  USER_MESSAGES_URL = 'https://graph.facebook.com/me/feed?access_token=%s'
  def env_get_fb_tst_user_messages(self, fb):
    print "Getting FB test user messages", fb, self.fb_test_users.get('fb_id',None)
#    url = self.USER_MESSAGES_URL % (fb['id'], fb['access_token'])
    url = self.USER_MESSAGES_URL % (fb['access_token'])
    r = requests.get(url,headers={"Content-Type": "application/json"})
    if r.status_code == 200:
      ret = json.loads(r.content)
      # TODO Check data structures, and all return types
      print "Got back %s" % repr(ret)
      return ret
    else:
      print >> sys.stderr, "Error calling FB API - get test user messages: %s %s" % (r.status_code,
          r.content)
      return None

  ME_INFO_URL = 'https://graph.facebook.com/me/%s:%s/%s?access_token=%s&offset=%s&limit=%s'
  def env_get_fb_me_info(self, action, object, token, offset=0, limit=100):
    print "Getting Me info", action, object
    url = self.ME_INFO_URL % (self.FB_NAMESPACE, action, object, token, offset, limit)
    r = requests.get(url,headers={"Content-Type": "application/json"})
    if r.status_code == 200:
      ret = json.loads(r.content)
      # TODO Check data structures, and all return types
      print "Got back %s" % repr(ret)
      return ret
    else:
      print >> sys.stderr, "Error calling FB API - get me info: %s %s" % (r.status_code,
          r.content)
      return None

  MAKE_FRIEND_USER_URL = 'https://graph.facebook.com/%s/friends/%s?method=post&access_token=%s'
  def env_friend_fb_tst_user(self, fb_1, fb_id_2):
    print "Friending FB test users ", fb_1, fb_id_2
    url = self.MAKE_FRIEND_USER_URL % (fb_1['id'], fb_id_2, fb_1['access_token'])
    r = requests.get(url,headers={"Content-Type": "application/json"})
    if r.status_code == 200:
      ret = json.loads(r.content)
      # TODO Check data structures, and all return types
      print "Got back %s" % repr(ret)
      print "Friend FB test users ", fb_1, fb_id_2
      return ret
    else:
      print >> sys.stderr, "Error calling FB API - friend test users : %s %s" % (r.status_code,
          r.content)
      return None

  DELETE_TEST_USER_URL = 'https://graph.facebook.com/%s?method=delete&access_token=%s'
  def env_delete_fb_tst_user(self, test_user_id):
    print "Deleting FB test user", test_user_id, self.fb_test_users.get('test_user_id',None)
    test_user_url = self.DELETE_TEST_USER_URL % (test_user_id,self.FB_APP_TOKEN)
    r = requests.get(test_user_url)
    if r.status_code == 200:
      ret = r.content
      fb_id = self.fb_test_users.get('test_user_id', None)
      if fb_id:
        del self.fb_test_users[fb_id]

      # TODO Check data structures, and all return types
      print "Got back %s" % repr(ret)
      return ret
    else:
      print >> sys.stderr, "Error calling FB API - delete test user: %s %s" % (r.status_code,
          r.content)
      return None

  LIST_TEST_USERS_URL = 'https://graph.facebook.com/%s/accounts/test-users?access_token=%s'
  def env_list_fb_tst_users(self):
    print "Listing FB test users"
    test_user_url = self.LIST_TEST_USERS_URL % (self.FB_APP_ID,self.FB_APP_TOKEN)
    r = requests.get(test_user_url)
    if r.status_code == 200:
      ret = json.loads(r.content)
      # TODO Check data structures, and all return types
      print "Got back %s" % repr(ret)
      return ret['data']
    else:
      print >> sys.stderr, "Error calling FB API - list test users: %s %s" % (r.status_code,
          r.content)
      return None

class Localhost_EnvMixin(BaseSutEnvMixin):
  ENV_NAME = our_envs.LOCALHOST_ENV
  def env_data_builder(self, svc):
    self.data = databuilder.TestDataBuilder(svc)

class LocalVM_EnvMixin(BaseSutEnvMixin):
  ENV_NAME = our_envs.LOCAL_VM_ENV
  def env_data_builder(self, svc):
    self.data = databuilder.TestDataBuilder(svc)

class Dev_EnvMixin(BaseSutEnvMixin):
  ENV_NAME = our_envs.DEV_ENV
  def env_data_builder(self, svc):
    self.data = databuilder.TestDataBuilder(svc)

class CI_EnvMixin(BaseSutEnvMixin):
  ENV_NAME = our_envs.CI_ENV
  def env_data_builder(self, svc):
    self.data = databuilder.CIDataBuilder(svc)

class QA_EnvMixin(BaseSutEnvMixin):
  ENV_NAME = our_envs.QA_ENV
  def env_data_builder(self, svc):
    self.data = databuilder.QADataBuilder(svc)

class Staging_EnvMixin(BaseSutEnvMixin):
  ENV_NAME = our_envs.STAGING_ENV
  def env_data_builder(self, svc):
    self.data = databuilder.StagingDataBuilder(svc)

class Prod_EnvMixin(BaseSutEnvMixin):
  ENV_NAME = our_envs.PROD_ENV
  def __init__(self,*args):
    import sys
    assert [arg for arg in sys.argv if ('ProdSafe' in arg or 'ProdMonitor' in arg)], "run_PROD.py should only be run with -a ProdSafe|ProdMonitor."
    assert ['-a'] == [arg for arg in sys.argv if arg.startswith('-a')], "run_PROD.py multiple -a args are or'ed, should be '-a ProdSafe,Smoke'."
    #assert [] == [arg for arg in sys.argv if arg.startswith('--processes')], "run_PROD.py can not be run multiprocess."
    # fail for multiprocess in Prod_env (above) or only warn (below)  # TODO add to our_envs.py
    if [] != [arg for arg in sys.argv if arg.startswith('--processes')]: print "Warning: running multiprocess can be dangerous against Prod."
    BaseSutEnvMixin.__init__(self,*args)
  def env_data_builder(self, svc):
    self.data = databuilder.ProdDataBuilder()


class BaseSeEnvMixin(object):
  DO_POPUPS_WORK = False
  NEED_PRECLEAN = False  # needed for IE since it doesn't start a virgin instance each time.
  PLATFORM_SUFFIX = ''  # none by default
  def env_prep_for_se(self):
    try:
      self.driver = self.env_se_driver()
      self.start = gui_pages.MyPageFactory(self.driver, self, self.NEED_PRECLEAN, self.env_platform_suffix(),my_cfg.config.get('HIGHLIGHT_DELAY', 0))
      self.driver.implicitly_wait(1)
      self.svc = service.MyService(self.env_get_url(our_envs.DB_SVC_HOST_ENUM),self.env_allows_writes())
      self.env_data_builder(self.svc)
      self.env_specific_setup()
      self.fb_test_users = {}
    except Exception, e:
      traceback.print_exc()
      try:
        self.driver.quit()
      finally:
        raise e

  def env_restart_driver(self):
    self.driver = self.env_se_driver()
    self.start = gui_pages.MyPageFactory(self.driver, self.base_url, self.NEED_PRECLEAN, self.env_platform_suffix(),my_cfg.config.get('HIGHLIGHT_DELAY', 0))
    self.driver.implicitly_wait(1)

  def find_error_messages(self):
    # TODO add a list of expected errors that should be on the page so
    # negative test cases don't have missleading warning messages.
    try:
      if 'Internal Server Error' in self.driver.page_source:
        print "\nFailed with Internal Server Error\n"
    except selenium.common.exceptions.StaleElementReferenceException, e:
      pass # it is OK if there are no errors.
    #

  def env_teardown(self):
    #see if we failed and take a screen shot if we did
    # TODO only save on failure
    quit_driver = True
    try:
      # TODO maybe add datetimestamp.
      # TODO maybe only capture if a failing test, if we can tell
      errors = self.find_error_messages()
      snapshot_dir = my_cfg.config.get('SNAPSHOT_DIR', '')
      if snapshot_dir:
        if my_cfg.config.get('SNAPSHOT_DIR_AUTOCREATE', False) and not os.path.exists(snapshot_dir):
          print "Autocreating snapshot dir: %r" % snapshot_dir
          os.makedirs(snapshot_dir)
      else:
        snapshot_dir = tempfile.gettempdir()
      if errors or my_cfg.config.get('SAVE_SCREENSHOT', False):
        # TODO make an option for named screenshot and/or latest
        snap = os.path.join(snapshot_dir,"snap_%s.png" % self.find_tst_name())
        print "saving screenshot as: %s" % snap
        self.driver.get_screenshot_as_file(snap)
        snap = os.path.join(snapshot_dir,"snap_%s.png" % 'last_test')
        print "saving screenshot as: %s" % snap
        self.driver.get_screenshot_as_file(snap)
      if errors or my_cfg.config.get('SAVE_SOURCE', False):
        source = os.path.join(snapshot_dir,"source_%s.html" % self.find_tst_name())
        print "saving source as: %s" % source
        f = open(source,'wb')
        f.write((self.driver.page_source).encode('utf8'))
        f.close()
        source = os.path.join(snapshot_dir,"source_%s.html" %  'last_test')
        print "saving source as: %s" % source
        f = open(source,'wb')
        f.write((self.driver.page_source).encode('utf8'))
        f.close()
    #
    finally:
      if quit_driver:
        self.driver.quit()
        ##time.sleep(5) # getting Windows [32] error because process is not stopped, so lets wait a little

  def env_save_snapshot(self, timestamp, snap_name):
    where = my_cfg.config.get('SNAPSHOT_DIR',None)
    if where:
      # snapshot_linux_chrome_on_CI_timestamp_what.png
      snap = os.path.join(where ,"snapshot_%s_on_%s_%s_%s.png" % (
                 self.OS_BROWSER,self.ENV_NAME,timestamp,snap_name))
      print "saving screenshot as: %s" % snap
      self.driver.get_screenshot_as_file(snap)

  def get_grid_wd(self, caps, host):
    wd = webdriver.Remote(desired_capabilities=caps,
                            command_executor='http://%s/wd/hub' % host)
    print "Remote capabilities", wd.desired_capabilities
    info_url = "http://%s/grid/api/testsession?session=%s" % (host,wd.session_id)
    import requests
    r = requests.get(info_url, headers={"Content-Type": "application/json"})
    if r.status_code == 200:
      ret = json.loads(r.content)
      # TODO Check data structures, and all return types
      print "Got remote grid session info %s" % repr(ret)
    else:
      print >> sys.stderr, "Error calling for info: %s %s" % (r.status_code,r.content)
    # end
    return wd


class API_SeMixin(BaseSeEnvMixin):
  HOST_ENUM = our_envs.API_HOST_ENUM
  # This one is the no selenium mixin
  # This is a little hokey, but runner.make_derived() adds an SeMixin to the
  # derived test class
  def env_prep_for_svc(self):
    self.svc = service.MyService(self.env_get_url(self.HOST_ENUM),self.env_allows_writes())
    self.env_data_builder(self.svc)
    self.fb_test_users = {}


# it feels like there is a lot of boilerplate in these Se mixin classes
# TODO try to reduce the DRY.  Maybe a similar technique to our_envs.py.
class Local_FF_SeMixin(BaseSeEnvMixin):
  DO_POPUPS_WORK = False
  OS_BROWSER = 'Local_FF'
  def my_se(self):
    return "Local_FF Se for %s" % self.__class__.__name__
  def env_se_driver(self):
    drv = webdriver.Firefox()
    #size = drv.get_window_size()
    #drv.set_window_size(1025,size['height'])
    return drv


class Local_Chrome_SeMixin(BaseSeEnvMixin):
  OS_BROWSER = 'Local_Chrome'
  DO_POPUPS_WORK = True
  def my_se(self):
    return "Local_Chrome Se for %s" % self.__class__.__name__
  def env_se_driver(self):
    return webdriver.Chrome()

class Local_IE_SeMixin(BaseSeEnvMixin):
  OS_BROWSER = 'Local_IE'
  DO_POPUPS_WORK = True
  NEED_PRECLEAN = True
  def my_se(self):
    return "Local_IE Se for %s" % self.__class__.__name__
  def env_se_driver(self):
    return webdriver.Ie()


class Linux_FF_SeMixin(BaseSeEnvMixin):
  OS_BROWSER = 'Linux_FF'
  def my_se(self):
    return "Linux_FF Se for %s" % self.__class__.__name__
  def env_driver(self):
    host = my_cfg.config['HOST']['LINUX']
    return webdriver.Remote(desired_capabilities=DesiredCapabilities.FIREFOX,
                            command_executor='http://%s/wd/hub' % host)
  def env_se_driver(self):
    return self.env_driver()

class Linux_Chrome_SeMixin(BaseSeEnvMixin):
  OS_BROWSER = 'Linux_Chrome'
  DO_POPUPS_WORK = True
  def my_se(self):
    return "Linux_Chrome Se for %s" % self.__class__.__name__
  def env_driver(self):
    host = my_cfg.config['HOST']['LINUX']
    return webdriver.Remote(desired_capabilities=DesiredCapabilities.CHROME,
                            command_executor='http://%s/wd/hub' % host)
  def env_se_driver(self):
    return self.env_driver()


class OSX_FF_SeMixin(BaseSeEnvMixin):
  OS_BROWSER = 'OSX_FF'
  def my_se(self):
    return "OSX_FF Se for %s" % self.__class__.__name__
  def env_driver(self):
    host = my_cfg.config['HOST']['OSX']
    return webdriver.Remote(desired_capabilities=DesiredCapabilities.FIREFOX,
                            command_executor='http://%s/wd/hub' % host)
  def env_se_driver(self):
    return self.env_driver()

class OSX_Chrome_SeMixin(BaseSeEnvMixin):
  OS_BROWSER = 'OSX_Chrome'
  DO_POPUPS_WORK = True
  def my_se(self):
    return "OSX_Chrome Se for %s" % self.__class__.__name__
  def env_driver(self):
    host = my_cfg.config['HOST']['OSX']
    dc = DesiredCapabilities.CHROME
    dc['chrome.switches'] = ['--start-maximized']
    return webdriver.Remote(desired_capabilities=dc,
                            command_executor='http://%s/wd/hub' % host)
  def env_se_driver(self):
    return self.env_driver()


class IPhone_SeMixin(BaseSeEnvMixin):
  OS_BROWSER = 'iPhone'
  PLATFORM_SUFFIX = 'IOS'
  DO_POPUPS_WORK = True
  def my_se(self):
    return "IPhone Se for %s" % self.__class__.__name__
  def env_driver(self):
    host = my_cfg.config['HOST']['IPHONE']
    dc = DesiredCapabilities.IPHONE
    print dc,host
    return webdriver.Remote(desired_capabilities=dc,
                            command_executor='http://%s/wd/hub' % host)
  def env_se_driver(self):
    return self.env_driver()


class Android_SeMixin(BaseSeEnvMixin):
  OS_BROWSER = 'Android'
  DO_POPUPS_WORK = True
  def my_se(self):
    return "Android Se for %s" % self.__class__.__name__
  def env_driver(self):
    host = my_cfg.config['HOST']['ANDROID']
    dc = DesiredCapabilities.ANDROID
    print dc,host
    return webdriver.Remote(desired_capabilities=dc,
                            command_executor='http://%s/wd/hub' % host)
  def env_se_driver(self):
    return self.env_driver()


class Prod_OSX_Chrome_SeMixin(BaseSeEnvMixin):
  OS_BROWSER = 'Prod_OSX_Chrome'
  DO_POPUPS_WORK = True
  def my_se(self):
    return "Prod_OSX_Chrome Se for %s" % self.__class__.__name__
  def env_driver(self):
    host = my_cfg.config['HOST']['PROD_OSX']
    dc = DesiredCapabilities.CHROME
    dc['chrome.switches'] = ['--start-maximized']
    return webdriver.Remote(desired_capabilities=dc,
                            command_executor='http://%s/wd/hub' % host)
  def env_se_driver(self):
    return self.env_driver()


class Win7_FF_SeMixin(BaseSeEnvMixin):
  OS_BROWSER = 'Win7_FF'
  DO_POPUPS_WORK = False
  def my_se(self):
    return "Win7_FF Se for %s" % self.__class__.__name__
  def env_driver(self):
    host = my_cfg.config['HOST']['WIN_7']
    drv = webdriver.Remote(desired_capabilities=DesiredCapabilities.FIREFOX,
                            command_executor='http://%s/wd/hub' % host)
    size = drv.get_window_size()
    drv.set_window_size(1025,size['height'])
    return drv
  def env_se_driver(self):
    return self.env_driver()

class Win7_Chrome_SeMixin(BaseSeEnvMixin):
  OS_BROWSER = 'Win7_Chrome'
  DO_POPUPS_WORK = True
  def my_se(self):
    return "Win7_Chrome Se for %s" % self.__class__.__name__
  def env_driver(self):
    host = my_cfg.config['HOST']['WIN_7']
    dc = DesiredCapabilities.CHROME
    dc['chrome.switches'] = ['--start-maximized']
    return webdriver.Remote(desired_capabilities=dc,
                            command_executor='http://%s/wd/hub' % host)
  def env_se_driver(self):
    return self.env_driver()

class Win7_IE_SeMixin(BaseSeEnvMixin):
  OS_BROWSER = 'Win7_IE'
  NEED_PRECLEAN = True
  DO_POPUPS_WORK = True
  def my_se(self):
    return "Win_IE Se for %s" % self.__class__.__name__
  def env_driver(self):
    host = my_cfg.config['HOST']['WIN_7']
    dc = DesiredCapabilities.INTERNETEXPLORER
    dc['ensureCleanSession'] = 'true'  # this just doesn't work.  we stay logged in from prev test.
    wd = webdriver.Remote(desired_capabilities=dc,
                            command_executor='http://%s/wd/hub' % host)
    return wd
  def env_se_driver(self):
    return self.env_driver()

class WinXP_FF_SeMixin(BaseSeEnvMixin):
  OS_BROWSER = 'WinXP_FF'
  DO_POPUPS_WORK = False
  def my_se(self):
    return "WinXP_FF Se for %s" % self.__class__.__name__
  def env_driver(self):
    host = my_cfg.config['HOST']['WIN_XP']
    drv = webdriver.Remote(desired_capabilities=DesiredCapabilities.FIREFOX,
                            command_executor='http://%s/wd/hub' % host)
    size = drv.get_window_size()
    drv.set_window_size(1025,size['height'])
    return drv
  def env_se_driver(self):
    return self.env_driver()

class WinXP_Chrome_SeMixin(BaseSeEnvMixin):
  OS_BROWSER = 'WinXP_Chrome'
  DO_POPUPS_WORK = True
  def my_se(self):
    return "WinXP_Chrome Se for %s" % self.__class__.__name__
  def env_driver(self):
    host = my_cfg.config['HOST']['WIN_XP']
    dc = DesiredCapabilities.CHROME
    dc['chrome.switches'] = ['--start-maximized']
    return webdriver.Remote(desired_capabilities=dc,
                            command_executor='http://%s/wd/hub' % host)
  def env_se_driver(self):
    return self.env_driver()

class WinXP_IE_SeMixin(BaseSeEnvMixin):
  OS_BROWSER = 'WinXP_IE'
  NEED_PRECLEAN = True
  DO_POPUPS_WORK = True
  def my_se(self):
    return "WinXP_IE Se for %s" % self.__class__.__name__
  def env_driver(self):
    host = my_cfg.config['HOST']['WIN_XP']
    dc = DesiredCapabilities.INTERNETEXPLORER
    #dc['ensureCleanSession'] = 'true'  # this just doesn't work.  we stay logged in from prev test.
    wd = webdriver.Remote(desired_capabilities=dc,
                            command_executor='http://%s/wd/hub' % host)
    return wd
  def env_se_driver(self):
    return self.env_driver()

class WinXP_IE8_SeMixin(BaseSeEnvMixin):
  OS_BROWSER = 'WinXP_IE8'
  NEED_PRECLEAN = True
  DO_POPUPS_WORK = True
  def my_se(self):
    return "WinXP_IE8 Se for %s" % self.__class__.__name__
  def env_driver(self):
    host = my_cfg.config['HOST']['WIN_XP_IE8']
    dc = DesiredCapabilities.INTERNETEXPLORER
    wd = webdriver.Remote(desired_capabilities=dc,
                            command_executor='http://%s/wd/hub' % host)
    return wd
  def env_se_driver(self):
    return self.env_driver()


class Grid_Chrome_SeMixin(BaseSeEnvMixin):
  OS_BROWSER = 'Grid Chrome'
  DO_POPUPS_WORK = True
  def my_se(self):
    return "Grid_Chrome Se for %s" % self.__class__.__name__
  def env_driver(self):
    host = my_cfg.config['HOST']['GRID']
    caps = DesiredCapabilities.CHROME
    #caps['platform'] = 'OSX'
    return self.get_grid_wd(caps,host)
  def env_se_driver(self):
    return self.env_driver()

class Grid_FF_SeMixin(BaseSeEnvMixin):
  OS_BROWSER = 'Grid FF'
  def my_se(self):
    return "Grid_FF Se for %s" % self.__class__.__name__
  def env_driver(self):
    host = my_cfg.config['HOST']['GRID']
    caps = DesiredCapabilities.FIREFOX
    #caps['platform'] = 'OSX'
    return self.get_grid_wd(caps,host)
  def env_se_driver(self):
    return self.env_driver()

class Grid_IE_SeMixin(BaseSeEnvMixin):
  OS_BROWSER = 'Grid IE'
  NEED_PRECLEAN = True
  DO_POPUPS_WORK = True
  def my_se(self):
    return "Grid_IE Se for %s" % self.__class__.__name__
  def env_driver(self):
    host = my_cfg.config['HOST']['GRID']
    caps = DesiredCapabilities.INTERNETEXPLORER
    #caps['platform'] = 'WIN'
    return self.get_grid_wd(caps,host)
  def env_se_driver(self):
    return self.env_driver()

