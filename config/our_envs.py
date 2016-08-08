
"""Configuration file for company/project specific environments.

Hosts need to be in order for readability and debugability.

To add a new host:
- Add the name to Host.__order__, in alphabeitcal order.
- Add the Host and name to the list in Host, in alphabeitcal order.
- Add the host specification line to all active environments, in alphabeitcal order.
    Leave placeholders for unknown values.  For instance "PLACEHOLDER" as the host, not "example.com".
    Note that the OrderedDict class just retains the definition order, it doesn't sort.
- Run the file by itself to verify ordering and consistancy (see tests at the bottom of the file).
    python -m config.our_envs
- Run whatever test(s) you desire.  The tests at the bottom of the file will be run every time the file is imported.

"""

from collections import OrderedDict

from env_enums import *
import my_cfg

envs = {
    Environment.LOCALHOST: {
        SpecGroup.ALLOWS_WRITES: True,
        SpecGroup.HOSTS: OrderedDict([
            (Host.EMAIL, {SpecKey.HOST: my_cfg.config['HOST']['LOCALHOST'], SpecKey.PORT: 993}),
            (Host.SAMPLE, {SpecKey.HOST: my_cfg.config['HOST']['LOCALHOST'], SpecKey.URL_TMPL: 'http://{host}'}),
            (Host.TRACKER, {SpecKey.HOST: my_cfg.config['HOST']['LOCALHOST'], SpecKey.URL_TMPL: 'http://{host}'}),
            (Host.WIKIPEDIA, {SpecKey.HOST: my_cfg.config['HOST']['LOCALHOST'], SpecKey.URL_TMPL: 'http://{host}'}),
            (Host.WIKIPEDIA_API, {SpecKey.HOST: my_cfg.config['HOST']['LOCALHOST'], SpecKey.URL_TMPL: 'http://{host}'}),
        ]),
    },
    Environment.LOCAL_VM: {
        SpecGroup.ALLOWS_WRITES: True,
        SpecGroup.HOSTS: OrderedDict([
            (Host.EMAIL, {SpecKey.HOST: my_cfg.config['HOST']['LOCALVM'], SpecKey.PORT: 993}),
            (Host.SAMPLE, {SpecKey.HOST: my_cfg.config['HOST']['LOCALVM'], SpecKey.URL_TMPL: 'http://{host}'}),
            (Host.TRACKER, {SpecKey.HOST: my_cfg.config['HOST']['LOCALVM'], SpecKey.URL_TMPL: 'http://{host}'}),
            (Host.WIKIPEDIA, {SpecKey.HOST: my_cfg.config['HOST']['LOCALVM'], SpecKey.URL_TMPL: 'http://{host}'}),
            (Host.WIKIPEDIA_API, {SpecKey.HOST: my_cfg.config['HOST']['LOCALVM'], SpecKey.URL_TMPL: 'http://{host}'}),
        ])
    },
    Environment.DEV: {
        SpecGroup.ALLOWS_WRITES: True,
        SpecGroup.HOSTS: OrderedDict([
            (Host.EMAIL, {SpecKey.HOST: "YOUR DEV HOST", SpecKey.PORT: 993}),
            (Host.SAMPLE, {SpecKey.HOST: "YOUR DEV HOST", SpecKey.URL_TMPL: 'http://{host}'}),
            (Host.TRACKER, {SpecKey.HOST: "YOUR DEV HOST", SpecKey.URL_TMPL: 'http://{host}'}),
            (Host.WIKIPEDIA, {SpecKey.HOST: "YOUR DEV HOST", SpecKey.URL_TMPL: 'http://{host}'}),
            (Host.WIKIPEDIA_API, {SpecKey.HOST: "YOUR DEV HOST", SpecKey.URL_TMPL: 'http://{host}'}),
        ])
    },
    Environment.CI: {
        SpecGroup.ALLOWS_WRITES: True,
        SpecGroup.HOSTS: OrderedDict([
            (Host.EMAIL, {SpecKey.HOST: "YOUR CI HOST", SpecKey.PORT: 993}),
            (Host.SAMPLE, {SpecKey.HOST: "YOUR CI HOST", SpecKey.URL_TMPL: 'http://{host}'}),
            (Host.TRACKER, {SpecKey.HOST: "YOUR CI HOST", SpecKey.URL_TMPL: 'http://{host}'}),
            (Host.WIKIPEDIA, {SpecKey.HOST: "YOUR CI HOST", SpecKey.URL_TMPL: 'http://{host}'}),
            (Host.WIKIPEDIA_API, {SpecKey.HOST: "YOUR CI HOST", SpecKey.URL_TMPL: 'http://{host}'}),
        ])
    },
    Environment.QA: {
        SpecGroup.ALLOWS_WRITES: True,
        SpecGroup.HOSTS: OrderedDict([
            (Host.EMAIL, {SpecKey.HOST: "YOUR QA HOST", SpecKey.PORT: 993}),
            (Host.SAMPLE, {SpecKey.HOST: "YOUR QA HOST", SpecKey.URL_TMPL: 'http://{host}'}),
            (Host.TRACKER, {SpecKey.HOST: "YOUR QA HOST", SpecKey.URL_TMPL: 'http://{host}'}),
            (Host.WIKIPEDIA, {SpecKey.HOST: "YOUR QA HOST", SpecKey.URL_TMPL: 'http://{host}'}),
            (Host.WIKIPEDIA_API, {SpecKey.HOST: "YOUR QA HOST", SpecKey.URL_TMPL: 'http://{host}'}),
        ])
    },
    Environment.STAGING: {
        SpecGroup.ALLOWS_WRITES: True,
        SpecGroup.HOSTS: OrderedDict([
            (Host.EMAIL, {SpecKey.HOST: 'imap.gmail.com', SpecKey.PORT: 993}),
            (Host.SAMPLE, {SpecKey.HOST: my_cfg.config['HOST']['LOCALHOST'], SpecKey.PORT: 8000,
                           SpecKey.URL_TMPL: 'http://{host}:{port}'}),
            (Host.TRACKER, {SpecKey.HOST: "YOUR STAGING HOST", SpecKey.URL_TMPL: 'http://{host}'}),
            (Host.WIKIPEDIA, {SpecKey.HOST: "wikipedia.com", SpecKey.URL_TMPL: 'http://{host}'}),
            (Host.WIKIPEDIA_API, {SpecKey.HOST: "wikipedia.com", SpecKey.URL_TMPL: 'http://{host}/w/api.php'}),
        ]),
    },
    Environment.PROD: {
        SpecGroup.ALLOWS_WRITES: False,
        SpecGroup.HOSTS: OrderedDict([
            (Host.EMAIL, {SpecKey.HOST: 'imap.gmail.com', SpecKey.PORT: 993}),
            (Host.SAMPLE, {SpecKey.HOST: my_cfg.config['HOST']['LOCALHOST'], SpecKey.PORT: 8000,
                           SpecKey.URL_TMPL: 'http://{host}:{port}'}),
            (Host.TRACKER, {SpecKey.HOST: my_cfg.config['HOST']['LOCALHOST'], SpecKey.URL_TMPL: 'http://{host}'}),
            (Host.WIKIPEDIA, {SpecKey.HOST: "wikipedia.com", SpecKey.URL_TMPL: 'http://{host}'}),
            (Host.WIKIPEDIA_API, {SpecKey.HOST: "wikipedia.com", SpecKey.URL_TMPL: 'http://{host}/w/api.php'}),
        ])
    },
}

