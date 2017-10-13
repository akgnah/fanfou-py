# -*- coding: utf-8 -*-
import six
import hmac
import json
import time
import random
import hashlib
import binascii
from six.moves.urllib import parse
from six.moves.urllib import request

# @home2 http://fanfou.com/home2


def oauth_escape(s, via='quote', safe='~'):
    quote_via = getattr(parse, via)
    if isinstance(s, (int, float)):
        s = str(s)
    if not isinstance(s, six.binary_type):
        s = s.encode('utf-8')
    return quote_via(s, safe=safe)


def oauth_timestamp():
    return str(int(time.time()))


def oauth_nonce(size=8):
    return ''.join([str(random.randint(0, 9)) for i in range(size)])


def oauth_query(args, via='quote', safe='~'):
    return '&'.join('%s=%s' % (k, oauth_escape(v, via, safe)) for k, v in sorted(args.items()))


def oauth_normalized_url(url):
    return '%s://%s%s' % (parse.urlparse(url)[:3])


class Auth(object):
    def __init__(self, oauth_consumer, oauth_token=None, callback=None, auth_host=None):
        self.oauth_consumer = oauth_consumer
        self.oauth_token = oauth_token or {}
        self.callback = callback or 'http://localhost:8080/callback'
        self.auth_host = 'http://%s' % (auth_host or 'm.fanfou.com')
        self.form_urlencoded = 'application/x-www-form-urlencoded'
        self.base_api_url = 'http://api.fanfou.com%s.json'
        self.access_token_url = 'http://fanfou.com/oauth/access_token'
        self.request_token_url = 'http://fanfou.com/oauth/request_token'
        self.authorize_url = parse.urljoin(self.auth_host, '/oauth/authorize?oauth_token=%s&oauth_callback=%s')

    def HMAC_SHA1(self, keys_string, base_string):
        hashed = hmac.new(keys_string.encode(), base_string.encode(), hashlib.sha1)
        return binascii.b2a_base64(hashed.digest())[:-1]

    def oauth_signature(self, url, method, base_args):
        normalized_url = oauth_normalized_url(url)
        query_items = oauth_query(base_args)
        base_elems = (method.upper(), normalized_url, query_items)
        base_string = '&'.join(oauth_escape(s) for s in base_elems)
        keys_elems = (self.oauth_consumer['secret'], self.oauth_token.get('secret', ''))
        keys_string = '&'.join(oauth_escape(s) for s in keys_elems)
        return self.HMAC_SHA1(keys_string, base_string)

    def oauth_header(self, base_args, realm=''):
        auth_header = 'OAuth realm="%s"' % realm
        for k, v in sorted(base_args.items()):
            if k.startswith('oauth_') or k.startswith('x_auth_'):
                auth_header += ', %s="%s"' % (k, oauth_escape(v))
        return {'Authorization': auth_header}

    def oauth_request(self, url, method='GET', args={}, headers={}):
        base_args = {
            'oauth_consumer_key': self.oauth_consumer['key'],
            'oauth_signature_method': 'HMAC-SHA1',
            'oauth_timestamp': oauth_timestamp(),
            'oauth_nonce': oauth_nonce(),
            'oauth_version': '1.0'
        }

        args = args.copy()
        headers = headers.copy()
        headers['User-Agent'] = headers.get('User-Agent', 'fanfou-py')

        if url.startswith('/'):
            if ':' in url:
                path, _ = url.split(':')
                if args.get('id'):
                    url = path + oauth_escape(args['id'], via='quote_plus', safe='')
                else:
                    url = path[:-1]
            url = self.base_api_url % url

        if method == 'POST':
            headers['Content-Type'] = headers.get('Content-Type', self.form_urlencoded)
            (headers['Content-Type'] == self.form_urlencoded) and base_args.update(args)
        else:
            base_args.update(args)
            url = url + '?' + oauth_query(args, via='quote_plus', safe='')

        self.oauth_token and base_args.update({'oauth_token': self.oauth_token['key']})
        base_args['oauth_signature'] = self.oauth_signature(url, method, base_args)
        headers.update(self.oauth_header(base_args))

        req = request.Request(url, headers=headers)

        if headers.get('Content-Type') == self.form_urlencoded:
            data = oauth_query(args, via='quote_plus', safe='').encode()
        elif 'form-data' in headers.get('Content-Type', ''):  # multipart/form-data
            data = args['form-data']
        else:
            data = None

        resp = request.urlopen(req, data=data)
        resp.json = lambda: json.loads(resp.read().decode() or '""')
        return resp


class OAuth(Auth):
    def __init__(self, oauth_consumer, oauth_token=None, callback=None, auth_host=None):
        Auth.__init__(self, oauth_consumer, oauth_token, callback, auth_host)

    def request(self, url, method='GET', args={}, headers={}):
        return self.oauth_request(url, method, args, headers)

    def request_token(self):
        resp = self.oauth_request(self.request_token_url, 'GET')
        oauth_token = dict(parse.parse_qsl(resp.read().decode()))
        self.authorize_url = self.authorize_url % (oauth_token['oauth_token'], self.callback)
        self.oauth_token = {'key': oauth_token['oauth_token'], 'secret': oauth_token['oauth_token_secret']}
        return self.oauth_token

    def access_token(self, oauth_token=None, oauth_verifier=None):
        self.oauth_token = oauth_token or self.oauth_token
        args = {'oauth_verifier': oauth_verifier} if oauth_verifier else {}  # if callback is oob
        resp = self.oauth_request(self.access_token_url, 'GET', args)
        oauth_token = dict(parse.parse_qsl(resp.read().decode()))
        self.oauth_token = {'key': oauth_token['oauth_token'], 'secret': oauth_token['oauth_token_secret']}
        return self.oauth_token


class XAuth(Auth):
    def __init__(self, oauth_consumer, username, password):
        Auth.__init__(self, oauth_consumer)
        self.oauth_token = self.xauth(username, password)

    def request(self, url, method='GET', args={}, headers={}):
        return self.oauth_request(url, method, args, headers)

    def xauth(self, username, password):
        args = {
            'x_auth_username': username,
            'x_auth_password': password,
            'x_auth_mode': 'client_auth'
        }
        resp = self.oauth_request(self.access_token_url, 'GET', args)
        oauth_token = dict(parse.parse_qsl(resp.read().decode()))
        return {'key': oauth_token['oauth_token'], 'secret': oauth_token['oauth_token_secret']}

    def access_token(self):
        return self.oauth_token
