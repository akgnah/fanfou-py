fanfou
======

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
   >>> access_token = client.access_token()    # done. keep the access_token

(1). The default callback is `'http://localhost:8080'`.

(2). The default authorize_url is `'http://m.fanfou.com/...'`, you can pass auth_host='fanfou.com' to change it.


If your app is a webapp, maybe you got access_token on callback page, create a new client like that:

.. code-block:: python

   >>> client = fanfou.OAuth(consumer, request_token)
   >>> access_token = client.access_token()    # done.

Way 2:
""""""

.. code-block:: python

   >>> consumer = {'key': 'your key', 'secret': 'your secret'}
   >>> client = fanfou.OAuth(consumer, callback='oob')
   >>> request_token = client.request_token()
   >>> print(client.authorize_url)    # browse the url and copy verifier_code
   >>> verifier_code = 'your verifier_code'
   >>> access_token = client.access_token(oauth_verifier=verifier_code)    # done. keep the access_token

Way 3:
""""""

.. code-block:: python

   >>> consumer = {'key': 'your key', 'secret': 'your secret'}
   >>> access_token =  {'key': 'your key', 'secret': 'your secret'}    # if you have a access_token
   >>> client = fanfou.OAuth(consumer, access_token)    # done

Way 4:
""""""

.. code-block:: python

   >>> consumer = {'key': 'your key', 'secret': 'your secret'}
   >>> client = fanfou.XAuth(consumer, 'username', 'password')    # done.


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
   >>> data = json.loads(resp.read())    # Python3: data = json.loads(resp.read().decode('utf8'))
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
   >>> fanfou.bound(client)    # Note the line
   >>> 
   >>> body = {'page': 2, 'count': 20, 'mode': 'lite'}
   >>> resp = client.statuses.home_timeline()
   >>> data = json.loads(resp.read())    # Python3: data = json.loads(resp.read().decode('utf8'))
   >>> for item in data:
   >>>     print(item['text'])
   >>> 
   >>> body = {'status': 'update status test 2'}
   >>> resp = client.statuses.update(body)
   >>> print(resp.code)

If you want to use style 2, you must **fanfou.bound(client)** before use. They have the same effect, just two different styles.

Just put all you want to request args to a dict (above is body), and then access a API. If you want to upload a photo, please see **pack_image**.
More API details on `Fanfou API Apicategory <https://github.com/FanfouAPI/FanFouAPIDoc/wiki/Apicategory>`_.

**What's new in 0.1.7**

.. code-block:: python

   >>> fanfou.bound(client)
   >>> 
   >>> resp = client.users.show()
   >>> print(resp.json())

In this update, you can get a json directly by using resp.json(). Note that resp.json() is only available in style 2.


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
   >>> print(resp.code)
   >>> 
   >>> # upload photo
   >>> args = {'photo': 'http://static2.fanfou.com/img/fanfou.png', 'status': 'upload online photo'}
   >>> body, headers = fanfou.pack_image(args)
   >>> resp = client.photos.upload(body, headers)
   >>> print(resp.code)

Just put the filename in the args, then pack_image it, and then you can access API. Image file can be local or network files, pack_image will auto read it.

Sometimes you want to provide binary bytes instead of filename when you're writing a webapp, because the data you get from the form is binary. (like `m.setq.me <http://m.setq.me>`_)

.. code-block:: python

   >>> f = open('test.jpg')
   >>> args = {'photo': 'test.jpg', 'status': 'upload local photo'}
   >>> body, headers = fanfou.pack_image(args, binary=f.read())  # Note the line
   >>> f.close()
   >>> resp = client.photos.upload(body, headers)
   >>> print(resp.code)


print_api('plain')
""""""""""""""""""

The following code print all api_access_url that be allowed pass to client.request:

.. code-block:: python

   >>> fanfou.print_api('plain')

If you type the line and watch the results carefully, you will find some api_access_api have *'/:id'*, they are:

* `GET /users/show <https://github.com/FanfouAPI/FanFouAPIDoc/wiki/users.show>`_
* `POST /favorites/destroy <https://github.com/FanfouAPI/FanFouAPIDoc/wiki/favorites.destroy>`_
* `GET /favorites <https://github.com/FanfouAPI/FanFouAPIDoc/wiki/favorites>`_
* `POST /favorites/create <https://github.com/FanfouAPI/FanFouAPIDoc/wiki/favorites.create>`_

Because these API need user_id on it's access_url, so we get user_id from body and replace :id, like that:

.. code-block:: python

   >>> body = {'id': 'home2'}
   >>> resp = client.request('/users/show/:id', 'GET', body)
   >>> data = json.loads(resp.read())  # Python3: data = json.loads(resp.read().decode('utf8'))
   >>> print(data)

The api_access_url will become http://api.fanfou.com/users/show/home2.json (try browse it). Forget to mention that '.json' will add to the access_url.


print_api('bound')
""""""""""""""""""

.. code-block:: python

   >>> fanfou.print_api('bound')

The line like *fanfou.print_api('plain')* but it will print all available methods that like client.statuses.home_timeline.

Your IDE (or editor) can autocomplete them after **fanfou.bound(client)**.

auth class
""""""""""

The module provides the following classes to authorize:

class **OAuth** (oauth_consumer, oauth_token={}, callback=None, auth_host='m.fanfou.com')

class **XAuth** (oauth_consumer, username, password)

Thanks
------

Thank `Fanfou <http://fanfou.com>`_ and thank you for tolerating  my poor English.

If you have any questions, I am here `@home2 <http://fanfou.com/home2>`_.
