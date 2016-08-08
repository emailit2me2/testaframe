
from enum import unique, Enum

@unique
class Environment(Enum):
    LOCALHOST = 'Localhost'
    LOCAL_VM = 'LocalVM'
    DEV = 'Dev'
    CI = 'CI'
    QA = 'QA'
    STAGING = 'Staging'
    PROD = 'Prod'


@unique
class Host(Enum):
    __order__ = """EMAIL SAMPLE TRACKER WIKIPEDIA"""

    EMAIL = 'Email_Host'
    SAMPLE = 'Sample_Host'
    TRACKER = 'Tracker_Host'
    WIKIPEDIA = 'Wikipedia_Host'
    WIKIPEDIA_API = 'Wikipedia_API_Host'


@unique
class SpecGroup(Enum):
    HOSTS = 'HOSTS'
    ALLOWS_WRITES = 'ALLOWS_WRITES'


@unique
class SpecKey(Enum):
    HOST = 'HOST'
    PORT = 'PORT'
    PREFIX = 'PREFIX'
    URL_TMPL = 'URL_TMPL'
