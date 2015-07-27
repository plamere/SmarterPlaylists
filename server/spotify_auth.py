'''
    Manages spotify auth.
    Uses Authroization code flow as described at

    https://developer.spotify.com/web-api/authorization-guide/

    Usage:

        spauth = SpotifyAuth()

        user_id = spauth.add_user(auth_token)

        spauth.get_fresh_user_token(user_id)

'''

import sys
import os
import time
import simplejson as json
import requests
import leveldb

class SpotifyAuth(object):

    def __init__(self, dbpath='.userdb'):
        self.db = leveldb.LevelDB(dbpath)
        self.EXPIRES_THRESHOLD = 120
        self.client_id = os.environ.get('SPOTIPY_CLIENT_ID')
        self.client_secret = os.environ.get('SPOTIPY_CLIENT_SECRET')
        self.client_redirect_uri = os.environ.get('SPOTIPY_REDIRECT_URI')
        self.trace = False

        if self.client_id == None or self.client_secret == None or \
            self.client_redirect_uri == None:
            raise Exception('Missing SPOTIPY credentials in the environment')

    def add_user(self, auth_token):
        # get access token
        user = None
        token = self._get_new_token(auth_token)
        if token:
            # make a 'me' call to get name
            me_info = self._me(token)
            if me_info:
                user = me_info['id']
                self._add_user_token(user, token)
        return user

    def get_fresh_user_token(self, user):
        now = time.time()
        token = self._get_user_token(user)
        if token and (token['expires_at'] - now) < self.EXPIRES_THRESHOLD:
            token = self._refresh_token(token)
            if token:
                self._add_user_token(user, token)
        return token

    def _add_user_token(self, user, token):
        now = time.time()
        token['expires_at'] = int(now) + token['expires_in']
        js = json.dumps(token)
        self.db.Put('token:' + user, js)
        if self.trace:
            print 'added user token to db', user, js

    def _get_new_token(self, authorization_code):
        params = {
            'grant_type': 'authorization_code',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'redirect_uri': self.client_redirect_uri,
            'code' : authorization_code
        }
        r = requests.post('https://accounts.spotify.com/api/token', params)
        if r.status_code >= 200 and r.status_code < 300:
            token = r.json()
            if self.trace:
                print 'got back token', token
            return token
        else:
            return None

    def _get_user_token(self, user):
        key = 'token:' + user
        try:
            js = self.db.Get(key)
            return json.loads(js)
        except KeyError:
            return None


    def _refresh_token(self, token):
        params = {
            'grant_type': 'refresh_token',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'refresh_token' : token['refresh_token']
        }
        r = requests.post('https://accounts.spotify.com/api/token', params)
        if r.status_code >= 200 and r.status_code < 300:
            token = r.json()
            if self.trace:
                print 'got back token', token
            return token
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


if __name__ == '__main__':
    spauth = SpotifyAuth()
    arg = sys.argv[1]
    fields = arg.split('=')
    if len(fields) == 2:
        code = fields[-1]
        user = spauth.add_user(code)
        if user:
            print 'got a code for user', user
            token = spauth.get_fresh_user_token(user)
            if token:
                remaining = token['expires_at'] - time.time()
                print 'Got a token that expires in', remaining, 'seconds'
            else:
                print 'no token for', user
        else:
            print "can't get a user for that code, probably a bad/old code"
    else:
        user = sys.argv[1]
        token = spauth.get_fresh_user_token(user)
        if token:
            remaining = token['expires_at'] - time.time()
            print 'Got a token that expires in', remaining, 'seconds'
        else:
            print 'no token for', user

