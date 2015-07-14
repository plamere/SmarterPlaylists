{
    "components": {
        "elscorcho" : { 
            "_type": "TrackSource",
            "uris" : [
                "spotify:track:3g2gQMeeQAEPztiQKMlGSl",
                "spotify:track:4rzEjTzcG4sP28IUnRwlex",
                "spotify:track:2PVZpYPQCAWuShzGadZYp7",
                "spotify:track:42hDrA9GTkuvpxjLtAshct",
                "spotify:track:3g2gQMeeQAEPztiQKMlGSl",
                "spotify:track:3g2gQMeeQAEPztiQKMlGSl",
                "spotify:track:42hDrA9GTkuvpxjLtAshct"
            ]
        },
        "dedup" : { 
            "_type": "DeDup",
            "source": "elscorcho",
            "by_name" : true
        }
    },

    "main": "dedup"
}
