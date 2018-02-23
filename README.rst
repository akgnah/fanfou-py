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

Demo
----

下面收集了一些使用 fanfou-py 的应用，可用作参考。

   * `fanfou-m <https://github.com/akgnah/fanfou-m>`_ 饭否手机版复刻
   * `fanfou-bot <https://github.com/akgnah/fanfou-bot>`_ Mr.Greeting 和诗词君
   * `road-tree <https://gist.github.com/akgnah/c76b3089170307df456b04673a525408>`_ 一路一树
   * `Manzarek <https://github.com/fancoo/Manzarek>`_ 相亲 bot
   * `Wox.Plugin.Fanfou <https://github.com/LitoMore/Wox.Plugin.Fanfou>`_ A Wox plugin for Fanfou


循序渐进的饭否机器人教程： `oh-my-robot <https://setq.me/512>`_


安装
----

.. code-block:: bash

    $ sudo pip install fanfou

使用
----

.. code-block:: python

   >>> import fanfou


步骤 1:  认证
^^^^^^^^^^^^^^^^^^

这个模块提供了几种方式来认证，请查看 `Fanfou API OAuth <https://github.com/FanfouAPI/FanFouAPIDoc/wiki/Oauth>`_ 了解更多详情。

方式 1:
""""""""

.. code-block:: python

   >>> consumer = {'key': 'your key', 'secret': 'your secret'}
   >>> client = fanfou.OAuth(consumer)    # (1)(2)
   >>> request_token = client.request_token()
   >>> print(client.authorize_url)    # 浏览这个 url 去认证
   >>> access_token = client.access_token()    # done

(1). 默认 callback 是 '`http://localhost:8080`'。

(2). 默认的 authorize_url 是 '`m.fanfou.com/`...'，你可以传递 auth_host='fanfou.com' 去更改它。

可能你会在其他页面处理 callback 过程，可以创建一个新的 client 用来获取 access_token，就像这样：

.. code-block:: python

   >>> client = fanfou.OAuth(consumer, request_token)
   >>> access_token = client.access_token()    # done
   >>> # or
   >>> client = fanfou.OAuth(consumer)
   >>> access_token = client.access_token(request_token)    # done

方式 2:
""""""""

.. code-block:: python

   >>> consumer = {'key': 'your key', 'secret': 'your secret'}
   >>> client = fanfou.OAuth(consumer, callback='oob')
   >>> request_token = client.request_token()
   >>> print(client.authorize_url)    # 浏览这个 url 并复制 verifier_code
   >>> verifier_code = 'your verifier_code'
   >>> access_token = client.access_token(oauth_verifier=verifier_code)    # done

你同样可以创建一个新的 client 来获取 access_token，就像上面 方式 1 那样。

方式 3:
""""""""

.. code-block:: python

   >>> consumer = {'key': 'your key', 'secret': 'your secret'}
   >>> access_token =  {'key': 'your key', 'secret': 'your secret'}    # access_token 是你之前保存的
   >>> client = fanfou.OAuth(consumer, access_token)    # done

方式 4:
""""""""

.. code-block:: python

   >>> consumer = {'key': 'your key', 'secret': 'your secret'}
   >>> client = fanfou.XAuth(consumer, 'username', 'password')    # done
   >>> access_token = client.access_token()    # 可选, 如果你想保存 access_token

使用 https:
""""""""""""

在最新的版本中，你可以使用 https 向饭否 API 发送请求，指定 fake_https 为真即可：

.. code-block:: python

   >>> consumer = {'key': 'your key', 'secret': 'your secret'}
   >>> client = fanfou.XAuth(consumer, 'username', 'password', fake_https=True)

fake_https 选项在上面的 4 种认证方式中均可用。使用 fake_https 这个名字的原因是，目前饭否 API 服务器 https 还有点小问题，需要手动修改 base_string。在将来饭否修复了这一问题后，我们将会使用 https 而不是 fake_https。


步骤 2: 访问 API
^^^^^^^^^^^^^^^^^^

我们假设你已经通过 步骤 1 取得了 client，现在你有两种访问 API 的风格可选择。

风格 1:
""""""""

.. code-block:: python

   >>> import json
   >>> 
   >>> resp = client.request('/statuses/home_timeline', 'GET')  # resp 是一个 HTTPResponse 实例
   >>> print(resp.code)
   >>> data = json.loads(resp.read())    # Python 3: data = json.loads(resp.read().decode('utf8'))
   >>> for item in data:
   >>>     print(item['text'])
   >>> 
   >>> body = {'status': 'update status test 1'}
   >>> resp = client.request('/statuses/update', 'POST', body)
   >>> print(resp.code)


