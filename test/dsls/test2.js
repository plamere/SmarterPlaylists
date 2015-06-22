
{
    "components": {
        "yfc" : { 
            "_type": "SpotifyPlaylist",
            "name" : "Your Favorite Coffeehouse"
        },

        "tp" : { 
            "_type": "SpotifyPlaylist",
            "name" : "Teen Party"
        },

        "alt" : {
            "_type": "Alternate",
            "source_list" : ["yfc", "tp"]
        },

        "AddEchonestData": {
            "_type":"Annotator",
            "type": "echonest",
            "source": "alt"
        },

        "filter": {
            "_type":"AttributeRangeFilter",
            "attr": "echonest.energy",
            "min_val" : 0.5,
            "source": "AddEchonestData"
        },

        "sorter": {
            "_type":"Sorter",
            "attr": "echonest.loudness",
            "source": "filter"
        }
    },
    "main": "sorter"
}
