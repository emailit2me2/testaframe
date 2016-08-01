
import my_cfg

LOCALHOST_ENV = 'Localhost'
LOCAL_VM_ENV = 'LocalVM'
DEV_ENV = 'Dev'
CI_ENV = 'CI'
QA_ENV = 'QA'
STAGING_ENV = 'Staging'
PROD_ENV = 'Prod'

WIKI_HOST_ENUM = 'Wiki_Host'
SAMPLE_HOST_ENUM = 'Sample_Host'
API_HOST_ENUM = 'API_Host'

DB_SVC_HOST_ENUM = API_HOST_ENUM

HOSTS_ENUM = 'HOSTS'
ALLOWS_WRITES_ENUM = 'ALLOWS_WRITES'
HOST_SPEC_ENUM = 'HOST'
URL_TMPL_ENUM = 'URL_TMPL'

envs = {
  LOCALHOST_ENV: {
    ALLOWS_WRITES_ENUM: True,
    HOSTS_ENUM: {
      WIKI_HOST_ENUM: {HOST_SPEC_ENUM:'wikipedia.org', URL_TMPL_ENUM: 'http://%s'},
      API_HOST_ENUM: {HOST_SPEC_ENUM:'geoip.nekudo.com', URL_TMPL_ENUM: 'http://%s'},
      # The lines above are used to make the example tests run "out of the box".
      # For real world use you will probably want to use the two lines below.
      #WIKI_HOST_ENUM: {HOST_SPEC_ENUM:my_cfg.config['HOST']['LOCALHOST'], URL_TMPL_ENUM: 'http://%s'},
      #API_HOST_ENUM: {HOST_SPEC_ENUM:my_cfg.config['HOST']['LOCALHOST'], URL_TMPL_ENUM: 'http://%s'},
      SAMPLE_HOST_ENUM: {HOST_SPEC_ENUM:my_cfg.config['HOST']['LOCALHOST'], URL_TMPL_ENUM: 'http://%s:8000'},
    }
    # Facebook/cookie secret stuff could go here too.
    #COOKIE_SECRET = ''
    #FB_APP_ID = ''
    #FB_APP_SECRET = ''
    #FB_APP_TOKEN = "|"
  },
  LOCAL_VM_ENV: {
    ALLOWS_WRITES_ENUM: True,
    HOSTS_ENUM: {
      WIKI_HOST_ENUM: {HOST_SPEC_ENUM:my_cfg.config['HOST']['LOCALVM'], URL_TMPL_ENUM: 'http://%s'},
      API_HOST_ENUM: {HOST_SPEC_ENUM:my_cfg.config['HOST']['LOCALVM'], URL_TMPL_ENUM: 'http://%s'},
      # you could also pull port numbers from my_cfg to create the URL_TMPL
      SAMPLE_HOST_ENUM: {HOST_SPEC_ENUM:my_cfg.config['HOST']['LOCALVM'], URL_TMPL_ENUM: 'http://%s:8000'},
    }
  },
  # Some environments may not have all host types.
  DEV_ENV: {
    ALLOWS_WRITES_ENUM: True,
    HOSTS_ENUM: {
      WIKI_HOST_ENUM: {HOST_SPEC_ENUM:'YOUR DEV HOST', URL_TMPL_ENUM: 'http://%s'},
      API_HOST_ENUM: {HOST_SPEC_ENUM:'YOUR DEV HOST', URL_TMPL_ENUM: 'http://%s'},
    }
  },
  CI_ENV: {
    ALLOWS_WRITES_ENUM: True,
    HOSTS_ENUM: {
      WIKI_HOST_ENUM: {HOST_SPEC_ENUM:'YOUR CI HOST', URL_TMPL_ENUM: 'http://%s'},
      API_HOST_ENUM: {HOST_SPEC_ENUM:'YOUR CI HOST', URL_TMPL_ENUM: 'http://%s'},
    }
  },
  QA_ENV: {
    ALLOWS_WRITES_ENUM: True,
    HOSTS_ENUM: {
      WIKI_HOST_ENUM: {HOST_SPEC_ENUM:'YOUR QA HOST', URL_TMPL_ENUM: 'http://%s'},
      API_HOST_ENUM: {HOST_SPEC_ENUM:'YOUR QA HOST', URL_TMPL_ENUM: 'http://%s'},
    }
  },
  STAGING_ENV: {
    ALLOWS_WRITES_ENUM: True,
    HOSTS_ENUM: {
      WIKI_HOST_ENUM: {HOST_SPEC_ENUM:'YOUR STAGING HOST', URL_TMPL_ENUM: 'http://%s'},
      API_HOST_ENUM: {HOST_SPEC_ENUM:'YOUR STAGING HOST', URL_TMPL_ENUM: 'http://%s'},
    }
  },
  PROD_ENV: {
    ALLOWS_WRITES_ENUM: False,
    HOSTS_ENUM: {
      WIKI_HOST_ENUM: {HOST_SPEC_ENUM:'YOUR PROD HOST', URL_TMPL_ENUM: 'http://%s'},
      API_HOST_ENUM: {HOST_SPEC_ENUM:'YOUR PROD HOST', URL_TMPL_ENUM: 'http://%s'},
    }
  },
}
