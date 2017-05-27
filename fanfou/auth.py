# -*- coding: utf-8 -*-
import six
import time
import hmac
import hashlib
import binascii
import random
from six.moves.urllib import parse
from six.moves.urllib import request

# @home2 http://fanfou.com/home2


def oauth_escape(s):
    if not isinstance(s, six.binary_type):
        s = str(s).encode('utf-8')
    return parse.quote(s, safe='~')


def oauth_timestamp():
    return str(int(time.time()))


def oauth_nonce(size=8):
    return ''.join([str(random.randint(0, 9)) for i in range(size)])


def oauth_query(base_args):
    return '&'.join('%s=%s' % (k, oauth_escape(v)) for k, v in sorted(base_args.items()))


def oauth_http_url(http_url):
    return '%s://%s%s' % (parse.urlparse(http_url)[:3])


class Auth(object):
    def __init__(self, oauth_consumer, oauth_token={}, callback=None, auth_host='m.fanfou.com'):
        self.oauth_consumer = oauth_consumer
        self.oauth_token = oauth_token
        self.callback = callback or 'http://localhost:8080/callback'
        self.form_urlencoded = 'application/x-www-form-urlencoded'
        self.base_api_url = 'http://api.fanfou.com%s.json'
        self.access_token_url = 'http://fanfou.com/oauth/access_token'
        self.request_token_url = 'http://fanfou.com/oauth/request_token'
        self.authorize_url = parse.urljoin('http://%s' % auth_host, '/oauth/authorize?oauth_token=%s&oauth_callback=%s')

    def HMAC_SHA1(self, keys_string, base_string):
        hashed = hmac.new(keys_string.encode(), base_string.encode(), hashlib.sha1)
        return binascii.b2a_base64(hashed.digest())[:-1]

    def oauth_signature(self, http_url, http_method, base_args):
        normalized_url = oauth_http_url(http_url)
        query_items = oauth_query(base_args)
        base_elems = (http_method.upper(), normalized_url, query_items)
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

    def oauth_request(self, http_url, http_method, http_args={}, headers={}):
        base_args = {
            'oauth_consumer_key': self.oauth_consumer['key'],
            'oauth_signature_method': 'HMAC-SHA1',
            'oauth_timestamp': oauth_timestamp(),
            'oauth_nonce': oauth_nonce(),
            'oauth_version': '1.0'
        }

        http_args = http_args.copy()
        headers = headers.copy()
        if http_url.startswith('/'):
            if ':' in http_url:
                path, argv = http_url.split(':')
                http_url = path + http_args.get(argv)
            http_url = self.base_api_url % http_url

        if http_method == 'POST':
            headers['Content-Type'] = headers.get('Content-Type', self.form_urlencoded)
            (headers['Content-Type'] == self.form_urlencoded) and base_args.update(http_args)
        else:
            base_args.update(http_args)
            http_url = http_url + '?' + parse.urlencode(http_args) if http_args else http_url

        self.oauth_token and base_args.update({'oauth_token': self.oauth_token['key']})
        base_args['oauth_signature'] = self.oauth_signature(http_url, http_method, base_args)

        headers.update(self.oauth_header(base_args))
        http_req = request.Request(http_url, headers=headers)
        if headers.get('Content-Type') == self.form_urlencoded:
            http_data = parse.urlencode(http_args).encode()
        elif 'form-data' in headers.get('Content-Type', ''):    # multipart/form-data
            http_data = http_args['form-data']
        else:
            http_data = None

        return request.urlopen(http_req, data=http_data)


class OAuth(Auth):
    def __init__(self, oauth_consumer, oauth_token={}, callback=None, auth_host='m.fanfou.com'):
        Auth.__init__(self, oauth_consumer, oauth_token, callback, auth_host)

    def request(self, http_url, http_method, http_args={}, headers={}):
        return self.oauth_request(http_url, http_method, http_args, headers)

    def request_token(self):
        resp = self.oauth_request(self.request_token_url, 'GET')
        oauth_token = dict(parse.parse_qsl(resp.read().decode()))
        self.authorize_url = self.authorize_url % (oauth_token['oauth_token'], self.callback)
        self.oauth_token = {'key': oauth_token['oauth_token'], 'secret': oauth_token['oauth_token_secret']}
        return self.oauth_token

    def access_token(self, oauth_token={}, oauth_verifier=None):
        self.oauth_token = oauth_token or self.oauth_token
        http_args = {'oauth_verifier': oauth_verifier} if oauth_verifier else {}  # if callback is oob
        resp = self.oauth_request(self.access_token_url, 'GET', http_args)
        oauth_token = dict(parse.parse_qsl(resp.read().decode()))
        self.oauth_token = {'key': oauth_token['oauth_token'], 'secret': oauth_token['oauth_token_secret']}
        return self.oauth_token


class XAuth(Auth):
    def __init__(self, oauth_consumer, username, password):
        Auth.__init__(self, oauth_consumer)
        self.oauth_token = self.xauth(username, password)

    def request(self, http_url, http_method, http_args={}, headers={}):
        return self.oauth_request(http_url, http_method, http_args, headers)

    def xauth(self, username, password):
        http_args = {
            'x_auth_username': username,
            'x_auth_password': password,
            'x_auth_mode': 'client_auth'
        }
        resp = self.oauth_request(self.access_token_url, 'GET', http_args)
        oauth_token = dict(parse.parse_qsl(resp.read().decode()))
        return {'key': oauth_token['oauth_token'], 'secret': oauth_token['oauth_token_secret']}


usage = '''
>>> # Usage:
>>> consumer = {'key': 'your key', 'secret': 'your secret'}
>>> client = OAuth(consumer)                                 # you can pass callback and auth_host
>>> request_token = client.request_token()                   # keep the request_token
>>> print(client.authorize_url)                              # verify the authorization at client.authorize_url
>>>
>>> client = OAuth(consumer, request_token)                  # optional, if you process callback on other page
>>> access_token = client.access_token()                     # keep the access_token
>>> body = {'status': 'test by oauth'}
>>> client.request('/statuses/update', 'POST',  body)
>>>
>>> # OR
>>> client = OAuth(consumer, access_token)                   # access_token is you kept before
>>> body = {'status': 'test by oauth'}
>>> client.request('/statuses/update', 'POST',  body)
>>>
>>> # OR
>>> client = XAuth(consumer, usernanem, password)
>>> body = {'status': 'test by xauth'}
>>> client.request('/statuses/update', 'POST',  body)
>>> '''

if __name__ == '__main__':
    print(usage)
