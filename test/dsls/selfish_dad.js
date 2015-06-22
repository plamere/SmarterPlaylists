{
    "components": {
        "jazz" : { 
            "_type": "SpotifyPlaylist",
            "name" : "Jazz Classics"
        },

        "teen" : { 
            "_type": "SpotifyPlaylist",
            "name" : "Teen Party"
        },

        "sorted_teen" : {
            "_type": "Sorter",
            "source" : "teen",
            "attr": "duration"
        },

        "sorted_jazz" : {
            "_type": "Sorter",
            "source" : "jazz",
            "attr": "duration",
            "reverse": true
        },

        "first_jazz" : {
            "_type": "First",
            "source" : "sorted_jazz",
            "sample_size": 10
        },

        "first_teen" : {
            "_type": "First",
            "source" : "sorted_teen",
            "sample_size": 10
        },
        "main" : {
            "_type": "Alternate",
            "source_list" : ["first_jazz", "first_teen"]
        }
    },
    "main": "main"
}
