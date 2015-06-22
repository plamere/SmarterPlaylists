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

        "fun_workout" : { 
            "_type": "SpotifyPlaylist",
            "name" : "Fun Workout"
        },

        "viral_hits" : { 
            "_type": "SpotifyPlaylist",
            "name" : "Viral Hits"
        },

        "confidence_boost" : { 
            "_type": "SpotifyPlaylist",
            "name" : "Confidence Boost"
        },

        "indie_mix" : { 
            "_type": "SpotifyPlaylist",
            "name" : "The Indie Mix"
        },

        "mellow_beats" : { 
            "_type": "SpotifyPlaylist",
            "name" : "Mellow Beats"
        },

        "deep_focus" : { 
            "_type": "SpotifyPlaylist",
            "name" : "Deep Focus"
        },

        "productive_morning" : { 
            "_type": "SpotifyPlaylist",
            "name" : "Productive Morning"
        },

        "alt" : {
            "_type": "Alternate",
            "source_list" : ["yfc", "tp", "productive_morning", 
                "confidence_boost", "fun_workout", "deep_focus",
                "mellow_beats", "indie_mix" ]
        },

        "alt-en": {
            "_type":"Annotator",
            "type": "echonest",
            "source": "alt"
        },

        "sorter": {
            "_type":"Sorter",
            "attr": "duration",
            "source": "alt"
        },

        "shuffler": {
            "_type":"Shuffler",
            "source": "alt-en"
        }

    },
    "main": "shuffler",
    "max_tracks": 1000
}
