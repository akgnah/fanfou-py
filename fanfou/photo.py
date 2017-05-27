# -*- coding: utf-8 -*-
import re
import random
import mimetypes
from six.moves.urllib import request


def open_image(filename):
    if re.match('http[s]?:.*', filename):
        image = request.urlopen(filename)
    else:
        image = open(filename, 'rb')
    return image.read()


def pack_image(filename, status=None, binary=None):
    'binary used for web form'
    # build the mulitpart-formdata body
    BOUNDARY = str(random.random())
    body = []
    if status:
        body.append('--' + BOUNDARY)
        body.append('Content-Disposition: form-data; name="status"')
        body.append('Content-Type: text/plain; charset=US-ASCII')
        body.append('Content-Transfer-Encoding: 8bit')
        body.append('')
        body.append(status)
    body.append('--' + BOUNDARY)
    body.append('Content-Disposition: form-data; name="photo"; filename="%s"' % filename)
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


# body, headers = pack_image('test.jpg', '#test#')
# client.request('/photos/upload', 'POST', body, headers)
