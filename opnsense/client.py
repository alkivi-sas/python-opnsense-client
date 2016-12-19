# -*- encoding: utf-8 -*-

"""
"""

import keyword
import json
import requests


try:
    from urllib import urlencode
except ImportError:  # pragma: no cover
    # Python 3
    from urllib.parse import urlencode


from .config import config
from .exceptions import APIError

# Disable warning
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


#: Default timeout for each request. 180 seconds connect, 180 seconds read.
TIMEOUT = 180


class Client(object):
    """
    """

    def __init__(self, endpoint=None, api_key=None, api_secret=None,
                 timeout=TIMEOUT, config_file=None):
        """
        """
        # Load a custom config file if requested
        if config_file is not None:
            config.read(config_file)

        # load endpoint
        if endpoint is None:
            endpoint = config.get('default', 'endpoint')
        self._endpoint = endpoint

        # load keys
        if api_key is None:
            api_key = config.get(endpoint, 'api_key')
        self._api_key = api_key

        if api_secret is None:
            api_secret = config.get(endpoint, 'api_secret')
        self._api_secret = api_secret

        # use a requests session to reuse HTTPS connections between requests
        self._session = requests.Session()

        # Override default timeout
        self._timeout = timeout

    def _canonicalize_kwargs(self, kwargs):
        """
        If an API needs an argument colliding with a Python reserved keyword,
        it can be prefixed with an underscore. For example, ``from`` argument
        of ``POST /email/domain/{domain}/redirection`` may be replaced by
        ``_from``.

        :param dict kwargs: input kwargs
        :return dict: filtered kawrgs
        """
        arguments = {}

        for k, v in kwargs.items():
            if k[0] == '_' and k[1:] in keyword.kwlist:
                k = k[1:]
            arguments[k] = v

        return arguments

    def _prepare_query_string(self, kwargs):
        """
        Boolean needs to be send as lowercase 'false' or 'true' in querystring.
        This function prepares arguments for querystring and encodes them.

        :param dict kwargs: input kwargs
        :return string: prepared querystring
        """
        arguments = {}

        for k, v in kwargs.items():
            if isinstance(v, bool):
                v = str(v).lower()
            arguments[k] = v

        return urlencode(arguments)

    def get(self, _target, **kwargs):
        """
        'GET' :py:func:`Client.call` wrapper.

        Query string parameters can be set either directly in ``_target`` or
        as keywork arguments. If an argument collides with a Python reserved
        keyword, prefix it with a '_'.
        For instance, ``from`` becomes ``_from``.

        :param string _target: API method to call
        """
        if kwargs:
            kwargs = self._canonicalize_kwargs(kwargs)
            query_string = self._prepare_query_string(kwargs)
            if '?' in _target:
                _target = '%s&%s' % (_target, query_string)
            else:
                _target = '%s?%s' % (_target, query_string)

        return self.call('GET', _target, None)

    def put(self, _target, **kwargs):
        """
        'PUT' :py:func:`Client.call` wrapper

        Body parameters can be set either directly in ``_target`` or as keywork
        arguments. If an argument collides with a Python reserved keyword,
        prefix it with a '_'. For instance, ``from`` becomes ``_from``.

        :param string _target: API method to call
        """
        kwargs = self._canonicalize_kwargs(kwargs)
        return self.call('PUT', _target, kwargs)

    def post(self, _target, **kwargs):
        """
        'POST' :py:func:`Client.call` wrapper

        Body parameters can be set either directly in ``_target`` or as keywork
        arguments. If an argument collides with a Python reserved keyword,
        prefix it with a '_'. For instance, ``from`` becomes ``_from``.

        :param string _target: API method to call
        """
        kwargs = self._canonicalize_kwargs(kwargs)
        return self.call('POST', _target, kwargs)

    def delete(self, _target):
        """
        'DELETE' :py:func:`Client.call` wrapper

        :param string _target: API method to call
        """
        return self.call('DELETE', _target, None)

    def call(self, method, path, data=None):
        """
        :param str method: HTTP verb. Usualy one of GET, POST, PUT, DELETE
        :param str path: api entrypoint to call, relative to endpoint base path
        :param data: any json serializable data to send as request's body
        :raises HTTPError: when underlying request failed for network reason
        :raises InvalidResponse: when API response could not be decoded
        """
        body = ''
        target = 'https://' + self._endpoint + '/api' + path
        headers = {}
        auth = (self._api_key, self._api_secret)

        # include payload
        if data is not None:
            headers['Content-type'] = 'application/json'
            body = json.dumps(data)

        # attempt request
        try:
            result = self._session.request(method, target, headers=headers,
                                           data=body, timeout=self._timeout,
                                           verify=False, auth=auth)
        except requests.RequestException as error:
            raise APIError("Low HTTP request failed error", error)

        status = result.status_code

        # attempt to decode and return the response
        try:
            json_result = result.json()
        except ValueError as error:
            raise APIError("Failed to decode API response", error)

        # error check
        if status >= 100 and status < 300:
            return json_result
        else:
            raise APIError(json_result.get('message'), response=result)
