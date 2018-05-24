import sys
sys.path.insert(0, "MouseTools")

from MouseTools.auth import getHeaders
from MouseTools.destinations import Destination
from MouseTools.parks import Park
from MouseTools.attractions import Attraction
from MouseTools.entertainments import Entertainment
import requests
import time
from datetime import datetime, timedelta
import json
import os
from tqdm import tqdm

destinations = {"Walt Disney World Resort" : "80007798", "Disneyland Resort" : "80008297"}

if not os.path.exists('checkpoints'):               #checks for checkpoints directory and creates it
    os.makedirs('checkpoints')
    os.makedirs('checkpoints/ridedata')
    os.makedirs('checkpoints/bylocation')

if os.path.exists('checkpoints'):                   #checks for ride_data.json and loads it to ride_data as a dictionary if it exists
    file_list = os.listdir('checkpoints/ridedata')
    if len(file_list) != 0:
        with open('checkpoints/ridedata/{}'.format(file_list[len(file_list)-1]), 'r') as f:
            ride_data = json.load(f)
    else:
        ride_data = {}

PAUSE_TIME = 15                                     #pause time between wait time gathering in minutes

def get_data():

    counter = 1
    while True:
        TODAY = datetime.today()
        TOMORROW = datetime.today() + timedelta(days=1)

        parkopen, parkclose = park_hours(TODAY.year, TODAY.month, TODAY.day)

        raw_attractions = load_attractions()
        attractions = []
        print("Checking for attractions with wait times...")
        for attr in tqdm(raw_attractions):
            if attr.checkForAttractionWaitTime():
                attractions.append(attr)

        while True:
            try:
                rides = []
                locations = []
                times = []
                parks = []

                YEAR = datetime.today().year
                MONTH = datetime.today().month
                DAY = datetime.today().day

                print("Getting wait times...")
                for attr in tqdm(attractions):
                    rides.append(attr.getAttractionName())
                    locations.append(attr.getAncestorLand())
                    times.append(attr.getAttractionWaitTime())
                    parks.append(attr.getAncestorThemePark().getParkName())

                if len(rides) != 0:
                    print('Adding new data...')
                    for i, ride in enumerate(rides):            #adds new times and location to ride dictionary...location is added in case its a new location or previously was none
                        if ride in ride_data:
                            ride_data[ride]['Times'][str(datetime.now())] = times[i]
                            ride_data[ride]['Location'] = locations[i].replace(u"\u2013", "-")
                            ride_data[ride]['Park'] = parks[i]
                        else:
                            ride_data[ride] = {'Times' : {}}
                            ride_data[ride]['Times'][str(datetime.now())] = times[i]
                            ride_data[ride]['Location'] = locations[i].replace(u"\u2013", "-")
                            ride_data[ride]['Park'] = parks[i]
                print('{}. Finsihed at {}'.format(counter, datetime.now()))
                counter += 1

                with open('checkpoints/ridedata/ridedata-{}-{}-{}.json'.format(YEAR, formatDate(str(MONTH)), formatDate(str(DAY))), 'w') as f:       #writes ride_data to json file
                    json.dump(ride_data, f)


                if datetime.now() < parkopen or datetime.now() >= parkclose:
                    location_data = {}

                    for key in ride_data:
                        if ride_data[key]["Park"] in location_data:
                            if ride_data[key]['Location'] in location_data[ride_data[key]["Park"]]:
                                location_data[ride_data[key]["Park"]][ride_data[key]["Location"]][key] = {}
                                location_data[ride_data[key]["Park"]][ride_data[key]["Location"]][key]['Times'] = ride_data[key]['Times']
                            else:
                                location_data[ride_data[key]["Park"]][ride_data[key]["Location"]] = {}
                                location_data[ride_data[key]["Park"]][ride_data[key]["Location"]][key] = {}
                                location_data[ride_data[key]["Park"]][ride_data[key]["Location"]][key]['Times'] = ride_data[key]['Times']
                        else:
                            location_data[ride_data[key]["Park"]] = {}
                            location_data[ride_data[key]["Park"]][ride_data[key]["Location"]] = {}
                            location_data[ride_data[key]["Park"]][ride_data[key]["Location"]][key] = {}
                            location_data[ride_data[key]["Park"]][ride_data[key]["Location"]][key]['Times'] = ride_data[key]['Times']

                    with open('checkpoints/bylocation/ridedata-location-{}-{}-{}.json'.format(YEAR, MONTH, DAY), 'w') as f:       #writes ride_data to json file
                        json.dump(location_data, f)

                    tomorrowopen, _ = park_hours(TOMORROW.year, TOMORROW.month, TOMORROW.day)

                    print('All parks are closed at {}:{}. They will reopen at {}:{}.'.format(datetime.now().hour, formatDate(str(datetime.now().minute)), tomorrowopen.hour, formatDate(tomorrowopen.minute)))
                    time_to_open = tomorrowopen - datetime.now()
                    for _ in tqdm(range(time_to_open.seconds)):
                        time.sleep(1)
                    break
                else:
                    for _ in tqdm(range(PAUSE_TIME*60)):
                        time.sleep(1)
            except:
                print("Wait Time Error")


def park_hours(year, month, day):
    print("Getting park hours...")
    DATE = datetime(year, month, day)
    parkopen = datetime(DATE.year, DATE.month, DATE.day, 9)
    parkclose = datetime(DATE.year, DATE.month, DATE.day, 19)

    wdw = Destination("80007798")
    dl = Destination("80008297")
    parks = wdw.getThemeParks() + wdw.getWaterParks() + dl.getThemeParks()

    for park in tqdm(parks):
        hours = park.getParkHours(year, month, day)
        if hours[2] != None:
            if hours[2] < parkopen:
                parkopen = hours[2]
        if hours[0] < parkopen:
            parkopen = hours[0]

        if hours[3] != None:
            if hours[3] > parkclose:
                parkclose = hours[3]
        if hours[1] > parkclose:
            parkclose = hours[1]

    return parkopen, parkclose

def load_attractions():
    print("Loading attractions...")
    wdw = Destination("80007798")
    dl = Destination("80008297")
    attractions = wdw.getAttractions() + dl.getAttractions()
    return attractions

def formatDate(num):
    """
    Formats month and day into proper format
    """
    if len(num) < 2:
        num = '0'+num
    return num

if __name__ == "__main__":
    """
    California is 3 hours behind us...do something about it.
    Possibly "check for wait time" after every iteration to make sure we're only getting attractions with wait times
    """
    print('Starting')
    while True:
        try:
            get_data()
        except KeyboardInterrupt:
            print('Keyboard Interruption, program ended')
            break
        except ConnectionError:
            print("Couldn't get new data")
            time.sleep(PAUSE_TIME*60)
        except Exception:
            print("Attraction Error")
            print("Restarting...")
