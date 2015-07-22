import pbl
import datetime
import random

class YesNo(pbl.Conditional):
    def __init__(self, yes, true_source, false_source):

        def func():
            return yes

        super(YesNo, self).__init__(func, true_source, false_source)


class IsWeekend(pbl.Conditional):
    def __init__(self, true_source, false_source):

        def bool_func():
            return datetime.datetime.today().weekday() >= 6

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

class Tempo(pbl.AttributeRangeFilter):

    def __init__(self, source, min_tempo, max_tempo):
        min_val = min_tempo
        max_val = max_tempo
        super(Tempo, self).__init__(source, "echonest.tempo",
            match=None, min_val=min_val, max_val=max_val)
