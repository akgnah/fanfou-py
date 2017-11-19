fanfou-py: a python oauth client for fanfou
===========================================

.. image:: https://img.shields.io/travis/akgnah/fanfou-py/master.svg
    :target: https://travis-ci.org/akgnah/fanfou-py

.. image:: https://img.shields.io/pypi/v/fanfou.svg
    :target: https://pypi.python.org/pypi/fanfou

.. image:: https://img.shields.io/pypi/l/fanfou.svg
    :target: https://pypi.python.org/pypi/fanfou

.. image:: https://img.shields.io/badge/code_style-pep8-orange.svg
    :target: https://www.python.org/dev/peps/pep-0008

Installation
------------

.. code-block:: bash

    $ sudo pip install fanfou

Usage
-----

.. code-block:: python

   >>> import fanfou


Step 1:  Authorize
^^^^^^^^^^^^^^^^^^

The module provides several ways to authorize, see more details on `Fanfou API OAuth <https://github.com/FanfouAPI/FanFouAPIDoc/wiki/Oauth>`_.

Way 1:
""""""

.. code-block:: python

   >>> consumer = {'key': 'your key', 'secret': 'your secret'}
   >>> client = fanfou.OAuth(consumer)    # (1)(2)
   >>> request_token = client.request_token()
   >>> print(client.authorize_url)    # browse the url to authorize
   >>> access_token = client.access_token()    # done

(1). The default callback is '`http://localhost:8080`'.

(2). The default authorize_url is '`m.fanfou.com/`...', you can pass auth_host='fanfou.com' to change it.

Maybe you handling the callback elsewhere, create a new client and get access_token, like that:

.. code-block:: python

   >>> client = fanfou.OAuth(consumer, request_token)
   >>> access_token = client.access_token()    # done
   >>> # or
   >>> client = fanfou.OAuth(consumer)
   >>> access_token = client.access_token(request_token)    # done

Way 2:
""""""

.. code-block:: python

   >>> consumer = {'key': 'your key', 'secret': 'your secret'}
   >>> client = fanfou.OAuth(consumer, callback='oob')
   >>> request_token = client.request_token()
   >>> print(client.authorize_url)    # browse the url and copy verifier_code
   >>> verifier_code = 'your verifier_code'
   >>> access_token = client.access_token(oauth_verifier=verifier_code)    # done

You can also create a new client and get access_token, like the way 1 above.

Way 3:
""""""

.. code-block:: python

   >>> consumer = {'key': 'your key', 'secret': 'your secret'}
   >>> access_token =  {'key': 'your key', 'secret': 'your secret'}    # access_token is what you saved before
   >>> client = fanfou.OAuth(consumer, access_token)    # done

Way 4:
""""""

.. code-block:: python

   >>> consumer = {'key': 'your key', 'secret': 'your secret'}
   >>> client = fanfou.XAuth(consumer, 'username', 'password')    # done
   >>> access_token = client.access_token()    # optional, if you want to save access_token


Using https:
""""""""""""

In the lastest edition, you can using https like that:

.. code-block:: python

   >>> consumer = {'key': 'your key', 'secret': 'your secret'}
   >>> client = fanfou.XAuth(consumer, 'username', 'password', fake_https=True)

The fake_https is available in all authorize ways.


Step 2: Access API
^^^^^^^^^^^^^^^^^^

We assume that you've got client on Step 1, now you have two styles to access API.

Style 1:
""""""""

.. code-block:: python

   >>> import json
   >>> 
   >>> resp = client.request('/statuses/home_timeline', 'GET')  # resp is a HTTPResponse instance
   >>> print(resp.code)
   >>> data = json.loads(resp.read())    # Python 3: data = json.loads(resp.read().decode('utf8'))
   >>> for item in data:
   >>>     print(item['text'])
   >>> 
   >>> body = {'status': 'update status test 1'}
   >>> resp = client.request('/statuses/update', 'POST', body)
   >>> print(resp.code)


Style 2:
""""""""

.. code-block:: python

   >>> import json
   >>>  
   >>> fanfou.bound(client)    # note the line
   >>> 
   >>> body = {'page': 2, 'count': 20, 'mode': 'lite'}
   >>> resp = client.statuses.home_timeline()
   >>> data = json.loads(resp.read())    # Python 3: data = json.loads(resp.read().decode('utf8'))
   >>> for item in data:
   >>>     print(item['text'])
   >>> 
   >>> body = {'status': 'update status test 2'}
   >>> resp = client.statuses.update(body)
   >>> print(resp.code)

