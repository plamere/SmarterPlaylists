import pbl
import datetime
import random
from werkzeug.contrib.cache import SimpleCache
from pbl import spotify_plugs

cache = SimpleCache()

class YesNo(pbl.Conditional):
    def __init__(self, yes, true_source, false_source):

        def func():
            return yes

        super(YesNo, self).__init__(func, true_source, false_source)


class IsWeekend(pbl.Conditional):
    def __init__(self, true_source, false_source):

        def bool_func():
            return datetime.datetime.today().weekday() >= 5

        super(IsWeekend, self).__init__(bool_func, true_source, false_source)

class IsDayOfWeek(pbl.Conditional):
    def __init__(self, day, true_source, false_source):

        def bool_func():
            return datetime.datetime.today().weekday() == day

        super(IsDayOfWeek, self).__init__(bool_func, true_source, false_source)

class IsTimeOfDay(pbl.Conditional):
    def __init__(self, startTime, endTime, true_source, false_source):

        def bool_func():
            return datetime.datetime.today().weekday() == day

        super(IsDayOfWeek, self).__init__(bool_func, true_source, false_source)

class IsTimeOfDay(pbl.Conditional):
    def __init__(self, startTime, endTime, true_source, false_source):

        def bool_func():
            return datetime.datetime.today().weekday() == day

        super(IsDayOfWeek, self).__init__(bool_func, true_source, false_source)

class RandomSelector(object):
    '''
        Randomly selects a track from one of the given inputs
        :param source_list: a list of sources
    '''
    def __init__(self, source_list, fail_fast):
        self.name = 'randomly selecting from ' + ', '.join([s.name for s in source_list])
        self.source_list = source_list
        self.fail_fast = fail_fast

    def next_track(self):
        while (len(self.source_list) > 0):
            src = random.choice(self.source_list)
            track = src.next_track()
            if track:
                return track
            elif not self.fail_fast:
                self.source_list.remove(src)
            else:
                break
        return None;

class RandomStreamSelector(object):
    '''
        Randomly selects a stream from a set of inputs
        :param source_list: a list of sources
    '''
    def __init__(self, source_list):
        self.source_list = source_list
        self.src = random.choice(self.source_list)
        self.name = 'randomly picked ' + self.src.name

    def next_track(self):
        return self.src.next_track()

class Comment(object):
    '''
        Randomly selects a stream from a set of inputs
        :param source_list: a list of sources
    '''
    def __init__(self, text, fontsize=12, color='#000000'):
        self.text = text
        self.name = text
        self.fontsize = fontsize
        self.color = color

    def next_track(self):
        raise pbl.PBLException(self, "a comment is not runnable")

class TrackFilter(object):
    '''
        produces tracks on the true source that are not on the false source
    '''
    def __init__(self, true_source, false_source):
        self.name = 'tracks in ' + true_source.name  + ' that are not in ' + \
            false_source.name
        self.true_source = true_source
        self.false_source = false_source
        self.bad_tracks = set()

    def next_track(self):
        while True:
            bad_track = self.false_source.next_track()
            if bad_track:
                self.bad_tracks.add(bad_track)
            else:
                break

        while True:
            track = self.true_source.next_track()
            if track:
                if track not in self.bad_tracks:
                    return track
            else:
                break
        return None

class ArtistFilter(object):
    '''
        produces tracks on the true source that are not by artists the false source
    '''
    def __init__(self, true_source, false_source):
        self.name = 'tracks in ' + true_source.name  + ' that are not by ' + \
            'artists in' + false_source.name
        self.true_source = true_source
        self.false_source = false_source
        self.bad_artists = set()

    def next_track(self):
        while True:
            bad_track = self.false_source.next_track()
            if bad_track:
                tinfo = pbl.tlib.get_track(bad_track)
                self.bad_artists.add(tinfo['artist'])
            else:
                break

        while True:
            track = self.true_source.next_track()
            if track:
                tinfo = pbl.tlib.get_track(track)
                if tinfo['artist'] not in self.bad_artists:
                    return track
            else:
                break
        return None


MOST = 0
MORE = 1
LESS = 2
LEAST = 3
ALL = 4

class Danceable(pbl.AttributeRangeFilter):
    ranges = [
        (.8, 1),
        (.6, 1),
        (.0, .4),
        (.0, .2),
        (.0, 1),
    ]

    def __init__(self, source, scale):
        min_val = self.ranges[scale] [0]
        max_val = self.ranges[scale] [1]
        super(Danceable, self).__init__(source, "echonest.danceability",
            match=None, min_val=min_val, max_val=max_val)

class Energy(pbl.AttributeRangeFilter):
    ranges = [
        (.8, 1),
        (.6, 1),
        (.0, .4),
        (.0, .2),
        (.0, 1),
    ]

    def __init__(self, source, scale):
        min_val = self.ranges[scale] [0]
        max_val = self.ranges[scale] [1]
        super(Energy, self).__init__(source, "echonest.energy",
            match=None, min_val=min_val, max_val=max_val)

class Live(pbl.AttributeRangeFilter):
    ranges = [
        (.8, 1),
        (.6, 1),
        (.0, .4),
        (.0, .2),
        (.0, 1),
    ]

    def __init__(self, source, scale):
        min_val = self.ranges[scale] [0]
        max_val = self.ranges[scale] [1]
        super(Live, self).__init__(source, "echonest.liveness",
            match=None, min_val=min_val, max_val=max_val)

