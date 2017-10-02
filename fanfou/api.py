# -*- coding: utf-8 -*-

APIs_all = {
    'search': (
        ('public_timeline', 'GET'),
        ('users', 'GET'),
        ('user_timeline', 'GET'),
    ),
    'blocks': (
        ('ids', 'GET'),
        ('blocking', 'GET'),
        ('create', 'POST'),
        ('exists', 'GET'),
        ('destroy', 'POST'),
    ),
    'users': (
        ('tagged', 'GET'),
        ('show/:id', 'GET'),
        ('tag_list', 'GET'),
        ('followers', 'GET'),
        ('recommendation', 'GET'),
        ('cancel_recommendation', 'GET'),
        ('friends', 'GET'),
    ),
    'account': (
        ('verify_credentials', 'POST'),
        ('update_profile_image', 'POST'),
        ('rate_limit_status', 'GET'),
        ('update_profile', 'POST'),
        ('notification', 'GET'),
        ('update_notify_num', 'POST'),
        ('notify_num', 'GET'),
    ),
    'saved_searches': (
        ('create', 'POST'),
        ('destroy', 'POST'),
        ('show', 'GET'),
        ('list', 'GET'),
    ),
    'photos': (
        ('user_timeline', 'GET'),
        ('upload', 'POST'),
    ),
    'trends': (
        ('list', 'GET'),
    ),
    'followers': (
        ('ids', 'GET'),
    ),
    'favorites': (
        ('destroy/:id', 'POST'),
        (':id', 'GET'),  # list
        ('create/:id', 'POST'),
    ),
    'friendships': (
        ('create', 'POST'),
        ('destroy', 'POST'),
        ('requests', 'GET'),
        ('deny', 'POST'),
        ('exists', 'GET'),
        ('accept', 'POST'),
        ('show', 'GET'),
    ),
    'friends': (
        ('ids', 'GET'),
    ),
    'statuses': (
        ('destroy', 'POST'),
        ('friends_timeline', 'GET'),
        ('home_timeline', 'GET'),
        ('public_timeline', 'GET'),
        ('replies', 'GET'),
        ('followers', 'GET'),
        ('update', 'POST'),
        ('user_timeline', 'GET'),
        ('friends', 'GET'),
        ('context_timeline', 'GET'),
        ('mentions', 'GET'),
        ('show', 'GET'),
    ),
    'direct_messages': (
        ('destroy', 'POST'),
        ('conversation', 'GET'),
        ('new', 'POST'),
        ('conversation_list', 'GET'),
        ('inbox', 'GET'),
        ('sent', 'GET'),
    ),
}


class APIs():
    def __init__(self, group):
        self.__group__ = group

    def __repr__(self):
        return '<APIs ' + dict.__repr__(self.__dict__) + '>'


def signed(client, apis, function, http_method):
    def request(http_args={}, headers={}):
        http_url = '/{}/{}'.format(apis.__group__, function)
        return client.request(http_url, http_method, http_args, headers)
    setattr(apis, function, request)
    setattr(client, apis.__group__, apis)


def fix_apis_key(client):
    client.users.show = client.users.__dict__.pop('show/:id')
    client.favorites.destroy = client.favorites.__dict__.pop('destroy/:id')
    client.favorites.create = client.favorites.__dict__.pop('create/:id')


def fix_favorites(client):
    class APIs_fix(APIs):
        def __init__(self):
            del client.favorites.__dict__[':id']
            self.__dict__.update(client.favorites.__dict__)

        def __call__(self, http_args={}, headers={}):
            return client.request('/favorites/:id', 'GET', http_args, headers)

    favorites = APIs_fix()
    setattr(favorites, 'list', favorites.__call__)
    setattr(client, 'favorites', favorites)


def bound(client):
    for key, value in APIs_all.items():
        apis = APIs(key)
        for item in value:
            signed(client, apis, *item)
    fix_apis_key(client)
    fix_favorites(client)


def print_api(mode='plain'):
    def cut(s):
        return (s[:-4] or 'list') if s.endswith(':id') else s

    if mode == 'plain':
        tmp = []
        for group, apis in APIs_all.items():
            for api, _ in apis:
                tmp.append('/%s/%s' % (group, api))
        print('\n'.join(tmp))
    else:
        tmp = []
        for group, apis in APIs_all.items():
            for api, _ in apis:
                tmp.append('client.%s.%s' % (group, cut(api)))
        print('\n'.join(tmp))


if __name__ == '__main__':
    print_api('plain')
    print()
    print_api('bound')
