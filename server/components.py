import pbl
import copy

exported_inventory = None

inventory = {
    "components" : [
        {
            "name" : "Annotator",
            "class": pbl.Annotator,
            "type" : "source",
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
            "name" : "SpotifyPlaylist",
            "class": pbl.PlaylistSource,
            "type" : "source",
            "description": "loads tracks from the given spotify playlist",
            "params": {
                "name": {
                    "type" : "string",
                    "optional" : False,
                    "description": "the name of the playlist",
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
            "name" : "Shuffler",
            "class": pbl.Shuffler,
            "type" : "filter",
            "description": "Shuffles the tracks in the stream",
            "params": {
                "source": {
                    "type" : "source",
                    "optional" : False,
                    "description": "the source of the tracks",
                },
                "max_size": {
                    "type" : "string",
                    "optional" : True,
                    "description": "maximum tracks to shuffle"
                }
            }
        },
        {
            "name" : "Sorter",
            "class": pbl.Sorter,
            "type" : "filter",
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
            "name" : "AttributeRangeFilter",
            "class": pbl.AttributeRangeFilter,
            "type" : "multi-in-filter",
            "description": "filter tracks by an attribute",
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
    

