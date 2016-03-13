import pbl
import plugs
import copy
import pyen
import datetime
import mixer

exported_inventory = None
en = pyen.Pyen()
en.debug=True

genres_enabled = True


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

         "playlist_suffix": [
            { "name" : "none", "value" : "none" },
            { "name" : "time", "value" : "time" },
            { "name" : "date", "value" : "date" },
            { "name" : "day-of-week", "value" : "day-of-week" },
            { "name" : "day-of-month", "value" : "day-of-month" }
         ],

         "scale": [
            { "name" : "most", "value" : 0 },
            { "name" : "more", "value" : 1 },
            { "name" : "less", "value" : 2 },
            { "name" : "least", "value" : 3 },
            { "name" : "all", "value" : 4 },
         ],

         "time_range": [
            { "name": "short term", "value": "short_term" },
            { "name": "medium term", "value": "medium_term" },
            { "name": "long term", "value": "long_term" }
         ],

         "range_attributes" : [
            { 
                "name" : "artist popularity", 
                "value" : "spotify.primary_artist_popularity",
                "min_value": 0,
                "max_value": 100,
                "description": """ A normalized estimation of how popular the
                primary artist of a track is based on recent streaming."""
            },
            { 
                "name" : "artist followers", 
                "value" : "spotify.primary_artist_followers",
                "min_value" : 0,
                "description": """ The current number of followers for the
                primary artist of the track."""
            },
            { 
                "name" : "album popularity", 
                "value" : "spotify.album_popularity",
                "min_value": 0,
                "max_value": 100,
                "description": """ A normalized estimation of how popular the
                album of a track is based on recent streaming."""
            },
            { 
                "name" : "track popularity", 
                "value" : "spotify.popularity",
                "min_value": 0,
                "max_value": 100,
                "description": """ A normalized estimation of how popular the
                track is based on recent streaming."""
            },
            { 
                "name" : "speechiness", 
                "value" : "audio.speechiness",
                "min_value": 0,
                "max_value": 1,
                "description": """Estimates the amount of spoken word in a
                track. The more exclusively speech-like the track (e.g. talk
                show, audio book, poetry), the closer to 1.0 the attribute
                value. Values above 0.66 describe tracks that are probably made
                entirely of spoken words. Values between 0.33 and 0.66 describe
                tracks that may contain both music and speech, either in
                sections or layered, including such cases as rap music. Values
                below 0.33 most likely represent music and other non-speech-like
                tracks."""
            },
            { 
                "name" : "acousticness", 
                "value" : "audio.acousticness",
                "min_value": 0,
                "max_value": 1,
                "description": """Estimates the likelihood a recording was
                created by solely acoustic means such as voice and acoustic
                instruments as opposed to electronically such as with
                synthesized, amplified, or effected instruments. Tracks with low
                acousticness include electric guitars, distortion, synthesizers,
                auto-tuned vocals, and drum machines, whereas songs with
                orchestral instruments, acoustic guitars, unaltered voice, and
                natural drum kits will have acousticness values closer to
                1.0."""
            },
            { 
                "name" : "danceability", 
                "value" : "audio.danceability",
                "min_value": 0,
                "max_value": 1,
                "description": """Describes how suitable a track is for dancing
                using a number of musical elements (the more suitable for
                dancing, the closer to 1.0 the value). The combination of
                musical elements that best characterize danceability include
                tempo, rhythm stability, beat strength, and overall
                regularity."""
            },
            { 
                "name" : "energy", 
                "value" : "audio.energy",
                "min_value": 0,
                "max_value": 1,
                "description": """Represents a perceptual measure of intensity
                and powerful activity released throughout the track. Typical
                energetic tracks feel fast, loud, and noisy. For example, death
                metal has high energy, while a Bach prelude scores low on the
                scale. Perceptual features contributing to this attribute
                include dynamic range, perceived loudness, timbre, onset rate,
                and general entropy."""
            },
            { 
                "name" : "tempo", 
                "value" : "audio.tempo",
                "min_value": 30,
                "max_value": 300,
                "description": """The overall estimated tempo of a track in
                beats per minute (BPM). In musical terminology, tempo is the
                speed or pace of a given piece and derives directly from the
                average beat duration. """
            },
            { 
                "name" : "instrumentalness", 
                "value" : "audio.instrumentalness",
                "min_value": 0,
                "max_value": 1,
                "description": """Predicts whether a track contains no vocals.
                "Ooh" and "aah" sounds are treated as instrumental in this
                context. Rap or spoken word tracks are clearly "vocal". The
                closer the instrumentalness value is to 1.0, the greater
                likelihood the track contains no vocal content. Values above 0.5
                are intended to represent instrumental tracks, but confidence is
                higher as the value approaches 1.0."""
            },
            { 
                "name" : "key", 
                "value" : "audio.key",
                "min_value": 0,
                "max_value": 12,
                "description": """The key the track is in. Integers map to
                pitches using standard Pitch Class notation. E.g. 0 = C, 1 =
                C#, 2 = D, and so on."""
            },
            { 
                "name" : "liveness", 
                "value" : "audio.liveness",
                "min_value": 0,
                "max_value": 1,
                "description": """ Detects the presence of an audience in the
                recording. The more confident that the track is live, the closer
                to 1.0 the attribute value. A value above 0.8 provides strong
                likelihood that the track is live."""
            },
            { 
                "name" : "mode", 
                "value" : "audio.mode",
                "min_value": 0,
                "max_value": 1,
                "description": """Indicates the modality (major or minor)
                of a track, the type of scale from which its melodic content is
                derived. Major is represented by 1 and minor is 0."""
            },
            { 
                "name" : "time signature", 
                "value" : "audio.time_signature",
                "min_value": 1,
                "max_value": 10,
                "description": """Estimates of the overall time signature of a
                track. The time signature (meter) is a notational convention to
                specify how many beats are in each bar (or measure)."""
            },
            { 
                "name" : "loudness", 
                "value" : "audio.loudness",
                "min_value": -60,
                "max_value": 5, "description": """The overall loudness of a track in decibels (dB).
                Loudness values are averaged across the entire track and are
                useful for comparing relative loudness of tracks. Loudness is
                the quality of a sound that is the primary psychological
                correlate of physical strength (amplitude)."""
            },
            { 
                "name" : "valence", 
                "value" : "audio.valence",
                "min_value": 0,
                "max_value": 1,
                "description": """A measure from 0.0 to 1.0 describing the
                musical "positiveness" conveyed by a track. Tracks with high
                valence sound more positive (e.g., happy, cheerful, euphoric),
                while tracks with low valence sound more negative (e.g. sad,
                depressed, angry)."""
            },
            { 
                "name" : "duration", 
                "value" : "duration",
                "min_value": 0,
                "max_value": 10000,
                "description": "The duration of the track, in seconds"
            },
            { 
                "name" : "popularity", 
                "value" : "spotify.popularity",
                "min_value": 0,
                "max_value": 100,
                "description": """A normalized estimation of how popular the
                track is based on recent streaming."""
            },
            { 
                "name" : "track number", 
                "value" : "spotify.track_number",
                "min_value": 0,
                "max_value": 100,
                "description": """The position of the track on its album. If an 
                album has several discs, the track number is the number on the specified
                disc."""
            },
            { 
                "name" : "disc number", 
                "value" : "spotify.disc_number",
                "min_value": 1,
                "max_value": 100,
                "description": """The disc number (usually 1 unless the album
                consists of more than one disc)."""
            }
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
            { "name" : "valence", "value" : "audio.valence"},

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
            "type" : "combiner",
            "description": "Annotates tracks with external information",
            "help" : """This component will add information to the tracks on the
            input stream. This can make downstream operations like range filters
            run much faster.  Supported annotation types are <i>echonest</i>,
            <i>audio</i> and <i>spotify</i>""",
            "title" : "annotate with $type data",
            "params": {
                "source": {
                    "type" : "port",
                    "optional" : False,
                    "port": "green",
                    "max_inputs": 1,
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
            the stream.  
            If <b> By Name </b> is set, then tracks dedupped by
            artist and title, otherwise, they are dedupped based upon their
            track id""",
            "params": {
                "source": {
                    "type" : "port",
                    "optional" : False,
                    "port": "green",
                    "max_inputs": 1,
                    "description": "the source of the tracks",
                },
                "by_name": {
                    "display" : "By name",
                    "type" : "bool",
                    "optional" : True,
                    "default": False,
                    "description": " if True also match by name in addition to the regular ID match",
                },
            }
        },
        {
            "name" : "ArtistDeDup",
            "display": "artist de-dup",
            "class": plugs.ArtistDeDup,
            "type" : "filter",
            "description": "Ensure only unique artists appear in the track stream",
            "help" : """ This component will remove any tracks with duplicate
            artists from the stream. """,
            "params": {
                "source": {
                    "type" : "port",
                    "optional" : False,
                    "port": "green",
                    "max_inputs": 1,
                    "description": "the source of the tracks",
                },
            }
        },
        {
            "name" : "ArtistSeparation",
            "display": "artist separation",
            "class": plugs.ArtistSeparation,
            "type" : "filter",
            "description": "Enforces a specified separation of artists in the track stream",
            "help" : """ This component will guarantee that artists will not
            appear closer together than the given <b>minimum artist separation</b> in the
            track stream. If <b>reorder</b> is set, then tracks may be reordered
            to enforce the separation, otherwise, if <b>reorder</b> is not set,
            then offending tracks are removed from the stream.""",
            "params": {
                "source": {
                    "type" : "port",
                    "optional" : False,
                    "port": "green",
                    "max_inputs": 1,
                    "description": "the source of the tracks",
                },
                "min_separation": {
                    "type" : "number",
                    "optional" : True,
                    "default" : 4,
                    "display" : "minimum artist separation",
                    "description": "minimum number of tracks between tracks by the same artist"
                },
                "reorder": {
                    "type" : "bool",
                    "optional" : True,
                    "default" : True,
                    "display": "reorder",
                    "description": "if true, tracks may be reordered to enforce artist separation, otherwise, offending tracks are simply omitted  from the stream",
                },
            }
        },
        {
            "name" : "comment",
            "display": "comment",
            "class": plugs.Comment,
            "type" : "misc",
            "title": "$text",
            "description": "Add a comment to the program",
            "help" : """This component lets you add arbitrary comments to your
            program.  Comments have no effect on how a program will execute""",
            "max_outputs": 0,
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
            "type" : "filter",
            "description": "removes track from a stream",
            "help": """ This component takes two input streams. It produces a
            stream of tracks from the green input
            stream with the tracks on the red input stream removed.  If the 
            <b>invert</b> flag is set, the filter is inverted, that is, it will
            produce a stream of tracks that consist of the tracks on the green
            input stream with the tracks that are <b> not </b> on the red
            stream.
            If <b> By Name </b> is set, then tracks are matched by name in
            addition to the regular ID match
            """,
            "params": {
                "true_source": {
                    "type" : "port",
                    "optional" : False,
                    "port": "green",
                    "max_inputs" : 1,
                    "description": "the source of tracks",
                },
                "false_source": {
                    "type" : "port",
                    "optional" : False,
                    "port": "red",
                    "max_inputs" : 1,
                    "description": "the tracks to be removed",
                },
                "invert": {
                    "type": "bool",
                    "default": False,
                    "optional" : True,
                    "description": "if set, only tracks on both input streams will be passed through"
                },
                "by_name": {
                    "display" : "By name",
                    "type" : "bool",
                    "optional" : True,
                    "default": False,
                    "description": " if True also match by name in addition to the regular ID match",
                },
            }
        },
        {
            "name" : "ArtistFilter",
            "class": plugs.ArtistFilter,
            "display": "artist filter",
            "type" : "filter",
            "description": "removes track from a stream by artist",
            "help": """ This component takes two input streams. It produces a
            stream of tracks that consist of the tracks on the green input
            stream with the tracks by artists of the tracks on the red input
            stream removed. If the <b>invert</b> parameter is set, the sense of
            the filter is reverse, i.e. the component will produce only tracks 
            from the green stream that are by artists on the red stream """,
            "params": {
                "true_source": {
                    "type" : "port",
                    "optional" : False,
                    "port": "green",
                    "max_inputs" : 1,
                    "description": "the source of tracks",
                },
                "false_source": {
                    "type" : "port",
                    "optional" : False,
                    "port": "red",
                    "max_inputs" : 1,
                    "description": "the tracks (by artist) to be removed",
                },
                "invert": {
                    "type": "bool",
                    "default": False,
                    "optional" : True,
                    "description": "if set, only tracks by artists on the red stream will be passed through"
                },
            }
        },
        {
            "name" : "YesNo",
            "class": plugs.YesNo,
            "display": "yes or no",
            "type" : "conditional",
            "description": "selects a stream based on a boolean",

            "help": """ This component excepts a red and a green input stream.
            If the <b> yes </b> parameter is set, tracks from the green stream
            will be passed through, otherwise, tracks from the red stream will
            be passed through""",

            "params": {
                "true_source": {
                    "type" : "port",
                    "optional" : False,
                    "port": "green",
                    "max_inputs" : 1,
                    "description": "the source of tracks when yes",
                },
                "false_source": {
                    "type" : "port",
                    "optional" : False,
                    "port": "red",
                    "max_inputs" : 1,
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
            "type" : "conditional",
            "description": "selects a stream based on whether or not today is a weekend",

            "help" : """This component accepts a green and a red stream. If the
            current day is a weekend, tracks from the green stream are passed
            through, otherwise tracks from the red stream are passed
            through.""",

            "params": {
                "true_source": {
                    "type" : "port",
                    "optional" : False,
                    "port": "green",
                    "max_inputs" : 1,
                    "description": "the source of tracks when it is a weekend",
                },
                "false_source": {
                    "type" : "port",
                    "optional" : False,
                    "port": "red",
                    "max_inputs" : 1,
                    "description": "the source of tracks when it is not a weekend",
                },
            }
        },
        {
            "name" : "IsDayOfWeek",
            "class": plugs.IsDayOfWeek,
            "type" : "conditional",
            "display": "is day of week",
            "title": "is $day",
            "description": "selects a stream based on whether is is the given day of the week",

            "help" : """This component accepts a green and a red stream. If the
            current day matches the day specified, tracks from the green stream are passed
            through, otherwise tracks from the red stream are passed
            through.""",

            "params": {
                "true_source": {
                    "type" : "port",
                    "optional" : False,
                    "port": "green",
                    "max_inputs" : 1,
                    "description": "the source of tracks when the day matches",
                },
                "false_source": {
                    "type" : "port",
                    "optional" : False,
                    "port": "red",
                    "max_inputs" : 1,
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
            "display": "simple artist filter",
            "description": "removes tracks by the given artist",

            "help" : """ This component will remove tracks from the input stream
            that are by the given set of artists. Artists are specified as a
            list of comma separated name.""",

            "params": {
                "source": {
                    "type" : "port",
                    "optional" : False,
                    "port": "green",
                    "max_inputs": 1,
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
            "name" : "RelativeDatedSpotifyPlaylist",
            "class": plugs.RelativeDatedPlaylistSource,
            "type" : "source",
            "display": "playlist (rel date)",
            "description": "loads tracks from the given spotify playlist, potentially ordered and filtered by the relative track added date",

            "help" : """ This component will generate a stream of tracks from the given Spotify
            playlist.  If you specify a Spotify playlist <b>URI</b>, that playlist will
            be loaded. If you omit the URI but specify a <b>user</b> and a
            <b>name</b>, the user's public playlists will be searched for the playlist with the
            given name. If no user is specified, the most popular playlist with
            the given <b>name</b> will be used.
            <p>
            By default tracks are generated in playlist order. If <b>Order by
            date added</b> is set, tracks are returned in order of the date they
            were added to the playlist.
            <p>
            By setting relative dates <b>tracks added before</b> and/or <b> tracks added since</b>
            you can restrict tracks generated to just those that were added in
            the given period. 
            <p> Examples of relative dates: 
            <ul>
                <li> 5 days
                <li> 1 year, 2 months and 3 days
                <li> last week
                <li> two weeks ago
            </ul> 
            More examples can be found on the <a href="about.html"> about
            page</a>
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
                "order_by_date_added": {
                    "type" : "bool",
                    "optional" : True,
                    "default" : False,
                    "display": "Order by date added",
                    "description": "if true, tracks are ordered by the date added to the playlist",
                },
                "tracks_added_since": {
                    "type" : "string",
                    "display": "Include only tracks added since",
                    "optional" : True,
                    "default" : "",
                    "description": "If set, only tracks added since this relative date are generated",
                },
                "tracks_added_before": {
                    "type" : "string",
                    "display": "Include only tracks added before",
                    "optional" : True,
                    "default" : "",
                    "description": "If set, only tracks added before this relative date are generated",
                },
            }
        },
        {
            "name" : "DatedSpotifyPlaylist",
            "class": plugs.DatedPlaylistSource,
            "type" : "source",
            "display": "playlist (abs date)",
            "description": "loads tracks from the given spotify playlist, potentially ordered and filtered by the absolute track added date",

            "help" : """ This component will generate a stream of tracks from the given Spotify
            playlist.  If you specify a Spotify playlist <b>URI</b>, that playlist will
            be loaded. If you omit the URI but specify a <b>user</b> and a
            <b>name</b>, the user's public playlists will be searched for the playlist with the
            given name. If no user is specified, the most popular playlist with
            the given <b>name</b> will be used.
            <p>
            By default tracks are generated in playlist order. If <b>Order by
            date added</b> is set, tracks are returned in order of the date they
            were added to the playlist.
            <p>
            By setting <b>tracks added before</b> and/or <b> tracks added since</b>
            you can restrict tracks generated to just those that were added in
            the given period. 
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
                "order_by_date_added": {
                    "type" : "bool",
                    "optional" : True,
                    "default" : False,
                    "display": "Order by date added",
                    "description": "if true, tracks are ordered by the date added to the playlist",
                },
                "tracks_added_since": {
                    "type" : "optional_date",
                    "display": "Include only tracks added since",
                    "optional" : True,
                    "default" : -1,
                    "description": "If set, only tracks added since this date are generated",
                },
                "tracks_added_before": {
                    "type" : "optional_date",
                    "display": "Include only tracks added before",
                    "optional" : True,
                    "default" : -1,
                    "description": "If set, only tracks added before this date are generated",
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
            current user's saved albums.
            <br>
            <span class="label label-warning"> Warning </span> This component may fail if you have a large number
            of saved albums.  Someday, this will be fixed.
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
            <br>
            <span class="label label-warning"> Warning </span> This component may fail if you have a large number
            of saved tracks.  Someday, this will be fixed.
            """,
            "title": "My Saved tracks",
            "params": { }
        },
        {
            "name" : "MyTopTracks",
            "class": plugs.MyTopTracks,
            "type" : "source",
            "display": "my top tracks",
            "description": "produces a list of the current user's recent top tracks",

            "help" : """ This component will generate a stream of your
            most listened to tracks from your listening history.  
            The top tracks are available over three time spans: 
            <ul>
                <li><b>short term</b> - the last month or so </li>
                <li><b>medium term</b> - the last half year or so </li>
                <li><b>long term</b> - the last several years </li>
            </ul>
            """,
            "title": "My $time_range Top tracks",
            "params": { 
                "time_range" : {
                    "type": "time_range",
                    "optional": True,
                    "default": "medium_term",
                    "description": "the time period of interest",
                    "display": "time range"
                }
            }
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
            "type" : "selector",
            "title" : "first $sample_size",
            "display": "first",
            "description": "Returns the first tracks from a stream",

            "help": """ This filter will only pass through the first <b> count
            </b> tracks through. Use this filter to limit the tracks to just the
            first <b>count</b> tracks""",

            "params": {
                "source": {
                    "type" : "port",
                    "optional" : False,
                    "port": "green",
                    "max_inputs": 1,
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
            "type" : "misc",
            "title" : "save to $playlist_name",
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
                    "type" : "port",
                    "optional" : False,
                    "port": "green",
                    "max_inputs": 1,
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
                    "optional" : True,
                    "description": "if true, append tracks to the playlist"
                }
            }
        },

        {
            "name" : "PlaylistSaveToNew",
            "class": plugs.PlaylistSaveToNew,
            "type" : "misc",
            "title" : "save to new playlist",
            "display": "save to new playlist",
            "description": "save the tracks to a new Spotify playlist with an optional automatically supplied suffix",

            "help": """ This filter will save all the tracks that pass through
            it to the Spotify playlist. A new playlist will always be created.
            Specify a suffix type to automatically vary the playlist name with
            the date, time, day of the week, or the day of the month. """,

            "params": {
                "source": {
                    "type" : "port",
                    "optional" : False,
                    "port": "green",
                    "max_inputs": 1,
                    "description": "the source of the tracks",
                },
                "playlist_name": {
                    "display": "name",
                    "type" : "string",
                    "default" : "My Smarter Playlist",
                    "optional" : True,
                    "description": "the name of the playlist"
                },
                "suffix_type": {
                    "display": "suffix_type",
                    "type" : "playlist_suffix",
                    "default" : "time",
                    "optional" : True,
                    "description": "type of suffix automatically applied to the playlist name"
                },
            }
        },

        {
            "name" : "AllButTheFirst",
            "class": plugs.AllButTheFirst,
            "type" : "selector",
            "title" : "all but the first $sample_size",
            "display": "all but the first",
            "description": "Returns all but the first tracks from a stream",

            "help": """ This filter will only pass through all but the first <b> count
            </b> tracks through. Use this filter to limit the tracks to all but the
            first <b>count</b> tracks""",

            "params": {
                "source": {
                    "type" : "port",
                    "optional" : False,
                    "port": "green",
                    "max_inputs": 1,
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
            "type" : "selector",
            "title" : "all but the last $sample_size",
            "display": "all but the last",
            "description": "Returns all but the last tracks from a stream",

            "help": """ This filter will only pass through all but the last <b> count
            </b> tracks through. Use this filter to limit the tracks to all but the
            last <b>count</b> tracks""",

            "params": {
                "source": {
                    "type" : "port",
                    "optional" : False,
                    "port": "green",
                    "max_inputs": 1,
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
            "type" : "selector",
            "title" : "last $sample_size",
            "display" : "last",
            "description": "Returns the last tracks from a stream",

            "help" : """ This component returns the last <b> count </b> number of
            tracks on the input stream""",

            "params": {
                "source": {
                    "type" : "port",
                    "optional" : False,
                    "port": "green",
                    "max_inputs": 1,
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
            "type" : "selector",
            "display" : "sample",
            "title" : "sample $sample_size tracks",
            "description": "randomly sample tracks from the stream",

            "help" : """ This component will randomly sample up to <b> count </b>
            tracks from the input stream. Sampled tracks may be returned in any
            order""",

            "params": {
                "source": {
                    "type" : "port",
                    "optional" : False,
                    "port": "green",
                    "max_inputs": 1,
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
            "type" : "selector",
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
                    "type" : "port",
                    "optional" : False,
                    "port": "green",
                    "max_inputs": 1,
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
            "type" : "selector",
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
                    "type" : "port",
                    "optional" : False,
                    "port": "green",
                    "max_inputs": 1,
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
            "type" : "order",
            "title" : "shuffle",
            "display" : "shuffle",
            "description": "Shuffles the tracks in the stream",

            "help" : """
                This component will randomly re-order the input tracks """,

            "params": {
                "source": {
                    "type" : "port",
                    "optional" : False,
                    "port": "green",
                    "max_inputs": 1,
                    "description": "the source of the tracks",
                },
            }
        },
        {
            "name" : "Weighted Shuffler",
            "class": plugs.WeightedShuffler,
            "type" : "order",
            "title" : "Weighted shuffle",
            "display" : "Weighted shuffle",
            "description": "performs a weighted shuffle of  the tracks in the stream",

            "help" : """
                This component will randomly re-order the input tracks. The
                amount of re-ordering is controlled by an 
                <b>amount of randomness</b> factor. This factor
                is a number between zero and one. The closer the factor is to
                one, the more random the resulting track order, while the closer
                the factor is to zero, the more the original track order is
                retained.  A factor of .1 will lightly shuffle the input tracks""",
            "params": {
                "source": {
                    "type" : "port",
                    "optional" : False,
                    "port": "green",
                    "max_inputs": 1,
                    "description": "the source of the tracks",
                },
                "factor": {
                    "display" : "amount of randomness",
                    "type" : "number",
                    "optional" : False,
                    "default": .1,
                    "description": "controls the amount of randomness used in shuffling the tracks"
                },
            }
        },
        {
            "name" : "SeparateArtists",
            "class": plugs.SeparateArtists,
            "type" : "order",
            "title" : "separate artists",
            "display" : "separate artists",
            "description": "minimizes the number of adjacent songs by the same artist",

            "help" : """
                This component will re-order the input tracks such that the
                number of adjacent tracks with the same artist is minimized""",

            "params": {
                "source": {
                    "type" : "port",
                    "optional" : False,
                    "port": "green",
                    "max_inputs": 1,
                    "description": "the source of the tracks",
                },
            }
        },
        {
            "name" : "MixIn",
            "class": plugs.MixIn,
            "display" : "mix in",
            "title": "mix in",
            "type" : "combiner",
            "description": "mix two input streams",

            "help": """ This component allows for more sophisticatd mixing of two
            streams. Tracks are alternately selected from the red and the green
            streams based upon the settings """,

            "params": {
                "true_source": {
                    "type" : "port",
                    "optional" : False,
                    "port": "green",
                    "max_inputs" : 1,
                    "description": "the primary source of tracks ",
                },
                "false_source": {
                    "type" : "port",
                    "optional" : False,
                    "port": "red",
                    "max_inputs" : 1,
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
            "type" : "order",
            "title" : "reverse",
            "display" : "reverse",
            "description": "Reverses the order of the tracks in the stream",

            "help" : """ This component will reverse the order of the input tracks """,

            "params": {
                "source": {
                    "type" : "port",
                    "optional" : False,
                    "port": "green",
                    "max_inputs": 1,
                    "description": "the source of the tracks",
                },
            }
        },
        {
            "name" : "Sorter",
            "class": pbl.Sorter,
            "type" : "order",
            "title": "sort by $reverse $attr",
            "display" : "sort",
            "description": "Sorts the tracks in the stream by the given attribute",

            "help" : """ This component will order the tracks based upon the
            given attribute. The sort can be reversed by selected the <b>
            reverse </b> option.""",

            "params": {
                "source": {
                    "type" : "port",
                    "optional" : False,
                    "port": "green",
                    "max_inputs": 1,
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
            "type" : "combiner",
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
                    "type" : "port",
                    "port": "green",
                    "max_inputs": "20",
                    "description": "the list of sources"
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
            "type" : "combiner",
            "display" : "random",
            "description": "randomly selects tracks from multiple streams",

            "help" : """This component takes any number of input streams and
            produces tracks by continuosly selecting a random input stream and
            returning the next track from that stream. If <b> fail fast </b> is
            set, this component will stop generating tracks as soon as any of
            its randomly selected sources stops generating tracks.""",

            "params": {
                "source_list": {
                    "type" : "port",
                    "port": "green",
                    "max_inputs": "20",
                    "description": "the list of sources"
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

            "type" : "combiner",
            "display" : "random stream",
            "description": "randomly selects a stream",
            "params": {
                "source_list": {
                    "type" : "port",
                    "port": "green",
                    "max_inputs": "20",
                    "description": "the list of sources"
                },
            }
        },
        {
            "name" : "Concatenate",
            "class": pbl.Concatenate,
            "display" : "concatenate",
            "type" : "combiner",
            "description": "Concatenate tracks from multiple streams",

            "help" : """ This component takes any number of input streams and
            produces tracks by retrieving all the tracks from the first stream,
            followed by all the tracks from the second stream and so on.""",

            "params": {
                "source_list": {
                    "type" : "port",
                    "port": "green",
                    "max_inputs": "20",
                    "description": "the list of sources"
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
                    "type" : "port",
                    "optional" : False,
                    "port": "green",
                    "max_inputs": 1,
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
            "name" : "ReleaseDateFilter",
            "class": plugs.ReleaseDateFilter,
            "type" : "filter",
            "description": "filter tracks by the date of release",
            "title": "released between $min_val and $max_val",
            "display" : "date filter",

            "help" : """ This component will filter the input stream and only
            pass through tracks that have a release date within the specified
            range""",

            "params": {
                "source": {
                    "type" : "port",
                    "optional" : False,
                    "port": "green",
                    "max_inputs": 1,
                    "description": "the source of the tracks",
                },
                "min_val": {
                    "type" : "string",
                    "optional" : True,
                    "display" : "Earliest Date",
                    "default" : "1935-01-08",
                    "description": "tracks must be released no earlier than this date"
                },
                "max_val": {
                    "type" : "string",
                    "optional" : True,
                    "display" : "Latest date",
                    "default" : datetime.datetime.now().strftime("%Y-%m-%d"),
                    "description": "tracks must be released no later than this date"
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
                    "type" : "port",
                    "optional" : False,
                    "port": "green",
                    "max_inputs": 1,
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
                    "type" : "port",
                    "optional" : False,
                    "port": "green",
                    "max_inputs": 1,
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
            "title" : "$!!explicit",
            "display": "explicit",
            "description": "filters tracks by their explicit attribute",

            "help" : """ This component will pass through tracks that match
            the given explicit criteria.""",

            "params": {
                "source": {
                    "type" : "port",
                    "optional" : False,
                    "port": "green",
                    "max_inputs": 1,
                    "description": "the source of the tracks",
                },
                "explicit": {
                    "type" : "bool",
                    "default" : False,
                    "optional" : True,
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
                    "type" : "port",
                    "optional" : False,
                    "port": "green",
                    "max_inputs": 1,
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
            "name" : "TextFilter",
            "class": plugs.TextFilter,
            "type" : "filter",
            "title" : "title $?invert:not-matching:matching  $text",
            "display": "title filter",
            "description": "filters tracks with titles that match a given string",

            "help" : """ This component will pass through tracks that have
            a title that matches the given text string.  The sense of the filter
            can be inverted by settting the <b>invert</b> parameter. To ignore
            case when matching set the  <b>ignore case</b> flag.  Note that
            the matching text is a <a
            href="http://www.regular-expressions.info">regular expression</a>
            allowing for very sophisticated matching logic.""",

            "params": {
                "source": {
                    "type" : "port",
                    "optional" : False,
                    "port": "green",
                    "max_inputs": 1,
                    "description": "the source of the tracks",
                },
                "text": {
                    "type" : "string",
                    "optional" : False,
                    "display": "match",
                    "default" : "",
                    "description": "regular expression to match track title"
                },
                "ignore_case": {
                    "type" : "bool",
                    "optional" : False,
                    "display": "ignore case",
                    "default" : True,
                    "description": "if true, matches ignore letter case"
                },
                "invert": {
                    "type" : "bool",
                    "optional" : False,
                    "default" : False,
                    "description": "if true, the filter is reversed"
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
                    "type" : "port",
                    "optional" : False,
                    "port": "green",
                    "max_inputs": 1,
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
                    "type" : "port",
                    "optional" : False,
                    "port": "green",
                    "max_inputs": 1,
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
        {
            "name" : "Mixer",
            "display": "mixer",
            "class": mixer.Mixer,
            "type" : "combiner",
            "description": "Mixes input tracks while maintaining a set of rules.",
            "help" : """ This component will mix tracks from the various input
            streams, while maintaining a set of rules that govern how the tracks
            will be ordered.
            <br>
            Input streams are on the <b> green </b> port, banned tracks
            are on the <b> red</b> port and banned artists are on 
            the <b> orange </b> port.  If <b> fail fast </b> is set, then the
            order of the input tracks is guaranteed to be preserved and the
            mixer will stop producing tracks when it is no longer able to
            guarantee the contraints.  If <b> fail fast </b> is not set, then
            the mixer will find the next best track on the next input stream
            that best fits the current constraints and will continue to produce
            tracks as long as any stream is producing tracks.
            """,

            "title" : "mixer",
            "params": {
                "source_list": {
                    "type" : "port",
                    "port": "green",
                    "max_inputs": "20",
                    "description": "the list of sources"
                },
                "bad_track_source_list": {
                    "type" : "port",
                    "port":  "red",
                    "max_inputs": "20",
                    "display" : "bad tracks",
                    "description": "tracks that should be removed from the output"
                },
                "bad_artist_source_list": {
                    "type" : "port",
                    "port":  "orange",
                    "max_inputs": "20",
                    "display" : "bad artists",
                    "description": "artists from this source are removed from the output"
                },
                "fail_fast": {
                    "type" : "bool",
                    "optional" : True,
                    "default" : True,
                    "display" : "fail fast",
                    "description": "if true stop producing tracks "
                        + "as soon as any input stops producing tracks"
                },
                "dedup": {
                    "type" : "bool",
                    "optional" : True,
                    "default" : True,
                    "display" : "de-dup",
                    "description": "if true don't allow duplicate tracks in the output"
                },
                "min_artist_separation": {
                    "type" : "number",
                    "optional" : True,
                    "default" : 4,
                    "display" : "minimum artist separation",
                    "description": "minimum number of tracks between tracks by the same artist"
                },
                "max_tracks": {
                    "type" : "number",
                    "optional" : True,
                    "default" : 50,
                    "display" : "maximum tracks",
                    "description": "the maximum number of tracks to produce"
                },
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
    if genres_enabled:
        response = en.get('genre/list', results=2000)
        gstyle = []
        for g in response['genres']:
            gn = g['name']
            gstyle.append( { 'name': gn, 'value': gn} )
        return gstyle
    else:
        return []

def check_components():
    for comp in inventory["components"]:
        check_component(comp)

def is_valid_param_type(type):
    valid_types = set(['number', 'string', 'port', 'bool', 
    'uri', 'uri_list', 'string_list', 'time', 'any', 'optional_date', 
    'optional_rel_date'])
    if type in valid_types:
        return True
    if type in inventory['types']:
        return True

    print "invalid type", type
    return False

def check_component(comp):
    print "checking", comp["name"]
    '''
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
                    "type" : "port",
                    "optional" : False,
                    "port": "green",
                    "max_inputs": 1,
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
    '''
    valid_ports = set(['green', 'red', 'orange', 'blue'])
    assert "name" in comp
    assert "class" in comp
    assert "type" in comp
    assert "description" in comp
    if "params" in comp:
        for name, param in comp["params"].items():
            assert "description" in param
            assert "type" in param
            ptype = param['type']
            assert ptype != "source" # archaic
            assert ptype != "source_list" # archaic
            if ptype == "port":
                assert "port" in param
                assert param['port'] in valid_ports
            if ptype != "port":
                assert "optional" in param
                # assert "default" in param
            assert is_valid_param_type(ptype)

    

exported_inventory = export_inventory()
check_components()

if __name__ == '__main__':
    #import json
    #get_genres()
    #print json.dumps(exported_inventory, indent=4)
    print ""