风格 2:
""""""""

.. code-block:: python

   >>> import json
   >>>  
   >>> fanfou.bound(client)    # 请留意这一行
   >>> 
   >>> body = {'page': 2, 'count': 20, 'mode': 'lite'}
   >>> resp = client.statuses.home_timeline(body)
   >>> data = json.loads(resp.read())    # Python 3: data = json.loads(resp.read().decode('utf8'))
   >>> for item in data:
   >>>     print(item['text'])
   >>> 
   >>> body = {'status': 'update status test 2'}
   >>> resp = client.statuses.update(body)
   >>> print(resp.code)

如果你想使用 风格 2，在使用之前，你必须先执行 **fanfou.bound(client)**。两种风格具体同样效果，只是不同的风格而已。

只需把你想要请求的参数放到一个字典中（上面是 body），接着把这个字典作为参数去访问 API。如果你想上传图片，请看 **pack_image** 小节。
更多 API 细节（包括每个 API 访问方法和可用参数）可查看 `Fanfou API Apicategory <https://github.com/FanfouAPI/FanFouAPIDoc/wiki/Apicategory>`_。


**有什么新的东西在 0.2.x 版本**

.. code-block:: python

   >>> fanfou.bound(client)
   >>> 
   >>> resp = client.users.show()
   >>> data = resp.json()    # 等价于: data = json.loads(resp.read().decode('utf8')) 

在这个更新中，你可以直接得到一个 Python 对象通过使用 resp.json()。


更多细节
^^^^^^^^^^^^

pack_image(args, binary=None)
"""""""""""""""""""""""""""""

在 API  `/account/update_profile_image <https://github.com/FanfouAPI/FanFouAPIDoc/wiki/account.update-profile-image>`_
和 `/photos/upload <https://github.com/FanfouAPI/FanFouAPIDoc/wiki/photos.upload>`_ 中，你需要上传一个图片, **pack_image** 可以帮你简化这些工作。

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

只需把文件名和他参数放到 args 中，pack_image 它，然后就可以访问 API 了。图片文件可以是本地文件或网络文件， pack_image 会自动读取它。

当你在写一个 Web 应用的时候（就像 `m.setq.me <http://m.setq.me>`_），你可能想要提供一个二进制文件来代替文件名，因为你从表单获取的数据是二进制的。

.. code-block:: python

   >>> f = open('test.jpg', 'rb')
   >>> args = {'photo': 'test.jpg', 'status': 'upload local photo'}
   >>> body, headers = fanfou.pack_image(args, binary=f.read())  # 请留意这一行
   >>> f.close()
   >>> resp = client.photos.upload(body, headers)
   >>> print(resp.code)


print_api('plain')
""""""""""""""""""

下面的代码会打印全部的你可以传递给 client.request 的 api_access_url：

.. code-block:: python

   >>> fanfou.print_api('plain')

如果你输入了上面的代码并细心查看它的结果，你会发现有两个 api_access_url 有  *'/:id'*，它们是：

* `POST /favorites/destroy <https://github.com/FanfouAPI/FanFouAPIDoc/wiki/favorites.destroy>`_
* `POST /favorites/create <https://github.com/FanfouAPI/FanFouAPIDoc/wiki/favorites.create>`_

因为这两个 API 需要 *id* 在它们的 access_url，所以我们会从 body 取得它并替换 :id，就像这样：


.. code-block:: python

   >>> body = {'id': 'zFbiu4CsJrw'}
   >>> resp = client.request('/favorites/create/:id', 'POST', body)
   >>> print(resp.url)

你会看到 resp.url 变成了 http://api.fanfou.com/favorites/create/zFbiu4CsJrw.json （忘了提，'.json' 会自动加到 access_url 的尾部）。

print_api('bound')
""""""""""""""""""

.. code-block:: python

   >>> fanfou.print_api('bound')

这行代码和 *fanfou.print_api('plain')* 相似，但它会打印全部可用的方法（风格 2），就像 client.statuses.home_timeline。
你的 IED （或编辑器）能自动补全这些方法，在你执行了 **fanfou.bound(client)** 之后。

auth classes
""""""""""""

两个 Auth 类的 __init__ 方法如下：

class **OAuth** (oauth_consumer, oauth_token=None, callback=None, auth_host=None, https=False, fake_https=False)

class **XAuth** (oauth_consumer, username, password, https=False, fake_https=False)

致谢
------

感谢 `饭否 <http://fanfou.com>`_ 并且感谢你的关注。如果你有任何问题，我在这里 `@home2 <http://fanfou.com/home2>`_。

许可证
------

MIT © `akgnah <https://github.com/akgnah>`_
