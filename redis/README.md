There are two instances of redis used in the SmarterPlaylist. The primary
instance (at port 6379), maintains the user data and the schedule.  The second
instance (at port 6380), is the track/artist/album cache. 

start both redis instances with:

   ./start-redis

stop both redis instances with:

    ./stop-redis


get info with 

    ./redis-info
    ./redish-cache-info

