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

        "yn" : {
            "_type": "YesNo",
            "true_source" : "yfc",
            "false_source" : "tp",
            "yes" : false
        }
    },
    "main": "yn"
}
