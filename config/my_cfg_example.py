
# Rename me to my_cfg.py
# Do not check in my_cfg.py, it is intended to be specific per person

# If you need to debug a script interactively try throwing this in
# from IPython import embed; embed()
# Or for better control try one of the flavors of pdb.
# import ipdb; ipdb.set_trace()  # http://georgejhunt.com/olpc/pydebug/pydebug/ipdb.html
# import pdb; pdb.set_trace()  # https://docs.python.org/2/library/pdb.html
# https://blog.safaribooksonline.com/2014/11/18/intro-python-debugger/
# self.set_highlight_delay()

from .env_enums import *
from services.tracker_svc import *


LOCALHOST = 'your box/vhost name'  # or 'localhost'
LOCALVM = 'your vm name'
RC_PORT = 4444
GRID_PORT = 5556
GRID_HOST = 'your selenium grid host name'
REMOTE_LINUX = 'your remote box name'
REMOTE_OSX = 'your remote box name'
REMOTE_WIN_7 = 'your remote box name'
REMOTE_WIN_XP = 'your remote box name'

REMOTE_IPHONE = 'your remote iphone host (IP)'
IPHONE_PORT = 3001

REMOTE_ANDROID = 'your remote android host (IP)'
ANDROID_PORT = 8080

config = {
    'HOST': {
        'LINUX': '%s:%d' % (REMOTE_LINUX, RC_PORT),
        'OSX': '%s:%d' % (REMOTE_OSX, RC_PORT),
        'WIN_7': '%s:%d' % (REMOTE_WIN_7, RC_PORT),
        'WIN_XP': '%s:%d' % (REMOTE_WIN_XP, RC_PORT),

        'WIN_XP_IE8': '%s:%d' % (REMOTE_WIN_XP, RC_PORT),
        'IPHONE': '%s:%d' % (REMOTE_IPHONE, IPHONE_PORT),
        'ANDROID': '%s:%d' % (REMOTE_ANDROID, ANDROID_PORT),

        'GRID': '%s:%d' % (GRID_HOST, GRID_PORT),
        'LOCALHOST': LOCALHOST,
        'LOCALVM': LOCALVM,
    },
    # Files are saved in your temp dir (unless SNAPSHOT_DIR is specified) as:
    #  snap_<test desc>.png and source_<test desc>.html
    'SAVE_SCREENSHOT': False,
    'SAVE_SOURCE': False,
    # 'SNAPSHOT_DIR_AUTOCREATE': False,  # create dir, if it doesn't exist
    # 'SNAPSHOT_DIR': '/tmp/',
    # 'HIGHLIGHT_DELAY': 0,

    # 'AVOID_WHERE_HANGS': True,  # Getting location/size from selenium can hang for minutes in some cases.

    # 'TRACKER_WRITER_ADDITIONS': [RecordAsYouGo,],
    # 'TRACKER_WRITER_SUBTRACTIONS': [WriteAsYouGo,],

    # 'VERBOSE_RECORDER_OUTPUT': True,  # Output all debug output in BaseService for Recorder calls

    'db_creds':
    {
        'example':
        {
            "host": "",
            'user': '',
            "passwd": '',
            "db": '',
        },
    },

    'gmail_creds': {
        "user": "",
        "password": "",
    },

    'wiki_creds': {
        'user': '',
        'password': '',
    },
}
