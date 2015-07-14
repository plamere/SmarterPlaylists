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
