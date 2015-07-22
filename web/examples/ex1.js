{
    "components": {
        "ArtistFilter-5": {
            "extra": {
                "x": 596,
                "y": 146
            },
            "false_source": "SpotifyPlaylist-3",
            "maxInputs": 2,
            "minInputs": 2,
            "name": "ArtistFilter-5",
            "params": {},
            "true_source": "SpotifyPlaylist-4",
            "type": "ArtistFilter"
        },
        "ArtistFilter-6": {
            "extra": {
                "x": 594,
                "y": 272
            },
            "false_source": "SpotifyPlaylist-7",
            "maxInputs": 2,
            "minInputs": 2,
            "name": "ArtistFilter-6",
            "params": {},
            "true_source": "ArtistFilter-5",
            "type": "ArtistFilter"
        },
        "DeDup-9": {
            "extra": {
                "x": 851,
                "y": 562
            },
            "maxInputs": 1,
            "minInputs": 1,
            "name": "DeDup-9",
            "params": {
                "by_name": false
            },
            "source": "RandomSelector-11",
            "type": "DeDup"
        },
        "RandomSelector-11": {
            "extra": {
                "x": 848,
                "y": 402
            },
            "maxInputs": 20,
            "minInputs": 1,
            "name": "RandomSelector-11",
            "params": {
                "fail_fast": false
            },
            "source_list": [
                "Sample-10",
                "TrackFilter-1"
            ],
            "type": "RandomSelector"
        },
        "Sample-10": {
            "extra": {
                "x": 846,
                "y": 236
            },
            "maxInputs": 1,
            "minInputs": 1,
            "name": "Sample-10",
            "params": {
                "sample_size": 10
            },
            "source": "SpotifyPlaylist-8",
            "type": "Sample"
        },
        "ShorterThan-1": {
            "extra": {
                "x": 765,
                "y": 661
            },
            "maxInputs": 1,
            "minInputs": 1,
            "name": "ShorterThan-1",
            "params": {
                "time": 1800
            },
            "source": "DeDup-9",
            "type": "ShorterThan"
        },
        "SpotifyPlaylist-3": {
            "extra": {
                "x": 338,
                "y": 78
            },
            "maxInputs": 0,
            "minInputs": 0,
            "name": "SpotifyPlaylist-3",
            "params": {
                "name": "Teen Party"
            },
            "type": "SpotifyPlaylist"
        },
        "SpotifyPlaylist-4": {
            "extra": {
                "x": 596,
                "y": 20
            },
            "maxInputs": 0,
            "minInputs": 0,
            "name": "SpotifyPlaylist-4",
            "params": {
                "name": "Summer Party"
            },
            "type": "SpotifyPlaylist"
        },
        "SpotifyPlaylist-5": {
            "extra": {
                "x": 354,
                "y": 328
            },
            "maxInputs": 0,
            "minInputs": 0,
            "name": "SpotifyPlaylist-5",
            "params": {
                "name": "My banned tracks",
                "user": "plamere"
            },
            "type": "SpotifyPlaylist"
        },
        "SpotifyPlaylist-7": {
            "extra": {
                "x": 344,
                "y": 204
            },
            "maxInputs": 0,
            "minInputs": 0,
            "name": "SpotifyPlaylist-7",
            "params": {
                "name": "My banned artists",
                "user": "plamere"
            },
            "type": "SpotifyPlaylist"
        },
        "SpotifyPlaylist-8": {
            "extra": {
                "x": 842,
                "y": 70
            },
            "maxInputs": 0,
            "minInputs": 0,
            "name": "SpotifyPlaylist-8",
            "params": {
                "name": "beauty and the beast",
                "user": "plamere"
            },
            "type": "SpotifyPlaylist"
        },
        "TrackFilter-1": {
            "extra": {
                "x": 602,
                "y": 402
            },
            "false_source": "SpotifyPlaylist-5",
            "maxInputs": 2,
            "minInputs": 2,
            "name": "TrackFilter-1",
            "params": {},
            "true_source": "ArtistFilter-6",
            "type": "TrackFilter"
        }
    },
    "extra": {
        "createdOn": 1436683426512,
        "errors": 0,
        "lastRun": 1437033936330,
        "runs": 15
    },
    "main": "DeDup-9",
    "name": "good summer music plus a little metal"
}