# In place tests to make sure everything stays clean, consistent, and sorted.
enum_hosts = list(Host)
enum_keys = Host.__members__.keys()

prod_keys = envs[Environment.PROD][SpecGroup.HOSTS].keys()
stage_keys = envs[Environment.STAGING][SpecGroup.HOSTS].keys()
local_keys = envs[Environment.LOCALHOST][SpecGroup.HOSTS].keys()

# Overwrite specified environments from my_cfg if applicable
overwrite_envs = my_cfg.config.get('OVERWRITE_ENVS')
if overwrite_envs:
    for overwrite in overwrite_envs:
        current_level = envs
        for level in overwrite['path']:
            current_level = current_level[level]
        #
        current_level.update(overwrite['value'])
    #
#

assert enum_keys == sorted(enum_keys), "Host Enum elements not in order:  %r != %r" % (enum_keys, sorted(enum_keys))

assert enum_hosts == prod_keys, "Prod spec doesn't match Host Enum: %r != %r" % (enum_hosts, prod_keys)
assert enum_hosts == stage_keys, "Staging spec doesn't match Host Enum: %r != %r" % (enum_hosts, stage_keys)
assert enum_hosts == local_keys, "Localhost spec doesn't match Host Enum: %r != %r" % (enum_hosts, local_keys)