class SpokenWord(pbl.AttributeRangeFilter):
    ranges = [
        (.8, 1),
        (.6, 1),
        (.0, .4),
        (.0, .2),
        (.0, 1),
    ]

    def __init__(self, source, scale):
        min_val = self.ranges[scale] [0]
        max_val = self.ranges[scale] [1]
        super(SpokenWord, self).__init__(source, "echonest.speechiness",
            match=None, min_val=min_val, max_val=max_val)

class Tempo(pbl.AttributeRangeFilter):

    def __init__(self, source, min_tempo, max_tempo):
        min_val = min_tempo
        max_val = max_tempo
        super(Tempo, self).__init__(source, "echonest.tempo",
            match=None, min_val=min_val, max_val=max_val)

class AllButTheFirst(object):
    '''
        Returns all but the first tracks from a stream

        :param source: the source of tracks
        :param sample_size: the number of tracks to skip
    '''
    def __init__(self, source, sample_size=10):
        self.name = 'all but the first ' + str(sample_size) + ' of ' + source.name
        self.source = source
        self.sample_size = sample_size
        self.buffer = []
        self.filling = True

    def next_track(self):
        while self.filling:
            track = self.source.next_track()
            if track:
                self.buffer.append(track)
            else:
                self.filling = False
                self.buffer = self.buffer[self.sample_size:]

        if len(self.buffer) > 0:
            return self.buffer.pop(0)
        else:
            return None

class AllButTheLast(object):
    '''
        Returns all but the last tracks from a stream

        :param source: the source of tracks
        :param sample_size: the number of tracks to skip
    '''
    def __init__(self, source, sample_size=10):
        self.name = 'all but the last ' + str(sample_size) + ' of ' + source.name
        self.source = source
        self.sample_size = sample_size
        self.buffer = []
        self.filling = True

    def next_track(self):
        while self.filling:
            track = self.source.next_track()
            if track:
                self.buffer.append(track)
            else:
                self.filling = False
                self.buffer = self.buffer[:-self.sample_size:]

        if len(self.buffer) > 0:
            return self.buffer.pop(0)
        else:
            return None


def is_authenticated():
    auth_token = pbl.engine.getEnv('spotify_auth_token')
    return auth_token != None

def get_user():
    user = pbl.engine.getEnv('spotify_user_id')
    return user

def get_spotify():
    return pbl.spotify_plugs._get_spotify()

class PlaylistSave(object):
    ''' A PBL Sink that saves the source stream of tracks to the given playlist

        :param source: the source of tracks to be saved
        :param playlist_name: the name of the playlist
        :param uri: the uri of the playlist

    '''
    def __init__(self, source, playlist_name= None, append=False):
        self.source = source
        self.name = 'save to ' + playlist_name
        self.playlist_name = playlist_name
        self.append = append
        self.buffer = []
        self.saved = False
        self.max_size = 1000

    def next_track(self):
        if not is_authenticated():
            raise pbl.PBLException(self, "not authenticated for save")

        track = self.source.next_track()
        if track and len(self.buffer) < self.max_size:
            self.buffer.append(track)
        elif not self.saved:
            self._save_playlist()
        return track

    def _save_playlist(self):
        self.saved = True
        sp = get_spotify()
        user = get_user()

        if not sp:
            raise pbl.PBLException(self, "not authenticated for save")

        if not user:
            raise pbl.PBLException(self, "no user")

        # TODO - this can be slow if the user has lots of playlists
        # should cache?
        uri = find_playlist_by_name(sp, user, self.playlist_name)
        if uri:
            print 'found', self.playlist_name, uri
        else:
            print 'creating new', self.playlist_name, 'playlist'
            response = sp.user_playlist_create(user, self.playlist_name)
            uri = response['uri']

        pid = get_pid_from_playlist_uri(uri)
        if pid:
            batch_size = 100
            uris = [ 'spotify:track:' + id for id in self.buffer]
            for start in xrange(0, len(uris), batch_size):
                turis = uris[start:start+batch_size]
                if start == 0 and not self.append:
                    print 'replace', start
                    sp.user_playlist_replace_tracks(user, pid, turis)
                else:
                    print 'add', start
                    sp.user_playlist_add_tracks(user, pid, turis)
        else:
            print "Can't get authenticated access to spotify"


def get_pid_from_playlist_uri(uri):
 # spotify:user:plamere:playlist:5pjUedV8eoCJUiYzyo79eq
    split_uri = uri.split(':')
    if len(split_uri) == 5:
        return split_uri[4]
    else:
        return None

def find_playlist_by_name(sp, user, name):
    key = user + ':::' + name
    uri = cache.get(key)
    if not uri: 
        uri = spotify_plugs._find_playlist_by_name(sp, user, name)
        if uri:
            cache.set(key, uri)
    return uri

def save_to_playlist(title, uri, tids):
    sp = get_spotify()
    user = get_user()

    if not sp:
        raise Exception("not authenticated for save")

    if not user:
        raise Exception("no authenticated user")

    if not uri:
        print 'creating new', title, 'playlist'
        response = sp.user_playlist_create(user, title)
        if 'uri' in response:
            uri = response['uri']
        else:
            raise Exception("Can't create playlist " + title)

    pid = get_pid_from_playlist_uri(uri)
    if pid:
        batch_size = 100
        uris = [ 'spotify:track:' + id for id in tids] 
        for start in xrange(0, len(uris), batch_size):
            turis = uris[start:start+batch_size]
            if start == 0:
                print 'replace', start
                sp.user_playlist_replace_tracks(user, pid, turis)
            else:
                print 'add', start
                sp.user_playlist_add_tracks(user, pid, turis)
    else:
        print "Can't get authenticated access to spotify"
    return uri
