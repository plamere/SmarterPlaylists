'''
    Manages spotify auth.
    Uses Authroization code flow as described at

    https://developer.spotify.com/web-api/authorization-guide/

    Usage:

        spauth = SpotifyAuth()

        token = spauth.get_fresh_token(auth_code)

'''

import sys
import os
import time
import simplejson as json
import requests
import redis

class SpotifyAuth(object):

    def __init__(self, r = None):
        print 'creating spotify auth'
        if r:
            self.r = r
        else:
            self.r = redis.StrictRedis(host='localhost', port=6379, db=0)
        self.EXPIRES_THRESHOLD = 120
        self.client_id = os.environ.get('SPOTIPY_CLIENT_ID')
        self.client_secret = os.environ.get('SPOTIPY_CLIENT_SECRET')
        self.client_redirect_uri = os.environ.get('SPOTIPY_REDIRECT_URI')
        self.trace = False

        print 'client id', self.client_id 
        print 'client secret', self.client_secret 
        print 'client rediret uri', self.client_redirect_uri 

        if self.client_id == None or self.client_secret == None or \
            self.client_redirect_uri == None:
            raise Exception('Missing SPOTIPY credentials in the environment')


    def get_fresh_token(self, code):
        print 'gft code', code
        now = time.time()
        token = self._get_token(code)
        print 'gft token', token
        if token:
            if (token['expires_at'] - now) < self.EXPIRES_THRESHOLD:
                print 'gft token refresh', token
                token = self._refresh_token(token)
                if token:
                    self._add_token(code, token)
                    print 'gft token refreshed', token
        else:
            token = self._add_auth_code(code)
            print 'gft token add_auth', token

        print 'gft ret', token
        return token

    def get_fresh_token_for_user(self, user):
        now = time.time()
        token = self._get_token(user)
        if token:
            if (token['expires_at'] - now) < self.EXPIRES_THRESHOLD:
                token = self._refresh_token(token)
                if token:
                    self._add_token(code, token)
        return token

    def _add_auth_code(self, auth_code):
        token = self._get_new_token(auth_code)
        if token:
            token = self._add_token(auth_code, token)
        return token

    def _add_token(self, code, token):
        now = time.time()
        token['expires_at'] = int(now) + token['expires_in']
        user_info = self._me(token)
        if user_info:
            token['user_id'] = user_info['id']
            token['user_name'] = user_info['display_name']

            user = token['user_id']
            self._put('token:' + code, token)
            if self.trace:
                print 'added token to db', code, token
        else:
            print "can't get user info, bailing"
            return None
        return token


    def _get_new_token(self, authorization_code):
        params = {
            'grant_type': 'authorization_code',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'redirect_uri': self.client_redirect_uri,
            'code' : authorization_code
        }
        print 'get_new_token', json.dumps(params, indent=4)
        r = requests.post('https://accounts.spotify.com/api/token', params)
        if r.status_code >= 200 and r.status_code < 300:
            token = r.json()
            if self.trace:
                print 'got back token', token
            return token
        else:
            return None

    def _get_token(self, code):
        key = 'token:' + code
        js = self._get(key)
        return js

    def _refresh_token(self, token):
        params = {
            'grant_type': 'refresh_token',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'refresh_token' : token['refresh_token']
        }
        r = requests.post('https://accounts.spotify.com/api/token', params)
        if r.status_code >= 200 and r.status_code < 300:
            new_token = r.json()
            if self.trace:
                print 'got back token', token
            if not 'refresh_token' in new_token:
                new_token['refresh_token'] = token['refresh_token']
            return new_token
        else:
            raise Exception("can't get token")


    def _me(self, token):
        me_info = self._spget('me', token['access_token'])
        return me_info

    def _spget(self, method, auth, params=None):
        prefix = 'https://api.spotify.com/v1/'
        args = dict(params=params)
        url = prefix + method
        headers = {'Authorization': 'Bearer {0}'.format(auth)}
        headers['Content-Type'] = 'application/json'

        r = requests.get(url, headers=headers, **args)

        if len(r.text) > 0:
            results = r.json()
            if self.trace:  # pragma: no cover
                print('RESP', results)
                print()
            return results
        else:
            return None

    def _get(self, key):
        js = self.r.get(key)
        if js:
            return json.loads(js)
        else:
            return None

    def _put(self, key, val):
        js = json.dumps(val)
        print 'put', key, val
        self.r.set(key, js)

    def delete_auth(self, code):
        key = 'token:' + code
        self.r.delete(key)
    


if __name__ == '__main__':
    spauth = SpotifyAuth()
    arg = sys.argv[1]
    fields = arg.split('=')
    my_code = fields[-1]
    spauth.delete_auth(my_code)
    token = spauth.get_fresh_token(my_code)
    if token:
        remaining = token['expires_at'] - time.time()
        print 'Got a token that expires in', remaining, 'seconds'
    else:
        print 'no token for that code'

