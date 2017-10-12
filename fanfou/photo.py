# -*- coding: utf-8 -*-
import re
import six
import random
import mimetypes
from six.moves.urllib import request


def encode(s):
    if isinstance(s, int):
        s = str(s)
    if not isinstance(s, six.binary_type):
        s = s.encode('utf-8')
    return s


def open_image(filename):
    if re.match('http[s]?:.*', filename):
        image = request.urlopen(filename)
    else:
        image = open(filename, 'rb')
    return image.read()


def pack_image(args, binary=None):
    if not isinstance(args, dict):
        raise Exception('TypeError: argument args: expected a dict')

    # build the mulitpart-formdata body
    body = []
    name = 'photo' if args.get('photo') else 'image'
    filename = args.pop(name)
    BOUNDARY = str(random.random())
    for key, value in args.items():
        body.append('--' + BOUNDARY)
        body.append('Content-Disposition: form-data; name="%s"' % key)
        body.append('Content-Type: text/plain; charset=US-ASCII')
        body.append('Content-Transfer-Encoding: 8bit')
        body.append('')
        body.append(encode(value))
    body.append('--' + BOUNDARY)
    body.append('Content-Disposition: form-data; name="%s"; filename="%s"' % (name, filename))
    body.append('Content-Type: %s' % mimetypes.guess_type(filename)[0])
    body.append('Content-Transfer-Encoding: binary')
    body.append('')
    if not binary:
        binary = open_image(filename)
    body.append(binary)
    body.append('--' + BOUNDARY + '--')
    body.append('')
    body = map(lambda s: isinstance(s, bytes) and s or s.encode(), body)
    body = b'\r\n'.join(body)
    # build the headers
    headers = {
        'Content-Type': 'multipart/form-data; boundary=' + BOUNDARY,
        'Content-Length': len(body)
    }

    return {'form-data': body}, headers


'''
args = {'photo': 'test.jpg', 'status': 'upload a new photo'}
body, headers = pack_image(args)
client.request('/photos/upload', 'POST', body, headers)

args = {'image': 'test.jpg', 'mode': 'lite'}
body, headers = pack_image(args)
client.request('/account/update_profile_image', 'POST', body, headers)
'''
