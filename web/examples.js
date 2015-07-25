[
    {
        "name": "Less teen-oriented new music",
        "main": "Shuffler-6",
        "components": {
            "SpotifyPlaylist-1": {
                "name": "SpotifyPlaylist-1",
                "type": "SpotifyPlaylist",
                "params": {
                    "name": "Today's Top HIts"
                },
                "extra": {
                    "x": 41,
                    "y": 35
                },
                "maxInputs": 0,
                "minInputs": 0,
                "maxOutputs": 1
            },
            "SpotifyPlaylist-2": {
                "name": "SpotifyPlaylist-2",
                "type": "SpotifyPlaylist",
                "params": {
                    "name": "Teen Party"
                },
                "extra": {
                    "x": 43,
                    "y": 111
                },
                "maxInputs": 0,
                "minInputs": 0,
                "maxOutputs": 1
            },
            "ArtistFilter-3": {
                "name": "ArtistFilter-3",
                "type": "ArtistFilter",
                "params": {},
                "extra": {
                    "x": 359,
                    "y": 36
                },
                "maxInputs": 2,
                "minInputs": 2,
                "maxOutputs": 1,
                "true_source": "SpotifyPlaylist-1",
                "false_source": "Concatenate-5"
            },
            "SpotifyPlaylist-4": {
                "name": "SpotifyPlaylist-4",
                "type": "SpotifyPlaylist",
                "params": {
                    "name": "Teen Pop!"
                },
                "extra": {
                    "x": 48,
                    "y": 194.00000000000006
                },
                "maxInputs": 0,
                "minInputs": 0,
                "maxOutputs": 1
            },
            "Concatenate-5": {
                "name": "Concatenate-5",
                "type": "Concatenate",
                "params": {},
                "extra": {
                    "x": 205,
                    "y": 152
                },
                "maxInputs": 20,
                "minInputs": 1,
                "maxOutputs": 1,
                "source_list": [
                    "SpotifyPlaylist-4",
                    "SpotifyPlaylist-2"
                ]
            },
            "Shuffler-6": {
                "name": "Shuffler-6",
                "type": "Shuffler",
                "params": {},
                "extra": {
                    "x": 508,
                    "y": 36
                },
                "maxInputs": 1,
                "minInputs": 1,
                "maxOutputs": 1,
                "source": "ArtistFilter-3"
            }
        },
        "extra": {
            "createdOn": 1437712427203,
            "lastRun": 0,
            "runs": 0,
            "errors": 0,
            "uri": null
        }
    },
    {
        "name": "Combine two playlists",
        "main": "DeDup-1",
        "components": {
            "SpotifyPlaylist-1": {
                "name": "SpotifyPlaylist-1",
                "type": "SpotifyPlaylist",
                "params": {
                    "name": "Morning Commute"
                },
                "extra": {
                    "x": 85,
                    "y": 41
                },
                "maxInputs": 0,
                "minInputs": 0,
                "maxOutputs": 1
            },
            "Alternate-3": {
                "name": "Alternate-3",
                "type": "Alternate",
                "params": {
                    "fail_fast": true
                },
                "extra": {
                    "x": 178,
                    "y": 162
                },
                "maxInputs": 20,
                "minInputs": 1,
                "maxOutputs": 1,
                "source_list": [
                    "SpotifyPlaylist-1",
                    "SpotifyPlaylist-2"
                ]
            },
            "DeDup-1": {
                "name": "DeDup-1",
                "type": "DeDup",
                "params": {
                    "by_name": false
                },
                "extra": {
                    "x": 173,
                    "y": 273
                },
                "maxInputs": 1,
                "minInputs": 1,
                "maxOutputs": 1,
                "source": "Alternate-3"
            },
            "SpotifyPlaylist-2": {
                "name": "SpotifyPlaylist-2",
                "type": "SpotifyPlaylist",
                "params": {
                    "name": "Your favorite coffeehouse"
                },
                "extra": {
                    "x": 259,
                    "y": 35
                },
                "maxInputs": 0,
                "minInputs": 0,
                "maxOutputs": 1
            }
        },
        "extra": {
            "createdOn": 1437547363068,
            "lastRun": 0,
            "runs": 0,
            "errors": 0,
            "uri": null
        }
    },
    {
        "name": "Coffeehouse with an extra dose of Sheeran, but with none of the bad stuff",
        "main": "DeDup-7",
        "components": {
            "SpotifyPlaylist-1": {
                "name": "SpotifyPlaylist-1",
                "type": "SpotifyPlaylist",
                "params": {
                    "name": "Your favorite coffeehouse"
                },
                "extra": {
                    "x": 115,
                    "y": 43
                },
                "maxInputs": 0,
                "minInputs": 0,
                "maxOutputs": 1
            },
            "SpotifyPlaylist-2": {
                "name": "SpotifyPlaylist-2",
                "type": "SpotifyPlaylist",
                "params": {
                    "name": "My banned tracks",
                    "user": "plamere"
                },
                "extra": {
                    "x": 283,
                    "y": 158
                },
                "maxInputs": 0,
                "minInputs": 0,
                "maxOutputs": 1
            },
            "TrackFilter-3": {
                "name": "TrackFilter-3",
                "type": "TrackFilter",
                "params": {},
                "extra": {
                    "x": 496,
                    "y": 91.00000000000006
                },
                "maxInputs": 2,
                "minInputs": 2,
                "maxOutputs": 1,
                "true_source": "Alternate-4",
                "false_source": "SpotifyPlaylist-2"
            },
            "Alternate-4": {
                "name": "Alternate-4",
                "type": "Alternate",
                "params": {
                    "fail_fast": true
                },
                "extra": {
                    "x": 285,
                    "y": 68.00000000000006
                },
                "maxInputs": 20,
                "minInputs": 1,
                "maxOutputs": 1,
                "source_list": [
                    "SpotifyPlaylist-1",
                    "EchoNestArtist-6"
                ]
            },
            "EchoNestArtist-6": {
                "name": "EchoNestArtist-6",
                "type": "EchoNestArtist",
                "params": {
                    "count": 20,
                    "artist": "Ed Sheeran"
                },
                "extra": {
                    "x": 116,
                    "y": 132
                },
                "maxInputs": 0,
                "minInputs": 0,
                "maxOutputs": 1
            },
            "DeDup-7": {
                "name": "DeDup-7",
                "type": "DeDup",
                "params": {
                    "by_name": false
                },
                "extra": {
                    "x": 674,
                    "y": 93
                },
                "maxInputs": 1,
                "minInputs": 1,
                "maxOutputs": 1,
                "source": "TrackFilter-3"
            }
        },
        "extra": {
            "createdOn": 1437576428295,
            "lastRun": 1437576698875,
            "runs": 0,
            "errors": 0,
            "uri": null
        }
    },
    {
        "name": "Gothic Metal front-loaded with Ravenscry",
        "main": "DeDup-10",
        "components": {
            "SpotifyPlaylist-1": {
                "name": "SpotifyPlaylist-1",
                "type": "SpotifyPlaylist",
                "params": {
                    "name": "Gothic / Symphonic Metal"
                },
                "extra": {
                    "x": 128,
                    "y": 43
                },
                "maxInputs": 0,
                "minInputs": 0,
                "maxOutputs": 1
            },
            "First-2": {
                "name": "First-2",
                "type": "First",
                "params": {
                    "sample_size": 20
                },
                "extra": {
                    "x": 284,
                    "y": 44
                },
                "maxInputs": 1,
                "minInputs": 1,
                "maxOutputs": 1,
                "source": "SpotifyPlaylist-1"
            },
            "ArtistTopTracks-3": {
                "name": "ArtistTopTracks-3",
                "type": "ArtistTopTracks",
                "params": {
                    "name": "Ravenscry"
                },
                "extra": {
                    "x": 283,
                    "y": 129
                },
                "maxInputs": 0,
                "minInputs": 0,
                "maxOutputs": 1
            },
            "Concatenate-4": {
                "name": "Concatenate-4",
                "type": "Concatenate",
                "params": {},
                "extra": {
                    "x": 440,
                    "y": 92
                },
                "maxInputs": 20,
                "minInputs": 1,
                "maxOutputs": 1,
                "source_list": [
                    "ArtistTopTracks-3",
                    "First-2"
                ]
            },
            "Shuffler-5": {
                "name": "Shuffler-5",
                "type": "Shuffler",
                "params": {},
                "extra": {
                    "x": 598,
                    "y": 95
                },
                "maxInputs": 1,
                "minInputs": 1,
                "maxOutputs": 1,
                "source": "Concatenate-4"
            },
            "SpotifyPlaylist-6": {
                "name": "SpotifyPlaylist-6",
                "type": "SpotifyPlaylist",
                "params": {
                    "name": "Gothic / Symphonic metal"
                },
                "extra": {
                    "x": 135,
                    "y": 255
                },
                "maxInputs": 0,
                "minInputs": 0,
                "maxOutputs": 1
            },
            "AllButTheFirst-7": {
                "name": "AllButTheFirst-7",
                "type": "AllButTheFirst",
                "params": {
                    "sample_size": 20
                },
                "extra": {
                    "x": 290,
                    "y": 254
                },
                "maxInputs": 1,
                "minInputs": 1,
                "maxOutputs": 1,
                "source": "SpotifyPlaylist-6"
            },
            "Concatenate-9": {
                "name": "Concatenate-9",
                "type": "Concatenate",
                "params": {},
                "extra": {
                    "x": 777,
                    "y": 151
                },
                "maxInputs": 20,
                "minInputs": 1,
                "maxOutputs": 1,
                "source_list": [
                    "Shuffler-5",
                    "AllButTheFirst-7"
                ]
            },
            "DeDup-10": {
                "name": "DeDup-10",
                "type": "DeDup",
                "params": {
                    "by_name": false
                },
                "extra": {
                    "x": 932,
                    "y": 150
                },
                "maxInputs": 1,
                "minInputs": 1,
                "maxOutputs": 1,
                "source": "Concatenate-9"
            }
        },
        "extra": {
            "createdOn": 1437713186176,
            "lastRun": 1437713485353,
            "runs": 0,
            "errors": 0,
            "uri": null
        }
    }
]
