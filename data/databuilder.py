
# -*- coding: utf-8 -*-

import uuid

class TestDataBuilder(object):
  USERNAME = "example"
  EMAIL_DOMAIN = "gmail.com"
  EMAIL_TMPL = USERNAME+ "+%s@" + EMAIL_DOMAIN
  DEFAULT_PASSWORD = "DoNotLogMyPassword"

  def __init__(self, svc):
    self.svc = svc

  def get_uniq(self):
    return str(uuid.uuid4())[-8:]
  def uniq_user(self):
    uniq = self.get_uniq()
    uniq_username = "%s%8s" % (self.USERNAME, uniq)
    uniq_email = self.EMAIL_TMPL % uniq
    print repr(uniq_username), repr(uniq_email), repr(self.EMAIL_TMPL)
    password = self.DEFAULT_PASSWORD
    data = {"email": uniq_email, "password":password,
            "username": uniq_username}
    return data
  def uniq_comment(self,orig_comment=''):
    uniq = self.get_uniq()
    tmpl = u' \xC1ccented $5/mo %s Product & "stuff" \u4E2D\u56FD '
    tmpl = u' %s '
    return {'comment':          orig_comment+tmpl % (uniq,),
            'stripped_comment':(orig_comment+tmpl % (uniq,)).strip(),
            'uniq': uniq
    }


class CIDataBuilder(TestDataBuilder):
  pass

class QADataBuilder(TestDataBuilder):
  pass

class StagingDataBuilder(TestDataBuilder):
  pass

class ProdDataBuilder(object):
  # it might be dangerous to inherit from the TestDataBuilder for Prod.
  pass