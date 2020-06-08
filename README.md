# WDWWaits

This is a script that records wait time data for attractions and entertainments in Walt Disney World and Disneyland. It uses [MouseTools](https://github.com/scaratozzolo/MouseTools), my Python wrapper for Disney's API.

Stores the data in an sqlite3 database. For attractions and entertainments the database holds the id, name, wait time, destination, park, land, entertainment venue, status. It also holds the park hours for each day and the weather in Orlando and Anaheim each time the wait times are pulled.
