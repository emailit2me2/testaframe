
# -*- coding: utf-8 -*-

import os.path
import random
import string
import uuid


class TestDataBuilder(object):
    USERNAME = "qauser"
    EMAIL_DOMAIN = "example.com"
    EMAIL_TMPL = USERNAME + "+%s@" + EMAIL_DOMAIN
    DEFAULT_PASSWORD = "DoNotLogMyPassword"

    def get_uniq(self):
        return str(uuid.uuid4())[-8:]

    def uniq_user(self):
        uniq = self.get_uniq()
        uniq_username = "%s%8s" % (self.USERNAME, uniq)
        uniq_email = self.EMAIL_TMPL % uniq
        print repr(uniq_username), repr(uniq_email), repr(self.EMAIL_TMPL)
        password = self.DEFAULT_PASSWORD
        data = {
            "email": uniq_email, "password": password,
            "user_name": uniq_username
        }
        return data

    def uniq_keyword(self):
        uniq = self.get_uniq()
        return uniq

    def iter_fixture(self, fixture_path):
        """Iterate over the lines of the specified fixture file"""
        with open(os.path.join(os.path.dirname(__file__), 'fixtures', fixture_path), 'r') as f:
            for line in f:
                # Strip off the trailing newline but nothing else
                yield line.rstrip('\n')


class CIDataBuilder(TestDataBuilder):
    pass


class QADataBuilder(TestDataBuilder):
    pass


class ProdDataBuilder(object):
    USERNAME = "qauser"
    EMAIL_DOMAIN = "example.com"
    EMAIL_TMPL = USERNAME + "+%s@" + EMAIL_DOMAIN
    DEFAULT_PASSWORD = "DoNotLogMyPassword"
    # it might be dangerous to inherit from the TestDataBuilder for Prod.
    __cached_test_url = None

    def __init__(self):
        self.user_svc = None

    @staticmethod
    def _sample_iter(iterator, n=1):
        """Pick a random sample of size n from the iterator.

        The iterator must contain at least n items.

        Algorithm from http://code.activestate.com/recipes/426332-picking-random-items-from-an-iterator/#c2
        """

        result = [next(iterator) for i in range(n)]

        for index, item in enumerate(iterator):
            j = int(random.random() * (n + index + 1))
            if j < n:  # candidate is in results
                result[j] = item
        return result

    def uniq_user(self):
        uniq = self.get_uniq()
        uniq_first = 3
        uniq_username = "%s%8s" % (self.USERNAME, uniq)
        uniq_email = self.EMAIL_TMPL % uniq
        print repr(uniq_username), repr(uniq_email)  # , repr(self.EMAIL_TMPL)
        password = self.DEFAULT_PASSWORD
        data = {
            "email": uniq_email, "password": password, "password": password,
            "email_confirm": uniq_email, "password_confirm": password,
            "user_name": uniq_username,
            "display_name": uniq_username,
            "first_name": self.USERNAME + uniq[:uniq_first],
            "last_name": "Last%s" % (uniq[uniq_first:],),
            "address1": "%s Test St" % uniq,
            "address2": "Apt %s" % uniq,
            "country": "United States",
            "city": "Seattle",
            "state": "Washington",
            "postal_code": "98201",
        }

        return UserInfo(data, None)

    def uniq_billing_data(self):
        uniq = self.get_uniq()
        uniq_first = 3
        uniq_username = "%s%8s" % (self.USERNAME, uniq)
        uniq_email = self.EMAIL_TMPL % uniq
        print repr(uniq_username), repr(uniq_email)  # , repr(self.EMAIL_TMPL)
        data = {
            "first_name": self.USERNAME + uniq[:uniq_first],
            "last_name": "Last%s" % (uniq[uniq_first:],),
            "address1": "%s Test St" % uniq,
            "address2": "Apt %s" % uniq,
            "country": "United States",
            "city": "Seattle",
            "state": "Washington",
            "postal_code": "98201",
        }
        return data

    def get_uniq(self):
        return str(uuid.uuid4())[-8:]

    def get_random_autogen_string(self):
        str_length = 8
        my_string = ''.join([random.choice(string.ascii_letters) for n in xrange(str_length)])
        return my_string

    def uniq_comment(self, orig_comment=''):
        uniq = self.get_uniq()
        tmpl = u' \xC1ccented $5/mo %s Product & "stuff" \u4E2D\u56FD '
        tmpl = u' %s '
        return {
            'comment': orig_comment + tmpl % (uniq,),
            'stripped_comment': (orig_comment + tmpl % (uniq,)).strip(),
            'uniq': uniq
        }

    def tsting_creditcard(self):
        return {
            "card_number": "4111111111111111",
            "card_type": "VISA",
            "card_name": "Test Card",
            "card_exp_month": "11",
            "card_exp_year": "19",
            "card_ccv_code": "789"
        }

    def random_tsting_creditcard(self):
        cc_info = self.tsting_creditcard()
        cc_info['card_exp_year'] = str(random.randrange(21, 26))
        cc_info['card_exp_month'] = str(random.randrange(1, 12))
        cc_info['card_ccv_code'] = str(random.randrange(100, 1000))
        return cc_info


class StagingDataBuilder(ProdDataBuilder):
    pass
