import pbl
import copy

exported_inventory = None

inventory = {
    "components" : [
        {
            "name" : "Annotator",
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
            "name" : "AlbumSource",
            "class": pbl.AlbumSource,
            "type" : "source",
            "description": "generates a series of tracks given an album",
            "params": {
                "title": {
                    "type" : "string",
                    "optional" : True,
                    "description": "the title of the artist",
                },
                "artist": {
                    "type" : "string",
                    "optional" : True,
                    "description": "the name of the artist",
                },
                "uri": {
                    "type" : "uri",
                    "optional" : False,
                    "description": "the uri of the artist",
                },
            }
        },
        {
            "name" : "TrackSource",
            "class": pbl.TrackSource,
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
            "name" : "ArtistFilter",
            "class": pbl.ArtistFilter,
            "type" : "filter",
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
            "description": "generates a series of tracks in the given genre",
            "title" : "$genre",
            "params": {
                "genre": {
                    "type" : "string",
                    "optional" : False,
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
            "name" : "SpotifyPlaylist",
            "class": pbl.PlaylistSource,
            "type" : "source",
            "description": "loads tracks from the given spotify playlist",
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
            }
        },
        {
            "name" : "First",
            "class": pbl.First,
            "type" : "filter",
            "title" : "first $sample_size",
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
            "title" : "shorter than $time",
            "description": "Limit the stream, if possible, to tracks with a" + \
                "duration that is longer than the given time",
            "params": {
                "source": {
                    "type" : "source",
                    "optional" : False,
                    "description": "the source of the tracks",
                },
                "time": {
                    "type" : "number",
                    "optional" : False,
                    "description": "the length in seconds of the stream of tracks"
                }
            }
        },
        {
            "name" : "LongerThan",
            "class": pbl.LongerThan,
            "type" : "filter",
            "title" : "longer than $time",
            "description": "Limit the stream, if possible, to tracks with a" + \
                "duration that is longer than the given time",
            "params": {
                "source": {
                    "type" : "source",
                    "optional" : False,
                    "description": "the source of the tracks",
                },
                "time": {
                    "type" : "number",
                    "optional" : False,
                    "description": "the length in seconds of the stream of tracks"
                }
            }
        },
        {
            "name" : "Shuffler",
            "class": pbl.Shuffler,
            "type" : "filter",
            "title" : "shuffle",
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
            "description": "alternate tracks from multiple streams",
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
    inv = copy.deepcopy(inventory)
    for component in inv['components']:
        del component['class']
    return inv

exported_inventory = export_inventory()
    

