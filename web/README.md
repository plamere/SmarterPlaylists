To DOs
=======
  * Server site stats
  * Components that take URIs should also take URLs and provide better diagnostics for malformed addresses
  * get audio attributes from audio features api
  * get album attributes to get 


Auth Issues
============
Auth .... to use the app you will need to login, but his makes it hard to share
examples if there's a login page in between the share, that will be a challenge.
One approach would be to allow non-auth users to get to the examples page. If
they 'run' a program that requires auth, they will get an error and they will be
prompted to login.  Login button should be in the upper right of the app. (or
conversly, make sure people are logged in

Save should take place on the server side (to avoid needing two kinds of auth
for the user).  when they go to 'run' a program.

variables
=========
    we support a small set of variables. These are substituted at run time on
    the server

  * $my\_id - the current user
  * $my\_name - the current user
  * $date - the current date
  * $day - the day of the week
  * $hour - the our of the day
  * $daypart - morning, afternoon, evening, night

typical us would be a script that has a 'playlist' component with a 'My banned
artists' - the user could be $me.

personalized components

   * save playlist - saves tracks to playlist. Takes a name or a uri, saves
   * my saved tracks - generates the list of saved tracks

schedule program:

    need to start a scheduled update
    need to stop a scheduled update
    see your scheduled programs
    see status of latest run (time run, number of tracks generated, any errors)


user management:
    - s


More components
================
  * server side save
  * followed artists
  * track radio
  * light shuffle
  * artist separation
  * genre filter
  * advanced echo nest playlist
  * dedup-artists - playlist but with only one song per artist


Bugs
=====
  * track uris needs a strip


Later
=====
  * internal doc
  * Philosophy bits - to deal with user specific APIs we will can use the
    authorization code flow.
  * better github README
  * Add a technical bits section

  * Add initial login - get user info (TZ, username)
  * Add subprogram support
  * add smart reordering:
    - artist separation

  * add city components


  * add some targeted filters
    (explicit, length, release date)
  * Reorganize component menu so most common components are visible and the rest
    are in Deep Cuts
  * Loading an example takes longer than expected. Why? - compile js


Big Stuff
==========
  * Figure out onboarding
    * help for editing and connecting
  * Better way to connect components?
    * prompt
    * connect button? Delete button?
    * do we ever need a delete connection control?
    * smart connect - figures out source and dest based on:
        * current connections
        * position on the screen
  * Directory
      * bulk delete
      * run from directory?
      * bulk select?


Future
======
  * Allow for nesting of programs
  * Refactor type system
  * constrain connections based on in to top left and out to bottom right
  * Add 'match' filter?
  * remove maxInputs and maxOutputs from program json

Done
====
  * don't color non-bool sources as red
  * save when leaving builder page too (actually when RUN)
  * show status (checking, running, error)
  * support help in components
  * improve component ID for creation errors
  * change 'random' to pick one stream at random
  * improve track component (by artist, title) or URI
  * Add arbitratry text to a program ? - comments
  * add 30 second plays to track list
  * Save doesn't save the head
  * hiting return in the modal does bad thins
  * comment border?
  * add time support
  * add time support for types
  * 40 track pull? - increased to 200,
  * enery
  * danceable
  * tempo
  * attribute help range filters?
  * attribute help for sort
  * extract active components so we only error check ones that will run
  * Empty track list should be prettier
  * add clear all button? (shift-delete)
  * add help to all components
  * review/test default params for all components
  * Allow links to single program examples
  * Support saving to json
  * fix 'cannot read proper cls of null' that occurs after deleting
    editor 560, 553 (phew, needed to remove stale event handlers)
  * Create initial landing page
  * Document:
    - how to add components
    - how to connect components
    - how to create a program
    - how to run a program
    - how to save a playlist to spotify
  * Add help / about
  * Add some sample programs
  * W3C Validator
  * Properly support isLocal for playlist saving and logging in
  * Get built-in examples to fit the screen
  * FAQ - How do I delete a component?
  * de-logger
  * Move video to 'about'?
  * Add landing image
  * deploy strategy
  * Is the default font too big?
  * Add a what's coming section
  * make a kitchen sink test app
  * final review/test default params for all components
  * Fix weekend component
  * blog post
  * google analytics
  * Move server cache to bigger disk
  * Sharing / publishing
  * Add explicit Save button to editor
  * Add clear button to editor
  * Scaling rapheal
  * Download program link is unreliable
