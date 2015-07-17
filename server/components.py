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
         ]
    },
    "components" : [
        {
            "name" : "Annotator",
            "display": "annotate",
            "class": pbl.Annotator,
            "type" : "filter",
            "description": "annotates tracks with external information",
            "params": {
                "source": {
                    "type" : "source",
                    "optional" : False,
                    "description": "the source of the tracks",
                },
                "type": {
                    "type" : "string",
                    "optional" : False,
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
            "params": {
                "source": {
                    "type" : "source",
                    "optional" : False,
                    "description": "the source of the tracks",
                },
                "by_name": {
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
            "title" : "first $sample_size",
            "display" : "last",
            "description": "Returns the last tracks from a stream",
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
                    "type" : "number",
                    "stype" : "time",
                    "optional" : False,
                    "description": "the length in seconds of the stream of tracks"
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
                    "type" : "number",
                    "stype" : "time",
                    "optional" : False,
                    "placeholder" : "00:00:00",
                    "format" : "time",
                    "description": "the length in seconds of the stream of tracks"
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
            "params": {
                "source": {
                    "type" : "source",
                    "optional" : False,
                    "description": "the source of the tracks",
                },
                "attr": {
                    "type" : "string",
                    "optional" : False,
                    "description": "the attribute to be sorted on"
                },

                "reverse": {
                    "type" : "bool",
                    "optional" : True,
                    "description": "if true, reverse the sort"
                },

                "max_size": {
                    "type" : "number",
                    "optional" : True,
                    "description": "the maximum number of tracks to sort"
                }
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
                    "type" : "string",
                    "optional" : False,
                    "description": "the attribute to be sorted on"
                },

                "match": {
                    "type" : "any",
                    "optional" : True,
                    "description": "if not null, attribute must match this exactly"
                },

                "min_val": {
                    "type" : "number",
                    "optional" : True,
                    "description": "if not null attribute value must be at least this"
                },
                "max_val": {
                    "type" : "number",
                    "optional" : True,
                    "description": "if not null attribute value must be less than this"
                }
            }
        }
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
    

