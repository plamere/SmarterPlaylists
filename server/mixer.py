import pbl

class Mixer(object):
    '''
        A PBL Filter that mixes any number of input streams
        based upon a set of rules
    '''

    def __init__(self, source_list, bad_track_source, bad_artist_source,
        dedup, min_artist_separation, fail_fast, max_tracks):
        '''
        '''
        self.name = 'mixer'
        self.source_list = [pbl.PushableSource(s) for s in source_list]
        self.bad_track_source = bad_track_source
        self.bad_artist_source = bad_artist_source
        self.dedup = dedup 
        self.min_artist_separation = min_artist_separation
        self.fail_fast = fail_fast
        self.max_tracks = max_tracks
        self.retry_tracks = True

        self.bad_artists = set()
        self.bad_tracks = set()
        self.artist_history = None
        self.cur_channel = 0
        self.prepped = False

    def next_track(self):
        self.prep()
        pushback = []
        consecutive_fails = 0
        while len(self.source_list) > 0 and len(self.artist_history) < self.max_tracks:
            if consecutive_fails >= len(self.source_list):
                return None
            candidate_track = self.get_next_candidate()
            if candidate_track == None:
                if self.fail_fast:
                    return None
                else:
                    if len(pushback) > 0:
                        consecutive_fails += 1
                        self.push(pushback)
                        pushback = []
                        self.next_channel()
                    else:
                        consecutive_fails = 0
                        del self.source_list[self.cur_channel]
                        if self.cur_channel >= len(self.source_list):
                            self.cur_channel = 0
            else:
                good, could_be_good = self.good_candidate(candidate_track)
                if good:
                    self.add_to_history(candidate_track)
                    self.push(pushback)
                    self.next_channel()
                    return candidate_track
                else:
                    if could_be_good:
                        pushback.append(candidate_track)
                        
        return None

                
    def push(self, pushback):
        if self.retry_tracks:
            for t in reversed(pushback):
                self.push_track(t)

    def add_to_history(self, track):
        tinfo = pbl.tlib.get_track(track)
        self.track_history.add(track)
        self.artist_history.append(tinfo['artist'])

    def next_channel(self):
        self.cur_channel += 1
        if self.cur_channel >= len(self.source_list):
            self.cur_channel = 0

    def get_next_candidate(self):
        return self.source_list[self.cur_channel].next_track()

    def push_track(self,track):
        return self.source_list[self.cur_channel].push(track)

    def good_candidate(self, track):
        tinfo = pbl.tlib.get_track(track)
        artist = tinfo['artist']

        if self.dedup:
            if track in self.track_history:
                return False, False

        if track in self.bad_tracks:
            return False, False

        if artist in self.bad_artists:
            return False, False

        sep = self.get_artist_sep(artist)
        if sep < self.min_artist_separation:
            return False, self.min_artist_separation < self.max_tracks
        return True, True

    def get_artist_sep(self, artist):
        for idx, hartist in enumerate(reversed(self.artist_history)):
            if artist == hartist:
                return idx + 1
        return sys.maxint
            

    def prep(self):
        if not self.prepped:
            self.prepped = True
            if self.bad_artist_source:
                while True:
                    bad_track = self.bad_artist_source.next_track()
                    if bad_track:
                        tinfo = pbl.tlib.get_track(bad_track)
                        self.bad_artists.add(tinfo['artist'])
                    else:
                        break

            if self.bad_track_source:
                while True:
                    bad_track = self.bad_track_source.next_track()
                    if bad_track:
                        self.bad_tracks.add(bad_track)
                    else:
                        break

            self.artist_history = []
            self.track_history = set()

if __name__ == '__main__':
    import sys
    # first test
    p1 = pbl.ArtistTopTracks(name='Ravenscry')
    p2 = pbl.ArtistTopTracks(name='weezer')
    p2 = pbl.ArtistTopTracks(name='weezer')
    p3 = pbl.PlaylistSource(name='RapCaviar')
    mi = Mixer([p1, p2, p3], None, None, True, 5, False, 50)
    pbl.show_source(mi)
    p1 = pbl.PlaylistSource(name='RapCaviar')
    p2 = pbl.PlaylistSource(name='Rise & Shine')
    p3 = pbl.PlaylistSource(name='extender test', uri='spotify:user:plamere:playlist:7pcDE4xQBZtz3brznnEN8L')
    p4 = pbl.AlbumSource('Tarkus', 'Emerson, Lake & Palmer')
    p5 = pbl.AlbumSource('Brain Salad Surgery', 'Emerson, Lake & Palmer')
    skip = pbl.AlbumSource('Brain Salad Surgery', 'Emerson, Lake & Palmer')
    mi = Mixer([p1, p2, p3, p4, p5], None, None, True, 2, False, 100)
    pbl.show_source(mi, props=['source'])
    # second test

