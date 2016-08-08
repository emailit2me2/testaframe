"""Utilities for handling URLs."""

import urlparse

from publicsuffix import PublicSuffixList
_psl = PublicSuffixList()


def join(*parts):
    """Create a URL by joining sections.

    Does NOT handle '..'
    """
    return '/'.join(part.strip('/') for part in parts if part.strip('/') > '')


def slice_url(url):
    """Return a list of parts of the URL
    """
    parsed = urlparse.urlparse(url)
    parts = ["{0}://{1}".format(parsed.scheme, parsed.netloc)]
    parts = parts + parsed.path.split('/')
    return parts


def get_root_domain(hostname):
    """Get the root domain for a URL using the Public Suffix List.
    
    A root domain is one level above a public suffix, such as .com or .co.uk
    """
    return _psl.get_public_suffix(hostname)


def get_query(url):
    """Get the query portion of a URL."""
    parsed = urlparse.urlparse(url)
    return parsed.query


def get_query_as_dict(url):
    """Gets a dictionary version of the query in a URL"""
    query = get_query(url)
    return urlparse.parse_qs(query)
