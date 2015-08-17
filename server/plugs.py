import pbl
import datetime
import random
import spotipy
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

class MySavedTracks(object):
    ''' A PBL Source that generates a list of the saved tracks
        by the current suer
    '''

    def __init__(self):
        self.name = 'MySavedTracks'
        self.buffer = None

    def next_track(self):
        if self.buffer == None:
            self.buffer = []
            try:
                sp = get_spotify()
                limit = 50
                offset = 0

                remaining = 1
                while remaining > 0:
                    results = sp.current_user_saved_tracks(limit = limit, offset = offset)
                    for item in results['items']:
                        track = item['track']
                        if track and 'id' in track:
                            self.buffer.append(track['id'])
                            spotify_plugs._add_track(self.name, track)
                        else:
                            raise pbl.engine.PBLException(self, 'bad track')

                    if len(results['items']) < limit:
                        remaining = 0
                    else:
                        remaining = results['total'] - (results['offset'] + len(results['items']))
                    offset += limit

            except spotipy.SpotifyException as e:
                raise pbl.engine.PBLException(self, e.msg)

        if len(self.buffer) > 0:
            return self.buffer.pop(0)
        else:
            return None

class MyFollowedArtists(object):
    ''' A PBL Source that generates top tracks from followed artist
        by the current user
    '''

    def __init__(self, num_tracks):
        self.name = 'MyFollowedArtists'
        self.num_tracks = num_tracks
        self.buffer = None

    def next_track(self):
        if self.buffer == None:
            self.buffer = []
            try:
                sp = get_spotify()
                limit = 50
                after = None
                while True:
                    try:
                        results = get_spotify().current_user_followed_artists(limit = limit, after = after)
                    except spotipy.SpotifyException as e:
                        raise pbl.engine.PBLException(self, e.msg)

                    artists = results['artists']
                    items = artists['items']

                    for item in items:
                        artist_id = item['id']
                        after = artist_id
                        try:
                            results = get_spotify().artist_top_tracks(artist_id)
                        except spotipy.SpotifyException as e:
                            raise pbl.engine.PBLException(self, e.msg)

                        for track in results['tracks'][:self.num_tracks]:
                            self.buffer.append(track['id'])
                            spotify_plugs._add_track(self.name, track)
                    if len(items) < limit:
                        break

            except spotipy.SpotifyException as e:
                raise pbl.engine.PBLException(self, e.msg)

        if len(self.buffer) > 0:
            return self.buffer.pop(0)
        else:
            return None

class MixIn(object):
    ''' 
        A PBL Filter that mixes two input streams based upon a small
        set of rules
    '''

    def __init__(self, true_source, false_source, 
        ntracks=1, nskips=1, initial_skip = 1, fail_fast = True):
        '''
            params:
                * true_source
                * false_source
        '''
        self.name = 'mixing ' + true_source.name  + ' with ' + \
            false_source.name
        self.true_source = true_source
        self.false_source = false_source
        self.initial_offset = initial_skip
        self.ntracks = ntracks # false tracks in a row
        self.nskips = nskips   # true tracks in a row
        self.fail_fast = fail_fast
        self.which = 0

    def next_track(self):

        if self.which < self.initial_offset:
            true_count = self.initial_offset
        else:
            true_count = self.nskips

        false_count = self.ntracks
        total_tracks_in_cycle = true_count + false_count
        which_in_cycle = self.which % total_tracks_in_cycle
        use_first = which_in_cycle < true_count

        if use_first:
            next_source = self.true_source
            other_source = self.false_source
        else:
            next_source = self.false_source
            other_source = self.true_source

        track = next_source.next_track()
        if not track:
            if not self.fail_fast:
                track = other_source.next_track()
        self.which += 1
        return track

class SeparateArtists(object):
    ''' A PBL filter that reorders the input tracks to maximize
        the separation between artists
    '''

    def __init__(self, source):
        self.name = 'SeparateArtists'
        self.source = source
        self.tracks = []
        self.filling = True

    def score_list(self):
        min_delta_allowed = 2
        score = 0
        indexes = set()

        for i in xrange(len(self.tracks) - 1):
            aname = self.tracks[i]['artist']
            for j in xrange(i + 1, len(self.tracks)):

                if j - i >= min_delta_allowed:
                    break

                bname = self.tracks[j]['artist']
                if aname == bname:
                    delta = j - i
                    indexes.add(i)
                    indexes.add(j)
                    score += min_delta_allowed - delta

        lindex = list(indexes)
        lindex.sort()
        return score, lindex

    def random_index(self):
        return random.randint(0, len(self.tracks) - 1)

    def swap(self, a, b):
        tmp = self.tracks[a]
        self.tracks[a] = self.tracks[b]
        self.tracks[b] = tmp

    def separate_artists(self):
        max_tries = 1000
        cur_score = 0
        max_no_swaps = 100

        cur_score, indexes = self.score_list()
        no_swap = 0

        for i in xrange(max_tries):

            if cur_score == 0 or len(indexes) == 0:
                break

            swap_1 = random.choice(indexes)
            swap_2 = self.random_index()
            self.swap(swap_1, swap_2)
            new_score, new_indexes = self.score_list()

            if new_score >= cur_score:
                self.swap(swap_2, swap_1)
                no_swap += 1
                if no_swap > max_no_swaps:
                    print 'max swaps'
                    break
            else:
                no_swap = 0
                print i, cur_score, new_score, len(indexes)
                cur_score = new_score
                indexes = new_indexes

            if cur_score == 0:
                break

        return cur_score, len(indexes)

    def create_buffer(self):
        self.buffer = []
        for ti in self.tracks:
            self.buffer.append(ti['id'])

    def next_track(self):
        while self.filling:    
            track = self.source.next_track()
            if track:
                tinfo = pbl.tlib.get_track(track)
                self.tracks.append(tinfo)
            else:
                self.filling = False
                self.separate_artists()
                self.create_buffer()

        if len(self.buffer) > 0:
            return self.buffer.pop()
        else:
            return None


if __name__ == '__main__':
    import sys
    p1 = pbl.ArtistTopTracks(name='Ravenscry')
    p2 = pbl.ArtistTopTracks(name='weezer')
    mi = MixIn(p1, p2, 2,1,1, True)
    pbl.show_source(mi)
