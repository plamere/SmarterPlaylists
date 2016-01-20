TODOs before release
====================
* add kitchen sink tests
* mixer example
* blog post
  - new mixer component
  - internal refactoring

More TODOs
==========
* select tracks from a playlist by a date range
* change the API key
* Admin page
* UI for reordering inputs for multi-input ports
* Add a artist follow sampler
* general stats page
* add mechanism for sending notices
* scaling of raphael area is not great,
* better date UI for components that take dates
* Add range info and range checking for numeric params
* Get names for things like playlists that are specified by uri
* add reverse artist filter (only allow tracks by artists that match the filter)

User Suggestions
================

Testing
========
New user that fails to give permission gets proper page.

Bugs
=====
* don't allow scheduling in the past
* remove deleted programs that are shared from the import list
* track source doesn't work when a track appears on multiple sources
* artist tracks returns too few tracks (EN playlist problem, move to spotify API)


Later on
==========
* add date ranges for my saved tracks/albums - this will allow for components that get mysaved tracks for the last year.
* Add text when there are no programs

Fixed
======
* can't set schedule to never

Done
====
* DB restore test
* track uris needs a strip
* Add more refined categories, sources, filters, combiners, conditionals
* figure out how to display 'explicit vs not explicit'
* add buttons to connect components and to delete components/edges
* remove debugging output
* delete a component prompt?
* maintenance mode
