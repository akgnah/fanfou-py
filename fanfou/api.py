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
        ('show', 'GET'),
        ('tag_list', 'GET'),
        ('followers', 'GET'),
        ('recommendation', 'GET'),
        ('cancel_recommendation', 'POST'),
        ('friends', 'GET'),
    ),
    'account': (
        ('verify_credentials', 'GET'),
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
        ('#', 'GET'),
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


def signed(client, apis, func, method):
    def request(args={}, headers={}):
        url = '/{}/{}'.format(apis.__group__, func)
        return client.request(url, method, args, headers)

    setattr(apis, func, request)
    setattr(client, apis.__group__, apis)


def fix_favorites(client):
    class Favorites(APIs):
        def __init__(self):
            del client.favorites.__dict__['#']
            self.__dict__.update(client.favorites.__dict__)
            self.list = self.__call__
            self.create = self.__dict__.pop('create/:id')
            self.destroy = self.__dict__.pop('destroy/:id')

        def __call__(self, args={}, headers={}):
            return client.request('/favorites', 'GET', args, headers)

    client.favorites = Favorites()


def bound(client):
    for group, value in APIs_all.items():
        apis = APIs(group)
        for item in value:
            signed(client, apis, *item)
    fix_favorites(client)
    return client


def print_api(mode='plain'):
    if mode == 'plain':
        tmp = []
        for group, apis in APIs_all.items():
            for api, _ in apis:
                api = api.replace('#', '')
                tmp.append('/%s%s' % (group, api and '/' + api))
        print('\n'.join(tmp))
    else:
        tmp = []
        for group, apis in APIs_all.items():
            for api, _ in apis:
                api = api.replace('#', '').replace('/:id', '')
                tmp.append('client.%s%s' % (group, api and '.' + api))
        print('\n'.join(tmp))


if __name__ == '__main__':
    print_api('plain')
    print()
    print_api('bound')
