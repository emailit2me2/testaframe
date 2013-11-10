
# Rename me to my_cfg.py
# Do not check in my_cfg.py, it is intended to be specific per person

# If you need to debug a script interactively try throwing this in
# from IPython import embed; embed()

LOCALHOST = 'your box/vhost name' # or 'localhost'
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
    'LINUX': '%s:%d' % (REMOTE_LINUX,RC_PORT),
    'OSX': '%s:%d' % (REMOTE_OSX,RC_PORT),
    'WIN_7': '%s:%d' % (REMOTE_WIN_7,RC_PORT),
    'WIN_XP': '%s:%d' % (REMOTE_WIN_XP,RC_PORT),

    'WIN_XP_IE8': '%s:%d' % (REMOTE_WIN_XP,RC_PORT),
    'IPHONE': '%s:%d' % (REMOTE_IPHONE,IPHONE_PORT),
    'ANDROID': '%s:%d' % (REMOTE_ANDROID,ANDROID_PORT),

    'GRID': '%s:%d' % (GRID_HOST,GRID_PORT),
    'LOCALHOST': LOCALHOST,
    'LOCALVM': LOCALVM,
  },
  # Files are saved in your temp dir as:
  #  snap_<test desc>.png and source_<test desc>.html
  'SAVE_SCREENSHOT': False,
  'SAVE_SOURCE': False,
  #'SNAPSHOT_DIR': '/tmp/'
}
