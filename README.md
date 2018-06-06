# WDWWaits

This is a script that records wait time data for attractions in Walt Disney World and Disneyland. It uses [MouseTools](https://github.com/scaratozzolo/MouseTools), my Python wrapper for Disney's API.

I couldn't find any wait time data so I decided to make my own.

The goal is to create a large data set to perform future analysis on. The data set currently holds the ride, the internal ride ID, location of the ride, the park it's in, and the wait times at a given time. It also saves the current weather in Orlando and Anaheim incase it would be useful in the future.

It saves the data into daily json files, sorted by ride and by location.
