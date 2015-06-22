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

        "filter": {
            "_type":"AttributeRangeFilter",
            "attr": "echonest.energy",
            "max_val" : 0.5,
            "source": "alt"
        },

        "sorter": {
            "_type":"Sorter",
            "attr": "echonest.loudness",
            "source": "filter"
        }
    },
    "main": "sorter"
}
