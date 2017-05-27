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

We provide several ways to authorize, see more details on `Fanfou API OAuth <https://github.com/FanfouAPI/FanFouAPIDoc/wiki/Oauth>`_.

Way 1:
""""""

.. code-block:: python

   >>> consumer = {'key': 'your key', 'secret': 'your secret'}
   >>> client = fanfou.OAuth(consumer)     # (1)(2)
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

We assume that you've got client on Step 1, and provide two ways to access API.

Way 1:
""""""

.. code-block:: python

   >>> import json
   >>> 
   >>> resp = client.request('/statuses/home_timeline', 'GET')
   >>> print(resp.code)
   >>> data = json.loads(resp.read())    # Python3: data = json.loads(resp.read().decode('utf8'))
   >>> for item in data:
   >>>     print(item['text'])
   >>> 
   >>> body = {'status': 'update status test'}
   >>> resp = client.request('/statuses/update', 'POST', body)
   >>> print(resp.code)
   >>> 
   >>> body, headers = fanfou.pack_image('test.jpg', 'upload local photo test')
   >>> resp = client.request('/photos/upload','POST', body, headers)
   >>> print(resp.code)
   >>> 
   >>> body, headers = fanfou.pack_image('http://static2.fanfou.com/img/fanfou.png', 'upload online photo test')
   >>> resp = client.request('/photos/upload','POST', body, headers)
   >>> print(resp.code)

Way 2:
""""""

.. code-block:: python

   >>> import json
   >>>  
   >>> fanfou.bound(client)    # Note the line
   >>> 
   >>> resp = client.statuses.home_timeline()
   >>> print(resp.code)
   >>> data = json.loads(resp.read())    # Python3: data = json.loads(resp.read().decode('utf8'))
   >>> for item in data:
   >>>     print(item['text'])
   >>> 
   >>> body = {'status': 'update status test'}
   >>> resp = client.statuses.update(body)
   >>> print(resp.code)
   >>>  
   >>> body, headers = fanfou.pack_image('test.jpg', 'upload local photo')
   >>> resp = client.photos.upload(body, headers)
   >>> print(resp.code)
   >>> 
   >>> body, headers = fanfou.pack_image('http://static2.fanfou.com/img/fanfou.png', 'upload online photo test')
   >>> resp = client.photos.upload(body, headers)
   >>> print(resp.code)

You will see that *client.statuses.home_timeline()* and *client.request('/statuses/home_timeline', 'GET')* are equal after **fanfou.bound(client)**, etc.

You can see the all API details `Fanfou API Apicategory <https://github.com/FanfouAPI/FanFouAPIDoc/wiki/Apicategory>`_.

More details
^^^^^^^^^^^^

print_api('plain')
""""""""""""""""""

You will see all api_access_url that be allowed pass to client.request:

.. code-block:: python

   >>> fanfou.print_api('plain')

If you tpye the line and watch the results carefully, you will find some api_access_api have *'/:id'*, they are:

* `GET /users/show <https://github.com/FanfouAPI/FanFouAPIDoc/wiki/users.show>`_
* `POST /favorites/destroy <https://github.com/FanfouAPI/FanFouAPIDoc/wiki/favorites.destroy>`_
* `GET /favorites <https://github.com/FanfouAPI/FanFouAPIDoc/wiki/favorites>`_
* `POST /favorites/create <https://github.com/FanfouAPI/FanFouAPIDoc/wiki/favorites.create>`_

Because these API need user_id on it's access_url, so we get user_id from body and replace :id, like that:

.. code-block:: python

   >>> body = {'id': 'home2'}
   >>> resp = client.request('/users/show/:id', 'GET', body)
   >>> data = json.loads(resp.read())    # if Python3, resp.read().decode('utf8')
   >>> print(data)

The api_access_url will become http://api.fanfou.com/users/show/home2.json (try browse it). Forget to mention that we will append '.json' to end of the access_url.

The args that you put on body will be passed to api_access_url, all available args see `Fanfou API Apicategory <https://github.com/FanfouAPI/FanFouAPIDoc/wiki/Apicategory>`_.

.. code-block:: python

   >>> body = {'page': 2, 'count': 20, 'mode': 'lite'}
   >>> resp = client.request(/statuses/home_timeline', 'GET', body)
   >>> data = json.loads(resp.read())
   >>> for item in data:
   >>>     print(item['text'])

print_api('bound')
""""""""""""""""""

.. code-block:: python

   >>> fanfou.print_api('bound')

The line like *fanfou.print_api('plain')* but it will print all available methods that like client.statuses.home_timeline().

Your IDE (or editor) can autocomplete them after fanfou.bound(client).

You also can pass args by a dict.

Thanks
------

Thank `Fanfou <http://fanfou.com>`_ and thank you for tolerating  my poor English.

If you have any questions, I am here `@home2 <http://fanfou.com/home2>`_.
