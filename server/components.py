import pbl
import plugs
import copy
import pyen

exported_inventory = None
en = pyen.Pyen()
en.debug=True


inventory = {
    "types" : {
        "day_of_week": [
            { "name": "Monday", "value": 0 },
            { "name": "Tuesday", "value": 1 },
            { "name": "Wednesday", "value": 2 },
            { "name": "Thursday", "value": 3 },
            { "name": "Friday", "value": 4 },
            { "name": "Saturday", "value": 5 },
            { "name": "Sunday", "value": 6 }
        ],
        "color": [
            { "name": "black", "value": "#000000" },
            { "name": "red", "value": "#ff0000"  },
            { "name": "green", "value": "#00ff00"  },
            { "name": "blue", "value": "#0000ff"  },
         ],
         "annotations": [
            { "name" : "Spotify", "value" : "spotify" },
            { "name" : "Echo Nest", "value" : "echonest" },
            { "name" : "audio", "value" : "audio" }
         ],

         "scale": [
            { "name" : "most", "value" : 0 },
            { "name" : "more", "value" : 1 },
            { "name" : "less", "value" : 2 },
            { "name" : "least", "value" : 3 },
            { "name" : "all", "value" : 4 },
         ],

         "range_attributes" : [
            { "name" : "artist popularity", "value" : "spotify.primary_artist_popularity"},
            { "name" : "artist followers", "value" : "spotify.primary_artist_followers"},
            { "name" : "album popularity", "value" : "spotify.album_popularity"},
            { "name" : "album date", "value" : "spotify.album_release_date"},
            { "name" : "track popularity", "value" : "spotify.popularity"},

            { "name" : "speechiness", "value" : "audio.speechiness"},
            { "name" : "acousticness", "value" : "audio.acousticness"},
            { "name" : "danceability", "value" : "audio.danceability"},
            { "name" : "energy", "value" : "audio.energy"},
            { "name" : "tempo", "value" : "audio.tempo"},
            { "name" : "instrumentalness", "value" : "audio.instrumentalness"},
            { "name" : "key", "value" : "audio.key"},
            { "name" : "liveness", "value" : "audio.liveness"},
            { "name" : "mode", "value" : "audio.mode"},
            { "name" : "time signature", "value" : "audio.time_signature"},
            { "name" : "loudness", "value" : "audio.loudness"},

            { "name" : "src", "value" : "src"},
            { "name" : "duration", "value" : "duration"},
            { "name" : "artist", "value" : "artist"},
            { "name" : "title", "value" : "title"},

            { "name" : "popularity", "value" : "spotify.popularity"},
            { "name" : "explicit", "value" : "spotify.explicit"},
            { "name" : "track number", "value" : "spotify.track_number"},
            { "name" : "disc number", "value" : "spotify.disc_number"}
         ],
         "sort_attributes" : [
            { "name" : "artist popularity", "value" : "spotify.primary_artist_popularity"},
            { "name" : "artist followers", "value" : "spotify.primary_artist_followers"},
            { "name" : "album popularity", "value" : "spotify.album_popularity"},
            { "name" : "album date", "value" : "spotify.album_release_date"},
            { "name" : "track popularity", "value" : "spotify.popularity"},

            { "name" : "speechiness", "value" : "audio.speechiness"},
            { "name" : "acousticness", "value" : "audio.acousticness"},
            { "name" : "danceability", "value" : "audio.danceability"},
            { "name" : "energy", "value" : "audio.energy"},
            { "name" : "tempo", "value" : "audio.tempo"},
            { "name" : "instrumentalness", "value" : "audio.instrumentalness"},
            { "name" : "key", "value" : "audio.key"},
            { "name" : "liveness", "value" : "audio.liveness"},
            { "name" : "mode", "value" : "audio.mode"},
            { "name" : "time signature", "value" : "audio.time_signature"},
            { "name" : "loudness", "value" : "audio.loudness"},

            { "name" : "artist name ", "value" : "artist"},
            { "name" : "title", "value" : "title"},
            { "name" : "src", "value" : "src"},
            { "name" : "duration", "value" : "duration"},
            { "name" : "artist", "value" : "artist"},
            { "name" : "title", "value" : "title"},

            { "name" : "popularity", "value" : "spotify.popularity"},
            { "name" : "explicit", "value" : "spotify.explicit"},
            { "name" : "track number", "value" : "spotify.track_number"},
            { "name" : "disc number", "value" : "spotify.disc_number"}

            # TODO - get rid of echonest stuff, add full album attributes, to
            # get the release date, album type, genre and so on
            # add full artist attributes to get artist popularity, genres
            #
         ]
    },
    "components" : [
        {
            "name" : "Annotator",
            "display": "annotate",
            "class": pbl.Annotator,
            "type" : "filter",
            "description": "Annotates tracks with external information",
            "help" : """This component will add information to the tracks on the
            input stream. This can make downstream operations like range filters
            run much faster.  Supported annotation types are <i>echonest</i>,
            <i>audio</i> and <i>spotify</i>""",
            "title" : "annotate with $type data",
            "params": {
                "source": {
                    "type" : "source",
                    "optional" : False,
                    "description": "the source of the tracks",
                },
                "type": {
                    "type" : "annotations",
                    "optional" : False,
                    "default" : "audio",
                    "description": "the type of annotation",
                },
            }
        },
        {
            "name" : "DeDup",
            "display": "de-dup",
            "class": pbl.DeDup,
            "type" : "filter",
            "description": "Remove any duplicate tracks in the stream",
            "help" : """ This component will remove any duplicate tracks from
            the stream.  If <b> By Name </b> is set, then tracks dedupped by
            artist and title, otherwise, they are dedupped based upon their
            track id""",
            "params": {
                "source": {
                    "type" : "source",
                    "optional" : False,
                    "description": "the source of the tracks",
                },
                "by_name": {
                    "display" : "By name",
                    "type" : "bool",
                    "optional" : True,
                    "description": " if True also match by name in addition to the regular ID match",
                },
            }
        },
        {
            "name" : "comment",
            "display": "comment",
            "class": plugs.Comment,
            "type" : "filter",
            "title": "$text",
            "description": "Add a comment to the program",
            "help" : """This component lets you add arbitrary comments to your
            program.  Comments have no effect on how a program will execute""",
            "params": {
                "text": {
                    "type" : "string",
                    "optional" : True,
                    "description": "the text for the comment",
                }
            }
        },
        {
            "name" : "TrackFilter",
            "class": plugs.TrackFilter,
            "display": "track filter",
            "type" : "bool-filter",
            "description": "removes track from a stream",
            "help": """ This component takes two input streams. It produces a
            stream of tracks that consist of the tracks on the green input
            stream with the tracks on the red input stream removed""",
            "params": {
                "true_source": {
                    "type" : "source",
                    "optional" : False,
                    "description": "the source of tracks",
                },
                "false_source": {
                    "type" : "source",
                    "optional" : False,
                    "description": "the tracks to be removed",
                },
            }
        },
        {
            "name" : "ArtistFilter",
            "class": plugs.ArtistFilter,
            "display": "artist filter",
            "type" : "bool-filter",
            "description": "removes track from a stream by artist",
            "help": """ This component takes two input streams. It produces a
            stream of tracks that consist of the tracks on the green input
            stream with the tracks by artists of the tracks on the red input
            stream removed""",
            "params": {
                "true_source": {
                    "type" : "source",
                    "optional" : False,
                    "description": "the source of tracks",
                },
                "false_source": {
                    "type" : "source",
                    "optional" : False,
                    "description": "the tracks (by artist) to be removed",
                },
            }
        },
        {
            "name" : "YesNo",
            "class": plugs.YesNo,
            "display": "yes or no",
            "type" : "bool-filter",
            "description": "selects a stream based on a boolean",

            "help": """ This component excepts a red and a green input stream.
            If the <b> yes </b> parameter is set, tracks from the green stream
            will be passed through, otherwise, tracks from the red stream will
            be passed through""",

            "params": {
                "true_source": {
                    "type" : "source",
                    "optional" : False,
                    "description": "the source of tracks when yes",
                },
                "false_source": {
                    "type" : "source",
                    "optional" : False,
                    "description": "the source of tracks when no",
                },
                "yes": {
                    "type" : "bool",
                    "optional" : False,
                    "description": "if true chose the yes stream",
                },
            }
        },
        {
            "name" : "IsWeekend",
            "class": plugs.IsWeekend,
            "display": "is weekend",
            "type" : "bool-filter",
            "description": "selects a stream based on whether or not today is a weekend",

            "help" : """This component accepts a green and a red stream. If the
            current day is a weekend, tracks from the green stream are passed
            through, otherwise tracks from the red stream are passed
            through.""",

            "params": {
                "true_source": {
                    "type" : "source",
                    "optional" : False,
                    "description": "the source of tracks when it is a weekend",
                },
                "false_source": {
                    "type" : "source",
                    "optional" : False,
                    "description": "the source of tracks when it is not a weekend",
                },
            }
        },
        {
            "name" : "IsDayOfWeek",
            "class": plugs.IsDayOfWeek,
            "type" : "bool-filter",
            "display": "is day of week",
            "title": "is $day",
            "description": "selects a stream based on whether is is the given day of the week",

            "help" : """This component accepts a green and a red stream. If the
            current day matches the day specified, tracks from the green stream are passed
            through, otherwise tracks from the red stream are passed
            through.""",

            "params": {
                "true_source": {
                    "type" : "source",
                    "optional" : False,
                    "description": "the source of tracks when the day matches",
                },
                "false_source": {
                    "type" : "source",
                    "optional" : False,
                    "description": "the source of tracks when the day doesn't match",
                },
                "day": {
                    "type" : "day_of_week",
                    "stype" : "number",
                    "optional" : False,
                    "description": "the day of the week",
                },
            }
        },
        {
            "name" : "AlbumSource",
            "class": pbl.AlbumSource,
            "display": "album",
            "type" : "source",

            "description": "generates a series of tracks given an album",
            "help" : """ If an album <b> uri </b> is specified, the tracks from
            that album are generated, otherwise tracks from the album with the given
            <b>artist</b> and <b>title</b> are generated""",

            "title": "$title",
            "params": {
                "title": {
                    "type" : "string",
                    "optional" : True,
                    "description": "the title of the album",
                },
                "artist": {
                    "type" : "string",
                    "optional" : True,
                    "description": "the name of the artist",
                },
                "uri": {
                    "type" : "uri",
                    "optional" : True,
                    "description": "the uri of the artist",
                },
            }
        },
        {
            "name" : "TrackSource",
            "class": pbl.TrackSource,
            "display": "track uris",
            "type" : "source",
            "description": "generates a series of tracks given their URIs",

            "help": """ This component generates a series of one or more tracks
            given their URIs. You specify the URIs as a comma separated list of
            tracks like so: <pre> spotify:track:69JnEQF6OCntGndij5BTlq,
            spotify:track:00t1USAjV7tiTDwlN6U44I </pre>.""",

            "params": {
                "uris": {
                    "type" : "uri_list",
                    "optional" : False,
                    "description": "a list of track uris",
                },
            }
        },
        {
            "name" : "TrackSourceByName",
            "class": pbl.TrackSourceByName,
            "description": "generates a single track given its name",

            "help": """ This component will search for the most popular track
            with the given title and artist.""",

            "display": "track",
            "type" : "source",
            "title" : "$title",
            "params": {
                "title": {
                    "type" : "string",
                    "optional" : False,
                    "description": "the title and artist of the track",
                },
            }
        },
        {
            "name" : "SimpleArtistFilter",
            "class": pbl.ArtistFilter,
            "type" : "filter",
            "display": "Simple artist filter",
            "description": "removes tracks by the given artist",

            "help" : """ This component will remove tracks from the input stream
            that are by the given set of artists. Artists are specified as a
            list of comma separated name.""",

            "params": {
                "source": {
                    "type" : "source",
                    "optional" : False,
                    "description": "the source of the tracks",
                },
                "artistNames": {
                    "type" : "string_list",
                    "display" : "Artist name(s)",
                    "optional" : False,
                    "description": "a list of artist names",
                },
            }
        },
        {
            "name" : "ArtistTopTracks",
            "class": pbl.ArtistTopTracks,
            "type" : "source",
            "display": "artist top tracks",
            "description": "generates a series of top tracks by the given artist",
            "title" : "Top $name tracks",

            "help" : """ This component will generate the top 10 tracks for the
            given artist.  You can specify the artist either by name or by URI.
            If both are given, the URI is used.""",

            "params": {
                "name": {
                    "type" : "string",
                    "optional" : True,
                    "description": "the name of the artist",
                },
                "uri": {
                    "type" : "uri",
                    "optional" : True,
                    "description": "the uri of the artist",
                },
            }
        },
        {
            "name" : "EchoNestGenreRadio",
            "class": pbl.EchoNestGenreRadio,
            "type" : "source",
            "display": "genre radio",
            "description": "generates a series of tracks in the given genre",

            "help": """ This component will generate a stream of tracks given
            the Echo Nest genre. You can chose from a wide range of genres. Use
            <b> count </b> to control how many tracks are returned""",

            "title" : "$genre",
            "params": {
                "genre": {
                    "type" : "genre",
                    "stype" : "string",
                    "optional" : False,
                    "default": "emo",
                    "description": "the genre of interest",
                },
                "count": {
                    "type" : "number",
                    "optional" : True,
                    "default" : 20,
                    "description": "The number of tracks to generate",
                },
            }
        },
        {
            "name" : "EchoNestArtistRadio",
            "class": pbl.EchoNestArtistRadio,
            "type" : "source",
            "display": "artist radio",

            "description": "tracks by the given artist and similar artists",

            "help" : """ This component generates a stream of tracks by the
            given artist or similar artists. The <b>count</b> controls how many
            tracks are generated.""",

            "title" : "$artist radio",
            "params": {
                "artist": {
                    "type" : "string",
                    "optional" : False,
                    "description": "the seed artist",
                },
                "count": {
                    "type" : "number",
                    "optional" : True,
                    "default" : 20,
                    "description": "The number of tracks to generate",
                },
            }
        },
        {
            "name" : "EchoNestArtist",
            "class": pbl.EchoNestArtistPlaylist,
            "type" : "source",
            "display": "artist tracks",
            "description": "tracks by the given artist",

            "help" : """ This component generates a stream of tracks by the
            given artist. The <b>count</b> controls how many tracks are generated.
            The tracks returned will vary from run to run. More popular tracks
            by the artist are favored.""",

            "title" : "$artist",
            "params": {
                "artist": {
                    "type" : "string",
                    "optional" : False,
                    "description": "the seed artist",
                },
                "count": {
                    "type" : "number",
                    "optional" : True,
                    "default" : 20,
                    "description": "The number of tracks to generate",
                },
            }
        },
        {
            "name" : "SpotifyPlaylist",
            "class": pbl.PlaylistSource,
            "type" : "source",
            "display": "playlist",
            "description": "loads tracks from the given spotify playlist",

            "help" : """ This component will generate a stream of tracks from the given Spotify
            playlist.  If you specify a Spotify playlist <b>URI</b>, that playlist will
            be loaded. If you omit the URI but specify a <b>user</b> and a
            <b>name</b>, the user's public playlists will be searched for the playlist with the
            given name. If no user is specified, the most popular playlist with
            the given <b>name</b> will be used.
            """,

            "title": "$name",
            "params": {
                "name": {
                    "type" : "string",
                    "optional" : False,
                    "description": "the name of the playlist",
                    "default" : "Your favorite coffeehouse"
                },
                "user": {
                    "type" : "string",
                    "optional" : True,
                    "description": "the owner of the playlist",
                },
                "uri": {
                    "type" : "string",
                    "optional" : True,
                    "description": "the uri of the playlist",
                },
            }
        },
        {
            "name" : "MySavedAlbums",
            "class": plugs.MySavedAlbums,
            "type" : "source",
            "display": "my saved albums",
            "description": "produces a list of tracks from the current user's saved albums",

            "help" : """ This component will generate a stream of tracks from the
            current user's saved albums
            """,
            "title": "My Saved albums",
            "params": { }
        },
        {
            "name" : "MySavedTracks",
            "class": plugs.MySavedTracks,
            "type" : "source",
            "display": "my saved tracks",
            "description": "produces a list of the current user's saved tracks",

            "help" : """ This component will generate a stream of tracks from the
            current user's saved tracks
            """,
            "title": "My Saved tracks",
            "params": { }
        },
        {
            "name" : "MyFollowedArtists",
            "class": plugs.MyFollowedArtists,
            "type" : "source",
            "display": "followed artists",
            "description": "produces a list tracks by the current user's followed artists",

            "help" : """ This component will generate a stream of tracks from the
            current user's saved tracks
            """,
            "title": "top tracks by my followed artists",
            "params": {
                "num_tracks": {
                    "type" : "number",
                    "optional" : True,
                    "default" : 1,
                    "description": "The number of tracks per artist to generate",
                }
            }
        },
        {
            "name" : "First",
            "class": pbl.First,
            "type" : "filter",
            "title" : "first $sample_size",
            "display": "first",
            "description": "Returns the first tracks from a stream",

            "help": """ This filter will only pass through the first <b> count
            </b> tracks through. Use this filter to limit the tracks to just the
            first <b>count</b> tracks""",

            "params": {
                "source": {
                    "type" : "source",
                    "optional" : False,
                    "description": "the source of the tracks",
                },
                "sample_size": {
                    "display": "count",
                    "type" : "number",
                    "default" : 10,
                    "optional" : False,
                    "description": "the number of tracks to return"
                }
            }
        },

        {
            "name" : "PlaylistSave",
            "class": plugs.PlaylistSave,
            "type" : "filter",
            "title" : "save to Spotify",
            "display": "save to Spotify",
            "description": "save the tracks to a spotify playlist",

            "help": """ This filter will save all the tracks that pass through
            it to the Spotify playlist. If a playlist uri is given, it will
            be used, otherwise, if a playlist with the given name
            already exists it will be written to. If no playlist with the given
            name exists, it will be created.  If the <b> append </b> flag is
            set, the tracks will be appended to the playlist
            """,

            "params": {
                "source": {
                    "type" : "source",
                    "optional" : False,
                    "description": "the source of the tracks",
                },
                "playlist_name": {
                    "display": "name",
                    "type" : "string",
                    "default" : "My Smarter Playlist",
                    "optional" : True,
                    "description": "the name of the playlist"
                },
                "playlist_uri": {
                    "display": "uri",
                    "type" : "uri",
                    "optional" : True,
                    "description": "the uri of the playlist"
                },
                "append": {
                    "display": "append",
                    "type" : "bool",
                    "default" : False,
                    "description": "if true, append tracks to the playlist"
                }
            }
        },

        {
            "name" : "AllButTheFirst",
            "class": plugs.AllButTheFirst,
            "type" : "filter",
            "title" : "all but the first $sample_size",
            "display": "all but the first",
            "description": "Returns all but the first tracks from a stream",

            "help": """ This filter will only pass through all but the first <b> count
            </b> tracks through. Use this filter to limit the tracks to all but the
            first <b>count</b> tracks""",

            "params": {
                "source": {
                    "type" : "source",
                    "optional" : False,
                    "description": "the source of the tracks",
                },
                "sample_size": {
                    "display": "count",
                    "type" : "number",
                    "default" : 10,
                    "optional" : False,
                    "description": "the number of tracks to return"
                }
            }
        },
        {
            "name" : "AllButTheLast",
            "class": plugs.AllButTheLast,
            "type" : "filter",
            "title" : "all but the last $sample_size",
            "display": "all but the last",
            "description": "Returns all but the last tracks from a stream",

            "help": """ This filter will only pass through all but the last <b> count
            </b> tracks through. Use this filter to limit the tracks to all but the
            last <b>count</b> tracks""",

            "params": {
                "source": {
                    "type" : "source",
                    "optional" : False,
                    "description": "the source of the tracks",
                },
                "sample_size": {
                    "display": "count",
                    "type" : "number",
                    "default" : 10,
                    "optional" : False,
                    "description": "the number of tracks to return"
                }
            }
        },
        {
            "name" : "Last",
            "class": pbl.Last,
            "type" : "filter",
            "title" : "last $sample_size",
            "display" : "last",
            "description": "Returns the last tracks from a stream",

            "help" : """ This component returns the last <b> count </b> number of
            tracks on the input stream""",

            "params": {
                "source": {
                    "type" : "source",
                    "optional" : False,
                    "description": "the source of the tracks",
                },
                "sample_size": {
                    "display" : "count",
                    "type" : "number",
                    "optional" : False,
                    "default" : 10,
                    "description": "the number of tracks to return"
                }
            }
        },

        {
            "name" : "Sample",
            "class": pbl.Sample,
            "type" : "filter",
            "display" : "sample",
            "title" : "sample $sample_size tracks",
            "description": "randomly sample tracks from the stream",

            "help" : """ This component will randomly sample up to <b> count </b>
            tracks from the input stream. Sampled tracks may be returned in any
            order""",

            "params": {
                "source": {
                    "type" : "source",
                    "optional" : False,
                    "description": "the source of the tracks",
                },
                "sample_size": {
                    "type" : "number",
                    "optional" : False,
                    "description": "the number of tracks to return",
                    "display" : "count",
                    "default" : 10,
                }
            }
        },
        {
            "name" : "ShorterThan",
            "class": pbl.ShorterThan,
            "type" : "filter",
            "title" : "no longer than $time",
            "display" : "no longer than",
            "description": "Limit the stream, if possible, to tracks with " \
                "a duration that is no longer than the given time",

            "help" : """ This component will limit the stream of tracks to the
            first N tracks that have a total duration that is shorter than the
            given time.  The time is given in the form mm:ss or hh:mm:ss or just
            seconds""",

            "params": {
                "source": {
                    "type" : "source",
                    "optional" : False,
                    "description": "the source of the tracks",
                },
                "time": {
                    "type" : "time",
                    "default" : 900,
                    "optional" : False,
                    "description": "the length in the form hh:mm:ss of the stream of tracks"
                }
            }
        },

        {
            "name" : "LongerThan",
            "class": pbl.LongerThan,
            "type" : "filter",
            "title" : "no shorter than $time",
            "display" : "no shorter than",
            "description": "Limit the stream, if possible, to tracks with " + \
                "a duration that is no shorter than the given time",

            "help" : """ This component will limit the stream of tracks to the
            first N tracks that have a total duration that is longer than the
            given time.  The time is given in the form mm:ss or hh:mm:ss or just
            seconds""",

            "params": {
                "source": {
                    "type" : "source",
                    "optional" : False,
                    "description": "the source of the tracks",
                },
                "time": {
                    "type" : "time",
                    "optional" : False,
                    "default" :  1800,
                    "format" : "time",
                    "description": "the length in the form hh:mm:ss of the stream of tracks"
                }
            }
        },
        {
            "name" : "Shuffler",
            "class": pbl.Shuffler,
            "type" : "filter",
            "title" : "shuffle",
            "display" : "shuffle",
            "description": "Shuffles the tracks in the stream",

            "help" : """
                This component will randomly re-order the input tracks """,

            "params": {
                "source": {
                    "type" : "source",
                    "optional" : False,
                    "description": "the source of the tracks",
                },
            }
        },
        {
            "name" : "SeparateArtists",
            "class": plugs.SeparateArtists,
            "type" : "filter",
            "title" : "separate artists",
            "display" : "separate artists",
            "description": "minimizes the number of adjacent songs by the same artist",

            "help" : """
                This component will re-order the input tracks such that the
                number of adjacent tracks with the same artist is minimized""",

            "params": {
                "source": {
                    "type" : "source",
                    "optional" : False,
                    "description": "the source of the tracks",
                },
            }
        },
        {
            "name" : "MixIn",
            "class": plugs.MixIn,
            "display" : "mix in",
            "title": "mix in",
            "type" : "bool-filter",
            "description": "mix two input streams",

            "help": """ This component allows for more sophisticatd mixing of two
            streams. Tracks are alternately selected from the red and the green
            streams based upon the settings """,

            "params": {
                "true_source": {
                    "type" : "source",
                    "optional" : False,
                    "description": "the primary source of tracks ",
                },
                "false_source": {
                    "type" : "source",
                    "optional" : False,
                    "description": "the mixin source of tracks",
                },
                "fail_fast": {
                    "type" : "bool",
                    "optional" : True,
                    "default" : True,
                    "display" : "fail fast",
                    "description": "if true stop producing tracks "
                        + "as soon as any input stops producing tracks"
                },

                "ntracks": {
                    "type" : "number",
                    "display" : "# red tracks in a row",
                    "optional" : False,
                    "default" : 1,
                    "description": "the number of red tracks in a row"
                },
                "nskips": {
                    "type" : "number",
                    "display" : "# green tracks in a row",
                    "optional" : False,
                    "default" : 1,
                    "description": "the number of green tracks in a row"
                },
                "initial_skip": {
                    "type" : "number",
                    "display" : "initial number of green tracks",
                    "default" : 1,
                    "optional" : False,
                    "description": "the initial number of green tracks"
                }
            }
        },
        {
            "name" : "Reverse",
            "class": pbl.Reverse,
            "type" : "filter",
            "title" : "reverse",
            "display" : "reverse",
            "description": "Reverses the order of the tracks in the stream",

            "help" : """ This component will reverse the order of the input tracks """,

            "params": {
                "source": {
                    "type" : "source",
                    "optional" : False,
                    "description": "the source of the tracks",
                },
            }
        },
        {
            "name" : "Sorter",
            "class": pbl.Sorter,
            "type" : "filter",
            "title": "sort by $reverse $attr",
            "display" : "sort",
            "description": "Sorts the tracks in the stream by the given attribute",

            "help" : """ This component will order the tracks based upon the
            given attribute. The sort can be reversed by selected the <b>
            reverse </b> option.""",

            "params": {
                "source": {
                    "type" : "source",
                    "optional" : False,
                    "description": "the source of the tracks",
                },
                "attr": {
                    "type" : "sort_attributes",
                    "default" : "title",
                    "optional" : False,
                    "description": "the attribute to be sorted on"
                },

                "reverse": {
                    "type" : "bool",
                    "optional" : True,
                    "description": "if true, reverse the sort"
                },
            }
        },
        {
            "name" : "Alternate",
            "class": pbl.Alternate,
            "type" : "multi-in-filter",
            "display" : "alternate",
            "description": "alternate tracks from multiple streams",

            "help" : """ This component takes any number of input streams and
            generates a single output stream by alternating between each of the
            input streams.  If <b> fail fast </b> is set, this component will
            stop producing any tracks once any input stream stops producing
            tracks. If <b>fail fast</b> is not set, this component will continue
            to generate tracks until all input sources are exhausted.""",

            "params": {
                "source_list": {
                    "type" : "source_list",
                    "optional" : False,
                    "description": "the list of sources",
                },
                "fail_fast": {
                    "type" : "bool",
                    "optional" : True,
                    "default" : True,
                    "display" : "fail fast",
                    "description": "if true stop producing tracks "
                        + "as soon as any input stops producing tracks"
                },
            }
        },
        {
            "name" : "RandomSelector",
            "class": plugs.RandomSelector,
            "type" : "multi-in-filter",
            "display" : "random",
            "description": "randomly selects tracks from multiple streams",

            "help" : """This component takes any number of input streams and
            produces tracks by continuosly selecting a random input stream and
            returning the next track from that stream. If <b> fail fast </b> is
            set, this component will stop generating tracks as soon as any of
            its randomly selected sources stops generating tracks.""",

            "params": {
                "source_list": {
                    "type" : "source_list",
                    "optional" : False,
                    "description": "the list of sources",
                },
                "fail_fast": {
                    "type" : "bool",
                    "optional" : True,
                    "default" : True,
                    "display" : "fail fast",
                    "description": "if true stop producing tracks "
                        + "as soon as any input stops producing tracks"
                },
            }
        },

        {
            "name" : "RandomStreamSelector",
            "class": plugs.RandomStreamSelector,

            "help" : """This component will pick one input stream at random and
            use that stream to produce tracks""",

            "type" : "multi-in-filter",
            "display" : "random stream",
            "description": "randomly selects a stream",
            "params": {
                "source_list": {
                    "type" : "source_list",
                    "optional" : False,
                    "description": "the list of sources",
                },
            }
        },
        {
            "name" : "Concatenate",
            "class": pbl.Concatenate,
            "display" : "concatenate",
            "type" : "multi-in-filter",
            "description": "Concatenate tracks from multiple streams",

            "help" : """ This component takes any number of input streams and
            produces tracks by retrieving all the tracks from the first stream,
            followed by all the tracks from the second stream and so on.""",

            "params": {
                "source_list": {
                    "type" : "source_list",
                    "optional" : False,
                    "description": "the list of sources",
                },
            }
        },
        {
            "name" : "AttributeRangeFilter",
            "class": pbl.AttributeRangeFilter,
            "type" : "filter",
            "description": "filter tracks by an attribute",
            "title": "filter $attr",
            "display" : "range filter",

            "help" : """ This component will filter the input stream and only
            pass through tracks that have an attribute that passes the range
            filter.""",

            "params": {
                "source": {
                    "type" : "source",
                    "optional" : False,
                    "description": "the source of the tracks",
                },
                "attr": {
                    "type" : "range_attributes",
                    "optional" : False,
                    "description": "the attribute to be sorted on"
                },

                "match": {
                    "type" : "any",
                    "optional" : True,
                    "description": "if not empty, attribute must match this exactly"
                },

                "min_val": {
                    "type" : "number",
                    "optional" : True,
                    "display" : "min value",
                    "description": "if not empty attribute value must be at least this"
                },
                "max_val": {
                    "type" : "number",
                    "optional" : True,
                    "display" : "max value",
                    "description": "if not empty attribute value must be less than this"
                }
            }
        },
        {
            "name" : "Danceable",
            "class": plugs.Danceable,
            "type" : "filter",
            "title" : "$scale danceable",
            "display": "danceable",
            "description": "filters tracks by their danceability attribute",

            "help" : """ This component will pass through tracks that meet
            the given danceability scale.""",

            "params": {
                "source": {
                    "type" : "source",
                    "optional" : False,
                    "description": "the source of the tracks",
                },
                "scale": {
                    "type" : "scale",
                    "optional" : False,
                    "default" : 0,
                    "stype" : "number",
                    "description": "how danceble are the desired tracks"
                }
            }
        },
        {
            "name" : "Energy",
            "class": plugs.Energy,
            "type" : "filter",
            "title" : "$scale energy",
            "display": "energy",
            "description": "filters tracks by their energy attribute",

            "help" : """ This component will pass through tracks that meet
            the given energy scale.""",

            "params": {
                "source": {
                    "type" : "source",
                    "optional" : False,
                    "description": "the source of the tracks",
                },
                "scale": {
                    "type" : "scale",
                    "optional" : False,
                    "default" : 0,
                    "stype" : "number",
                    "description": "how energetic are the desired tracks"
                }
            }
        },
        {
            "name" : "Explicit",
            "class": plugs.Explicit,
            "type" : "filter",
            "title" : "$explicit",
            "display": "explicit",
            "description": "filters tracks by their explicit attribute",

            "help" : """ This component will pass through tracks that match
            the given explicit criteria.""",

            "params": {
                "source": {
                    "type" : "source",
                    "optional" : False,
                    "description": "the source of the tracks",
                },
                "explicit": {
                    "type" : "bool",
                    "default" : False,
                    "description": """if true, only explicit tracks are passed
                    through, if false no explicit tracks are passed through"""
                }
            }
        },
        {
            "name" : "Live",
            "class": plugs.Live,
            "type" : "filter",
            "title" : "$scale live",
            "display": "live",
            "description": "filters tracks by their liveness attribute",

            "help" : """ This component will pass through tracks that meet
            the given liveness scale.""",

            "params": {
                "source": {
                    "type" : "source",
                    "optional" : False,
                    "description": "the source of the tracks",
                },
                "scale": {
                    "type" : "scale",
                    "optional" : False,
                    "default" : 0,
                    "stype" : "number",
                    "description": "how live are the desired tracks"
                }
            }
        },
        {
            "name" : "Spoken Word",
            "class": plugs.SpokenWord,
            "type" : "filter",
            "title" : "$scale spoken word",
            "display": "spoken word",
            "description": "filters tracks by their speechiness attribute",

            "help" : """ This component will pass through tracks that meet
            the given speechiness scale.""",

            "params": {
                "source": {
                    "type" : "source",
                    "optional" : False,
                    "description": "the source of the tracks",
                },
                "scale": {
                    "type" : "scale",
                    "optional" : False,
                    "default" : 0,
                    "stype" : "number",
                    "description": "how much spoken are the desired tracks"
                }
            }
        },
        {
            "name" : "Tempo",
            "class": plugs.Tempo,
            "type" : "filter",
            "title" : "$min_tempo to $max_tempo BPM",
            "display": "tempo",
            "description": "filters tracks by their tempo",

            "help" : """ This component will pass through tracks that have a
            tempo that is between the given min and max tempos""",

            "params": {
                "source": {
                    "type" : "source",
                    "optional" : False,
                    "description": "the source of the tracks",
                },
                "min_tempo": {
                    "type" : "number",
                    "display" : "Min Tempo",
                    "optional" : True,
                    "description": "the minimum tempo. If omitted, there is no minimum"
                },
                "max_tempo": {
                    "type" : "number",
                    "display" : "Max Tempo",
                    "optional" : True,
                    "description": "the maximum tempo. If omitted, there is no maxiumum"
                }
            }
        },
    ]
}


def export_inventory():
    inventory['types']['genre'] = get_genres()
    inv = copy.deepcopy(inventory)
    for component in inv['components']:
        del component['class']
    return inv

def get_genres():
    response = en.get('genre/list', results=2000)
    gstyle = []
    for g in response['genres']:
        gn = g['name']
        gstyle.append( { 'name': gn, 'value': gn} )
    return gstyle


exported_inventory = export_inventory()


if __name__ == '__main__':
    import json
    print json.dumps(exported_inventory, indent=4)
