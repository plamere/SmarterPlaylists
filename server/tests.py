# -*- coding: latin-1 -*-
import pbl
import unittest
import pprint

from pbl import engine,Dumper
from plugs import *

silent_running = True

def runner(source, max_tracks = 100, props=[]):
    if not silent_running:
        pipeline = source
    else:
        pipeline = pbl.Dumper(source, props)
    return engine.run_source(pipeline, max_tracks)

class TestPlugs(unittest.TestCase):

    def test_artist_dedup(self):
        print 'with dedup'
        src = pbl.PlaylistSource("extender test", None, 'plamere')
        src = ArtistDeDup(src)
        de_dup_size = runner(src, 500)

        src = pbl.PlaylistSource("extender test", None, 'plamere')
        undup_size = runner(src, 500)
        assert de_dup_size < undup_size

    def test_artist_separation(self):
        src = pbl.PlaylistSource("extender test", None, 'plamere')
        runner(src, 500)

        src = pbl.PlaylistSource("extender test", None, 'plamere')
        asep  = ArtistSeparation(src, 4, True)
        runner(asep, 500)

    def test_artist_separation2(self):
        src = pbl.PlaylistSource("extender test", None, 'plamere')
        asep  = ArtistSeparation(src, 4, False)
        runner(asep, 500)

if __name__ == '__main__':
    unittest.main()
