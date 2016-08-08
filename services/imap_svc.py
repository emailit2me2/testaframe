#!/usr/bin/env python

"""MailBox class for processing IMAP email.

To use with Gmail: enable IMAP access in your Google account settings
for other IMAP servers, adjust settings as necessary.

TODO The functions with leading _'s are not cleaned up and ready for use yet.

https://yuji.wordpress.com/2011/06/22/python-imaplib-imap-example-with-gmail/
http://www.example-code.com/asp/imap-search-examples.asp

"""

import imaplib
import time
import email
import base_svc


class MailBox(base_svc.BaseWebService):

    IMAP_USE_SSL = True

    MAX_TIME_TO_WAIT = 90
    POLL_TIME_TO_WAIT = 2

    def __init__(self, host, port, user, password, writes_allowed=True):
        base_svc.BaseWebService.__init__(self, None, writes_allowed)
        self.writes_allowed = writes_allowed
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.max_time_to_wait = self.MAX_TIME_TO_WAIT
        self.poll_time_to_wait = self.POLL_TIME_TO_WAIT

    def teardown(self):
        return self.SUCCESSFUL_TEARDOWN

    def start(self):
        if self.IMAP_USE_SSL:
            self.imap = imaplib.IMAP4_SSL(self.host, self.port)
        else:
            self.imap = imaplib.IMAP4(self.host, self.port)
        self.imap.login(self.user, self.password)
        return self

    def finish(self):
        self.imap.close()
        self.imap.logout()

    def _get_count(self):
        self.imap.select('Inbox')
        status, data = self.imap.search(None, 'ALL')
        return sum(1 for num in data[0].split())

    def fetch_message(self, num):
        self.imap.select('Inbox')
        status, data = self.imap.fetch(str(num), '(RFC822)')
        email_msg = email.message_from_string(data[0][1])
        return status, email_msg

    def _delete_message(self, num):
        self.imap.select('Inbox')
        self.imap.store(num, '+FLAGS', r'\Deleted')
        self.imap.expunge()

    def _delete_all(self):
        self.imap.select('Inbox')
        status, data = self.imap.search(None, 'ALL')
        for num in data[0].split():
            self.imap.store(num, '+FLAGS', r'\Deleted')
        self.imap.expunge()

    def _print_msgs(self):
        self.imap.select('Inbox')
        status, data = self.imap.search(None, 'ALL')
        for num in reversed(data[0].split()):
            status, data = self.imap.fetch(num, '(RFC822)')
            print 'Message %s\n%s\n' % (num, data[0][1])

    def get_latest_email_sent_to(self, email_address):
        self.start()
        start_time = time.time()
        while ((time.time() - start_time) < self.max_time_to_wait):
            # It's no use continuing until we've successfully selected
            # the inbox. And if we don't select it on each iteration
            # before searching, we get intermittent failures.
            status, data = self.imap.select('Inbox')
            if status != 'OK':
                print "  Polling for email to arrive"
                time.sleep(self.poll_time_to_wait)
                continue
            status, data = self.imap.search(None, 'TO', email_address)
            data = [d for d in data if d is not None]
            if status == 'OK' and data:
                for num in reversed(data[0].split()):
                    status, msg = self.fetch_message(num)
                    pieces = self.split_out_mail_pieces(msg)
                    self.finish()
                    return pieces
            print "  Polling for email to arrive"
            time.sleep(self.poll_time_to_wait)
        self.finish()
        raise AssertionError("No email sent to '%s' found in inbox "
             "after polling for %s seconds." % (email_address, self.max_time_to_wait))

    def _delete_msgs_sent_to(self, email_address):
        self.imap.select('Inbox')
        status, data = self.imap.search(None, 'TO', email_address)
        if status == 'OK':
            for num in reversed(data[0].split()):
                status, data = self.imap.fetch(num, '(RFC822)')
                self.imap.store(num, '+FLAGS', r'\Deleted')
        self.imap.expunge()


    # there is a cleanup_all_email method in service_test.py to run this
    # In mutt do shift-D then "~s .*" then quit to delete all messages.
    def _cleanup_all_email(self):
        cred = self.env_email_credentials()
        m = imaplib.IMAP4_SSL('imap.gmail.com')
        m.login(cred['email'], cred['password'])
        m.select()
        typ, results = m.search(None, 'ALL')
        assert typ == 'OK'
        for num in results[0].split():
            # we want to flag the message for deletion
            m.store(num, '+FLAGS', '\\Deleted')
        m.expunge()
        m.close()
        m.logout()

    def split_out_mail_pieces(self, msg):
        #print msg
        #print email.iterators._structure(msg)
        ret = {}
        for part in msg.walk():
            if part.get_content_maintype() == 'multipart':
                continue  # multipart/* are just containers
            ret[part.get_content_type()] = part.get_payload(decode=True).decode('utf-8')
        # end for all parts
        return ret

    def get_emails_with_body_containing(self, search, min_emails=1):
        ## take a username to further specify
        self.start()
        print "email body search text: %r" % search
        results = None
        start = time.time()
        while time.time() - start < self.max_time_to_wait:
            self.imap.select()
            typ, results = self.imap.search(None, 'BODY', search)
            print typ, results
            all = []
            for num in results[0].split():
                typ, msg = self.fetch_message(num)
                pieces = self.split_out_mail_pieces(msg)
                all.append(pieces)
            # end if results
            if len(all) >= min_emails:
                self.finish()
                return all
            # end if
            #else wait a bit
            time.sleep(self.poll_time_to_wait)
        # end while not timeout
        print "TIMEDOUT"
        self.finish()
        return []

    def find_emails_with_body_containing(self, search):
        self.start()
        print "email body search text: %r" % search
        results = None
        start = time.time()
        while time.time() - start < self.max_time_to_wait:
            self.imap.select()
            typ, results = self.imap.search(None, 'BODY', search)
            print typ, results
            if results[0]:
                self.finish()
                return True
            # end if results
            # else wait a bit
            time.sleep(self.poll_time_to_wait)
        # end while not timeout
        print "TIMEDOUT"
        self.finish()
        return False

    def find_emails_to_with_subject_containing(self, to, search, max_time_to_wait=MAX_TIME_TO_WAIT,
                                               poll_time_to_wait=POLL_TIME_TO_WAIT):
        self.start()
        print "email to {0} with subject search text: {1}".format(to, search)
        results = None
        start = time.time()
        while time.time() - start < max_time_to_wait:
            self.imap.select()
            typ, results = self.imap.search(None, '(HEADER Subject "{search}" TO "{to}")'.format(**locals()))
            print typ, results
            if results[0]:
                self.finish()
                return True
            # end if results
            # else wait a bit
            time.sleep(poll_time_to_wait)
        # end while not timeout
        print "TIMEDOUT"
        self.finish()
        return False

    def __repr__(self):
        return "{self.__class__.__name__} at {self.host}:{self.port}".format(**locals())

if __name__ == '__main__':
    import sys
    import os.path
    # Since we don't have relative imports in python...
    # We need the base directory, so grab the module's location zeroth element,
    # and strip off the module and then mess with the python path... I feel so dirty!!
    sys.path.insert(0,os.path.split(sys.path[0])[0])
    import config.my_cfg
    imap_username = config.my_cfg.config['gmail_creds']['user']
    imap_password = config.my_cfg.config['gmail_creds']['password']
    mbox = MailBox('imap.gmail.com', 993, imap_username, imap_password)
    mbox.max_time_to_wait = 5
#    print mbox.get_latest_email_sent_to("bill@example.com").keys()
#    print len(mbox.get_emails_with_body_containing("unique_test_string"))
#    print mbox.get_emails_with_body_containing("The Report data you requested for Bob")

