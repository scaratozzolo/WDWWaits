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

PAUSE_TIME = 15                                     #pause time between wait time gathering in minutes

wdw = Destination("80007798")
dl = Destination("80008297")
parks_dict = {"WDW": wdw.getThemeParks() + wdw.getWaterParks(), "DL": dl.getThemeParks()}

def get_data():

    counter = 1
    while True:
        global parks_dict
        parks_dict = {"WDW": wdw.getThemeParks() + wdw.getWaterParks(), "DL": dl.getThemeParks()}

        TODAY = datetime.today()
        TOMORROW = datetime.today() + timedelta(days=1)

        global ride_data
        if counter > 1:
            ride_data = {}

        parkopen, parkclose = all_hours(TODAY.year, TODAY.month, TODAY.day)

        raw_attractions = load_all_attractions()

        while True:
            try:

                all_attractions = load_attractions(raw_attractions)

                attractions = []
                print("Checking for attractions with wait times...")
                for attr in tqdm(all_attractions):
                    if attr.checkForAttractionWaitTime():
                        attractions.append(attr)

                rides = []
                ids = []
                times = []
                locations = []
                parks = []

                NOW = datetime.now()

                print("Getting wait times...")
                for attr in tqdm(attractions):
                    park = attr.getAncestorThemePark()
                    for theme in parks_dict["WDW"]:
                        if theme == park:
                            rides.append(attr.getAttractionName() + " - WDW")
                            ids.append(attr.getAttractionID())
                            times.append(attr.getAttractionWaitTime())
                            locations.append(attr.getAncestorLand())
                            parks.append(park.getParkName())

                    for theme in parks_dict["DL"]:
                        if theme == park:
                            rides.append(attr.getAttractionName() + " - DL")
                            ids.append(attr.getAttractionID())
                            times.append(attr.getAttractionWaitTime())
                            locations.append(attr.getAncestorLand())
                            parks.append(park.getParkName())

                if len(rides) != 0:
                    print('Adding new data...')
                    for i, ride in enumerate(rides):            #adds new times and location to ride dictionary...location is added in case its a new location or previously was none
                        if ride in ride_data:
                            ride_data[ride]['Times'][str(datetime(NOW.year, NOW.month, NOW.day, NOW.hour, NOW.minute))] = times[i]
                            ride_data[ride]["ID"] = ids[i]
                            ride_data[ride]['Location'] = locations[i].replace(u"\u2013", "-")
                            ride_data[ride]['Park'] = parks[i]
                        else:
                            ride_data[ride] = {'Times' : {}}
                            ride_data[ride]["ID"] = ids[i]
                            ride_data[ride]['Times'][str(datetime(NOW.year, NOW.month, NOW.day, NOW.hour, NOW.minute))] = times[i]
                            ride_data[ride]['Location'] = locations[i].replace(u"\u2013", "-")
                            ride_data[ride]['Park'] = parks[i]

                    weather_data = requests.get("https://api.openweathermap.org/data/2.5/group?id=4167147,5323810&units=imperial&appid=07e91d416dbdfcbd7d7ab9c8096ac687").json()
                    for entry in weather_data["list"]:
                        if entry["name"] in ride_data:
                            ride_data[entry["name"]][str(datetime(NOW.year, NOW.month, NOW.day, NOW.hour, NOW.minute))] = {}
                            ride_data[entry["name"]][str(datetime(NOW.year, NOW.month, NOW.day, NOW.hour, NOW.minute))]["weather"] = entry["weather"]
                            ride_data[entry["name"]][str(datetime(NOW.year, NOW.month, NOW.day, NOW.hour, NOW.minute))]["main"] = entry["main"]
                            ride_data[entry["name"]][str(datetime(NOW.year, NOW.month, NOW.day, NOW.hour, NOW.minute))]["wind"] = entry["wind"]
                            ride_data[entry["name"]][str(datetime(NOW.year, NOW.month, NOW.day, NOW.hour, NOW.minute))]["clouds"] = entry["clouds"]
                            try:
                                ride_data[entry["name"]][str(datetime(NOW.year, NOW.month, NOW.day, NOW.hour, NOW.minute))]["rain"] = entry["rain"]
                            except:
                                pass
                        else:
                            ride_data[entry["name"]] = {}
                            ride_data[entry["name"]][str(datetime(NOW.year, NOW.month, NOW.day, NOW.hour, NOW.minute))] = {}
                            ride_data[entry["name"]][str(datetime(NOW.year, NOW.month, NOW.day, NOW.hour, NOW.minute))]["weather"] = entry["weather"]
                            ride_data[entry["name"]][str(datetime(NOW.year, NOW.month, NOW.day, NOW.hour, NOW.minute))]["main"] = entry["main"]
                            ride_data[entry["name"]][str(datetime(NOW.year, NOW.month, NOW.day, NOW.hour, NOW.minute))]["wind"] = entry["wind"]
                            ride_data[entry["name"]][str(datetime(NOW.year, NOW.month, NOW.day, NOW.hour, NOW.minute))]["clouds"] = entry["clouds"]
                            try:
                                ride_data[entry["name"]][str(datetime(NOW.year, NOW.month, NOW.day, NOW.hour, NOW.minute))]["rain"] = entry["rain"]
                            except:
                                pass

                print('{}. Finsihed at {}'.format(counter, datetime.now()))
                counter += 1

                with open('checkpoints/ridedata/ridedata-{}-{}-{}.json'.format(TODAY.year, formatDate(str(TODAY.month)), formatDate(str(TODAY.day))), 'w') as f:       #writes ride_data to json file
                    json.dump(ride_data, f)

                if datetime.now() < parkopen or datetime.now() >= parkclose:
                    location_data = {}

                    for key in ride_data:
                        if key != "Orlando" or key != "Anaheim":
                            if ride_data[key]["Park"] in location_data:
                                if ride_data[key]['Location'] in location_data[ride_data[key]["Park"]]:
                                    location_data[ride_data[key]["Park"]][ride_data[key]["Location"]][key] = {}
                                    location_data[ride_data[key]["Park"]][ride_data[key]["Location"]][key]['Times'] = ride_data[key]['Times']
                                    location_data[ride_data[key]["Park"]][ride_data[key]["Location"]][key]['ID'] = ride_data[key]['ID']
                                else:
                                    location_data[ride_data[key]["Park"]][ride_data[key]["Location"]] = {}
                                    location_data[ride_data[key]["Park"]][ride_data[key]["Location"]][key] = {}
                                    location_data[ride_data[key]["Park"]][ride_data[key]["Location"]][key]['Times'] = ride_data[key]['Times']
                                    location_data[ride_data[key]["Park"]][ride_data[key]["Location"]][key]['ID'] = ride_data[key]['ID']
                            else:
                                location_data[ride_data[key]["Park"]] = {}
                                location_data[ride_data[key]["Park"]][ride_data[key]["Location"]] = {}
                                location_data[ride_data[key]["Park"]][ride_data[key]["Location"]][key] = {}
                                location_data[ride_data[key]["Park"]][ride_data[key]["Location"]][key]['Times'] = ride_data[key]['Times']
                                location_data[ride_data[key]["Park"]][ride_data[key]["Location"]][key]['ID'] = ride_data[key]['ID']
                        else:
                            location_data[key] = ride_data[key]

                    with open('checkpoints/bylocation/ridedata-location-{}-{}-{}.json'.format(TODAY.year, formatDate(str(TODAY.month)), formatDate(str(TODAY.day))), 'w') as f:       #writes ride_data to json file
                        json.dump(location_data, f)

                    NOW = datetime.now()
                    if TODAY.month == NOW.month and TODAY.day == NOW.day and NOW.hour < 7:  #may need to adjust hour
                        tomorrowopen, _ = all_hours(TODAY.year, TODAY.month, TODAY.day)
                    else:
                        tomorrowopen, _ = all_hours(TOMORROW.year, TOMORROW.month, TOMORROW.day)

                    print('All parks are closed at {}:{}. They will reopen at {}:{}.'.format(datetime.now().hour, formatDate(str(datetime.now().minute)), tomorrowopen.hour, formatDate(str(tomorrowopen.minute))))
                    time_to_open = tomorrowopen - datetime.now()
                    for _ in tqdm(range(time_to_open.seconds)):
                        time.sleep(1)
                    break
                else:
                    for _ in tqdm(range(PAUSE_TIME*60)):
                        time.sleep(1)
            except Exception as e:
                print(e)
                print("Wait Time Error")


