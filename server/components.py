import pbl
import plugs
import copy
import pyen

exported_inventory = None
en = pyen.Pyen()


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
            { "name" : "Echo Nest", "value" : "echonest" }
         ],

         "scale": [
            { "name" : "most", "value" : 0 },
            { "name" : "more", "value" : 1 },
            { "name" : "less", "value" : 2 },
            { "name" : "least", "value" : 3 },
            { "name" : "all", "value" : 4 },
         ],

         "range_attributes" : [
            { "name" : "artist discovery", "value" : "echonest.artist_discovery"},
            { "name" : "speechiness", "value" : "echonest.speechiness"},
            { "name" : "song currencey rank", "value" : "echonest.song_currency_rank"},
            { "name" : "acousticness", "value" : "echonest.acousticness"},
            { "name" : "danceability", "value" : "echonest.danceability"},
            { "name" : "song currency", "value" : "echonest.song_currency"},
            { "name" : "artist familiarity", "value" : "echonest.artist_familiarity"},
            { "name" : "energy", "value" : "echonest.energy"},
            { "name" : "song hotttnesss", "value" : "echonest.song_hotttnesss"},
            { "name" : "tempo", "value" : "echonest.tempo"},
            { "name" : "instrumentalness", "value" : "echonest.instrumentalness"},
            { "name" : "key", "value" : "echonest.key"},
            { "name" : "album date", "value" : "echonest.album_date"},
            { "name" : "liveness", "value" : "echonest.liveness"},
            { "name" : "artist hotttnesss", "value" : "echonest.artist_hotttnesss"},
            { "name" : "artist hotttnesss rank", "value" : "echonest.song_hotttnesss_rank"},
            { "name" : "mode", "value" : "echonest.mode"},
            { "name" : "time signature", "value" : "echonest.time_signature"},
            { "name" : "loudness", "value" : "echonest.loudness"},
            { "name" : "valence", "value" : "echonest.valence"},
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
            { "name" : "artist name ", "value" : "artist"},
            { "name" : "title", "value" : "title"},
            { "name" : "artist discovery", "value" : "echonest.artist_discovery"},
            { "name" : "speechiness", "value" : "echonest.speechiness"},
            { "name" : "song currencey rank", "value" : "echonest.song_currency_rank"},
            { "name" : "acousticness", "value" : "echonest.acousticness"},
            { "name" : "danceability", "value" : "echonest.danceability"},
            { "name" : "song currency", "value" : "echonest.song_currency"},
            { "name" : "artist familiarity", "value" : "echonest.artist_familiarity"},
            { "name" : "energy", "value" : "echonest.energy"},
            { "name" : "song hotttnesss", "value" : "echonest.song_hotttnesss"},
            { "name" : "tempo", "value" : "echonest.tempo"},
            { "name" : "instrumentalness", "value" : "echonest.instrumentalness"},
            { "name" : "key", "value" : "echonest.key"},
            { "name" : "album date", "value" : "echonest.album_date"},
            { "name" : "liveness", "value" : "echonest.liveness"},
            { "name" : "artist hotttnesss", "value" : "echonest.artist_hotttnesss"},
            { "name" : "artist hotttnesss rank", "value" : "echonest.song_hotttnesss_rank"},
            { "name" : "mode", "value" : "echonest.mode"},
            { "name" : "time signature", "value" : "echonest.time_signature"},
            { "name" : "loudness", "value" : "echonest.loudness"},
            { "name" : "valence", "value" : "echonest.valence"},
            { "name" : "src", "value" : "src"},
            { "name" : "duration", "value" : "duration"},
            { "name" : "artist", "value" : "artist"},
            { "name" : "title", "value" : "title"},
            { "name" : "popularity", "value" : "spotify.popularity"},
            { "name" : "explicit", "value" : "spotify.explicit"},
            { "name" : "track number", "value" : "spotify.track_number"},
            { "name" : "disc number", "value" : "spotify.disc_number"}
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
            run much faster.  Supported annotation types are <i>echonest</i>
            and <i>spotify</i>""",
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
                    "default" : "echonest",
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
            "display": "Comment",
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
            "help": """ This component will search for the most popular track
            with the given title and artist of the track""",
            "display": "track",
            "type" : "source",
            "title" : "$title",
            "description": "generates a single track given its name",
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
            "params": {
                "source": {
                    "type" : "source",
                    "optional" : False,
                    "description": "the source of the tracks",
                },
                "artistNames": {
                    "type" : "string_list",
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
            "help" : """ This component will load tracks from the given Spotify
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
            "name" : "First",
            "class": pbl.First,
            "type" : "filter",
            "title" : "first $sample_size",
            "display": "first",
            "description": "Returns the first tracks from a stream",
            "params": {
                "source": {
                    "type" : "source",
                    "optional" : False,
                    "description": "the source of the tracks",
                },
                "sample_size": {
                    "type" : "number",
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
            "help" : """ This component returns the last <b> size </b> number of
            tracks on the input stream""",
            "params": {
                "source": {
                    "type" : "source",
                    "optional" : False,
                    "description": "the source of the tracks",
                },
                "sample_size": {
                    "display" : "size",
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
            "params": {
                "source": {
                    "type" : "source",
                    "optional" : False,
                    "description": "the source of the tracks",
                },
                "sample_size": {
                    "type" : "number",
                    "optional" : False,
                    "description": "the number of tracks to return"
                }
            }
        },
        {
            "name" : "ShorterThan",
            "class": pbl.ShorterThan,
            "type" : "filter",
            "title" : "no longer than $time",
            "display" : "no longer than",
            "description": "Limit the stream, if possible, to tracks with a" + \
                "duration that is no longer than the given time",
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
            "description": "Limit the stream, if possible, to tracks with a" + \
                "duration that is no shorter than the given time",
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
            "params": {
                "source": {
                    "type" : "source",
                    "optional" : False,
                    "description": "the source of the tracks",
                },
                "max_size": {
                    "type" : "number",
                    "optional" : True,
                    "description": "maximum tracks to shuffle"
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
            "description": "randomly select tracks from multiple streams",
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
                    "description": "if not empty attribute value must be at least this"
                },
                "max_val": {
                    "type" : "number",
                    "optional" : True,
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
    