If you want to use style 2, you must **fanfou.bound(client)** before use. They have the same effect, just two different styles.

Just put all you want to request args to a dict (above is body), and then access a API. If you want to upload a photo, please see **pack_image**.
More API details on `Fanfou API Apicategory <https://github.com/FanfouAPI/FanFouAPIDoc/wiki/Apicategory>`_.

**What's new in 0.2.x**

.. code-block:: python

   >>> fanfou.bound(client)
   >>> 
   >>> resp = client.users.show()
   >>> data = resp.json()    # equal: data = json.loads(resp.read().decode('utf8')) 

In this update, you can get a Python object directly by using resp.json().


More details
^^^^^^^^^^^^

pack_image(args, binary=None)
"""""""""""""""""""""""""""""

On `/account/update_profile_image <https://github.com/FanfouAPI/FanFouAPIDoc/wiki/account.update-profile-image>`_
and `/photos/upload <https://github.com/FanfouAPI/FanFouAPIDoc/wiki/photos.upload>`_ you need to upload a image, **pack_image** can help you work easily.

.. code-block:: python

   >>> # update profile image
   >>> args = {'image': 'test.jpg', 'mode': 'lite'}
   >>> body, headers = fanfou.pack_image(args)
   >>> resp = client.account.update_profile_image(body, headers)
   >>> # or, resp = client.request('/account/update_profile_image', 'POST', body, headers)
   >>> print(resp.code)
   >>> 
   >>> # upload photo
   >>> args = {'photo': 'http://static.fanfou.com/img/fanfou.png', 'status': 'upload online photo'}
   >>> body, headers = fanfou.pack_image(args)
   >>> resp = client.photos.upload(body, headers)
   >>> print(resp.code)

Just put the filename in the args, then pack_image it, and then you can access API. The image file can be local or network file, pack_image will auto read it.

Sometimes you want to provide binary bytes instead of filename when you're writing a webapp, because the data you get from the form is binary. (like `m.setq.me <http://m.setq.me>`_)

.. code-block:: python

   >>> f = open('test.jpg')
   >>> args = {'photo': 'test.jpg', 'status': 'upload local photo'}
   >>> body, headers = fanfou.pack_image(args, binary=f.read())  # note the line
   >>> f.close()
   >>> resp = client.photos.upload(body, headers)
   >>> print(resp.code)


print_api('plain')
""""""""""""""""""

The following code print all api_access_url that be allowed pass to client.request:

.. code-block:: python

   >>> fanfou.print_api('plain')

If you type the line and watch the results carefully, you will find two api_access_url have *'/:id'*, they are:

* `POST /favorites/destroy <https://github.com/FanfouAPI/FanFouAPIDoc/wiki/favorites.destroy>`_
* `POST /favorites/create <https://github.com/FanfouAPI/FanFouAPIDoc/wiki/favorites.create>`_

Because these API need *id* on it's access_url, so we get id from body and replace :id, like that:

.. code-block:: python

   >>> body = {'id': 'zFbiu4CsJrw'}
   >>> resp = client.request('/favorites/create/:id', 'POST', body)
   >>> print(resp.url)

You will see resp.url is http://api.fanfou.com/favorites/create/zFbiu4CsJrw.json (Forget to mention that '.json' will add to the access_url).


print_api('bound')
""""""""""""""""""

.. code-block:: python

   >>> fanfou.print_api('bound')

The line like *fanfou.print_api('plain')* but it will print all available methods that like client.statuses.home_timeline.

Your IDE (or editor) can autocomplete them after **fanfou.bound(client)**.

auth classes
""""""""""""

The __init__ method for auth classes is as follows:

class **OAuth** (oauth_consumer, oauth_token=None, callback=None, auth_host=None, https=False, fake_https=False)

class **XAuth** (oauth_consumer, username, password, https=False, fake_https=False)

Thanks
------

Thank `Fanfou <http://fanfou.com>`_ and thank you for tolerating  my poor English.

If you have any questions, I am here `@home2 <http://fanfou.com/home2>`_.
