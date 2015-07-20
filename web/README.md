NEED Before Ship:
=================
  * fix 'cannot read proper cls of null' that occurs after deleting
    editor 560, 553
  * Add some sample programs
  * review/test default params for all components
  * add help to all components
  * Add help / about


Later
=====

  * add smart reordering:
    - artist separation

  * add clear all button?

  * add some targeted filters 
    (tempo, explicit, length, release date)
  * Reorganize component menu so most common components are visible and the rest
    are in Deep Cuts
  * Empty track list should be prettier
  * Add 'match' filter?


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
  * Add help / about
  * Directory
      * bulk delete
      * run from directory?
      * bulk select?
  * deploy strategy


Future
======
  * extract components so we only error check ones that will run
  * Allow for nesting of programs
  * Refactor type system
  * constrain connections based on in to top left and out to bottom right

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
  * attribute help range filters?
  * attribute help for sort 