def all_hours(year, month, day):
    print("Getting park hours...")
    DATE = datetime(year, month, day)
    parkopen = datetime(DATE.year, DATE.month, DATE.day, 12)
    parkclose = datetime(DATE.year, DATE.month, DATE.day, 12)

    parks = parks_dict["WDW"] + parks_dict["DL"]

    for park in tqdm(parks):
        for item in parks_dict["WDW"]:
            if park == item:
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

        for item in parks_dict["DL"]:
            if park == item:
                hours = park.getParkHours(year, month, day)
                if hours[2] != None:
                    if hours[2] + timedelta(hours=3) < parkopen:
                        parkopen = hours[2] + timedelta(hours=3)
                if hours[0] + timedelta(hours=3) < parkopen:
                    parkopen = hours[0] + timedelta(hours=3)

                if hours[3] != None:
                    if hours[3] + timedelta(hours=3) > parkclose:
                        parkclose = hours[3] + timedelta(hours=3)
                if hours[1] + timedelta(hours=3) > parkclose:
                    parkclose = hours[1] + timedelta(hours=3)

    return parkopen, parkclose

def park_hours(park, year, month, day):
    DATE = datetime(year, month, day)

    for item in parks_dict["WDW"]:
        if park == item:
            parkopen = datetime(DATE.year, DATE.month, DATE.day, 12)
            parkclose = datetime(DATE.year, DATE.month, DATE.day, 12)

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

    for item in parks_dict["DL"]:
        if park == item:
            parkopen = datetime(DATE.year, DATE.month, DATE.day, 15)
            parkclose = datetime(DATE.year, DATE.month, DATE.day, 15)
            hours = park.getParkHours(year, month, day)
            if hours[2] != None:
                if hours[2] + timedelta(hours=3) < parkopen:
                    parkopen = hours[2] + timedelta(hours=3)
            if hours[0] + timedelta(hours=3) < parkopen:
                parkopen = hours[0] + timedelta(hours=3)

            if hours[3] != None:
                if hours[3] + timedelta(hours=3) > parkclose:
                    parkclose = hours[3] + timedelta(hours=3)
            if hours[1] + timedelta(hours=3) > parkclose:
                parkclose = hours[1] + timedelta(hours=3)

    return parkopen, parkclose

def load_all_attractions():
    print("Loading attractions...")
    raw_attractions = {}
    wdw = Destination("80007798")
    dl = Destination("80008297")
    attractions = wdw.getAttractions() + dl.getAttractions()

    for attr in attractions:
        park = attr.getAncestorThemeParkID()
        if park != None:
            if park in raw_attractions:
                raw_attractions[park].append(attr)
            else:
                raw_attractions[park] = [attr]

    return raw_attractions

def load_attractions(raw_attractions):

    DATE = datetime.today()
    # DATE = datetime(2018,5,28,7)
    attractions = []

    open = 0
    for theme in tqdm(raw_attractions):
        try:
            park = Park(theme)
            if DATE.hour >= 7:
                parkopen, parkclose = park_hours(park, DATE.year, DATE.month, DATE.day)
                # print(park, parkopen, parkclose, "1")
            else:
                YESTERDAY = DATE - timedelta(days=1)
                parkopen, parkclose = park_hours(park, YESTERDAY.year, YESTERDAY.month, YESTERDAY.day)
                # print(park, parkopen, parkclose, "2")

            if datetime.now() >= parkopen and datetime.now() <= parkclose:
                attractions += raw_attractions[theme]
                open+=1
        except:
            pass
    print("{} parks open right now...".format(open))
    return attractions


def formatDate(num):
    """
    Formats numbers into 2 digit strings
    """
    if len(num) < 2:
        num = '0'+num
    return num

if __name__ == "__main__":
    # print(park_hours(Park("80007981"), 2018, 5, 26))
    # print(park_hours(Park("336894"), 2018, 5, 26))
    # load_attractions(load_all_attractions())
    # print(park_hours(Park("336894"), 2018, 5, 26))
    # print(park_hours(Park("330339"), 2018, 5, 26))
    print('Starting')

    if not os.path.exists('checkpoints'):               #checks for checkpoints directory and creates it
        os.makedirs('checkpoints')
        os.makedirs('checkpoints/ridedata')
        os.makedirs('checkpoints/bylocation')

    TODAY = datetime.today()
    if os.path.exists('checkpoints'):                   #checks for ride_data.json and loads it to ride_data as a dictionary if it exists
        if os.path.isfile('checkpoints/ridedata/ridedata-{}-{}-{}.json'.format(TODAY.year, formatDate(str(TODAY.month)), formatDate(str(TODAY.day)))):
            with open('checkpoints/ridedata/ridedata-{}-{}-{}.json'.format(TODAY.year, formatDate(str(TODAY.month)), formatDate(str(TODAY.day))), 'r') as f:
                ride_data = json.load(f)
        else:
            ride_data = {}

    while True:
        try:
            get_data()
        except KeyboardInterrupt:
            print('Keyboard Interruption, program ended')
            break
        except ConnectionError:
            print("Couldn't get new data")
            time.sleep(PAUSE_TIME*60)
        except Exception as e:
            # print(e)
            print("Attraction Error")
            print("Restarting...")
