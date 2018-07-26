import sys
try:
    from MouseTools.auth import getHeaders
except:
    print("You must pip install MouseTools.")
    sys.exit()

from MouseTools.auth import getHeaders
from MouseTools.destinations import Destination, WDW_ID, DL_ID
from MouseTools.parks import Park
from MouseTools.attractions import Attraction
from MouseTools.entertainments import Entertainment
from tqdm import tqdm
from datetime import datetime, timedelta
from secretkey import weather_key
import requests
import time
import json
import os

PROGBAR = False
if PROGBAR:
    bar = "tqdm"
else:
    bar = ""

print("""\nStarting WDWWaits
                        .d88888888bo.
                      .d8888888888888b.
                      8888888888888888b
                      888888888888888888
                      888888888888888888
                       Y8888888888888888
                 ,od888888888888888888P
              .'`Y8P'```'Y8888888888P'
            .'_   `  _     'Y88888888b
           /  _`    _ `      Y88888888b   ____
        _  | /  \  /  \      8888888888.d888888b.
       d8b | | /|  | /|      8888888888d8888888888b
      8888_\ \_|/  \_|/      d888888888888888888888b
      .Y8P  `'-.            d88888888888888888888888
     /          `          `      `Y8888888888888888
     |                        __    888888888888888P
      \                       / `   dPY8888888888P'
       '._                  .'     .'  `Y888888P`
          `"'-.,__    ___.-'    .-'
              `-._````  __..--'`
                  ``````
Weather Powered by Dark Sky https://darksky.net/poweredby/
""")


PAUSE_TIME = 5                                     #pause time between wait time gathering in minutes

running = True
while running:
    try:
        wdw = Destination(WDW_ID)
        dl = Destination(DL_ID)
        print("Destinations loaded")
        running = False
    except:
        pass

parks_dict = {}

def get_data():

    counter = 1
    while True:
        global parks_dict
        parks_dict = {"WDW": wdw.getThemeParks(), "DL": dl.getThemeParks()}

        TODAY = datetime.today()
        TOMORROW = datetime.today() + timedelta(days=1)

        global ride_data
        if counter > 1:
            ride_data = {}

        parkopen, parkclose = all_hours(TODAY.year, TODAY.month, TODAY.day)

        raw_attractions, raw_entertainments = load_all_attractions()

        while True:
            try:

                all_attractions, all_entertainments = load_attractions(raw_attractions, raw_entertainments)

                attractions = []
                entertainments = []
                print("Checking for attractions with wait times...")
                for attr in eval("{}(all_attractions)".format(bar)):
                    if attr.checkForAttractionWaitTime():
                        attractions.append(attr)
                print("Checking for entertainments with wait times...")
                for enter in eval("{}(all_entertainments)".format(bar)):
                    if enter.checkForEntertainmentWaitTime():
                        entertainments.append(enter)

                rides = []
                ids = []
                times = []
                locations = []
                parks = []
                coords = []

                NOW = datetime.now()

                print("Getting wait times...")
                for attr in eval("{}(attractions)".format(bar)):
                    park = attr.getAncestorThemePark()
                    for theme in parks_dict["WDW"]:
                        if theme == park:
                            rides.append(attr.getAttractionName() + " - WDW")
                            ids.append(attr.getAttractionID())
                            times.append(attr.getAttractionWaitTimeFromData())
                            locations.append(attr.getAncestorLand())
                            parks.append(park.getParkName())
                            coords.append(attr.getAttractionCoordinates())

                    for theme in parks_dict["DL"]:
                        if theme == park:
                            rides.append(attr.getAttractionName() + " - DL")
                            ids.append(attr.getAttractionID())
                            times.append(attr.getAttractionWaitTimeFromData())
                            locations.append(attr.getAncestorLand())
                            parks.append(park.getParkName())
                            coords.append(attr.getAttractionCoordinates())

                for enter in eval("{}(entertainments)".format(bar)):
                    park = enter.getAncestorThemePark()
                    for theme in parks_dict["WDW"]:
                        if theme == park:
                            rides.append(enter.getEntertainmentName() + " - WDW")
                            ids.append(enter.getEntertainmentID())
                            times.append(enter.getEntertainmentWaitTime())
                            locations.append(enter.getAncestorLand())
                            parks.append(park.getParkName())
                            coords.append(enter.getEntertainmentCoordinates())

                    for theme in parks_dict["DL"]:
                        if theme == park:
                            rides.append(enter.getEntertainmentName() + " - DL")
                            ids.append(enter.getEntertainmentID())
                            times.append(enter.getEntertainmentWaitTime())
                            locations.append(enter.getAncestorLand())
                            parks.append(park.getParkName())
                            coords.append(enter.getEntertainmentCoordinates())

                if len(rides) != 0:
                    print('Adding new data...')
                    ride_data["last_updated"] = str(datetime(NOW.year, NOW.month, NOW.day, NOW.hour, NOW.minute))

                    orlando_data = requests.get("https://api.darksky.net/forecast/{}/28.388195,-81.569324?exclude=hourly,daily,flags".format(weather_key)).json()
                    anaheim_data = requests.get("https://api.darksky.net/forecast/{}/33.808666,-117.918955?exclude=hourly,daily,flags".format(weather_key)).json()

                    if "Orlando" in ride_data:
                        ride_data["Orlando"][str(datetime(NOW.year, NOW.month, NOW.day, NOW.hour, NOW.minute))] = orlando_data
                    else:
                        ride_data["Orlando"] = {}
                        ride_data["Orlando"][str(datetime(NOW.year, NOW.month, NOW.day, NOW.hour, NOW.minute))] = orlando_data

                    if "Anaheim" in ride_data:
                        ride_data["Anaheim"][str(datetime(NOW.year, NOW.month, NOW.day, NOW.hour, NOW.minute))] = anaheim_data
                    else:
                        ride_data["Anaheim"] = {}
                        ride_data["Anaheim"][str(datetime(NOW.year, NOW.month, NOW.day, NOW.hour, NOW.minute))] = anaheim_data

                    for i, ride in enumerate(rides):            #adds new times and location to ride dictionary...location is added in case its a new location or previously was none
                        if ride in ride_data:
                            ride_data[ride]['Times'][str(datetime(NOW.year, NOW.month, NOW.day, NOW.hour, NOW.minute))] = times[i]
                            ride_data[ride]["ID"] = ids[i]      #check if two rides have the same ID, incase of name changes or such ex. slinky dog
                            ride_data[ride]['Location'] = locations[i].replace(u"\u2013", "-")
                            ride_data[ride]['Park'] = parks[i]
                            ride_data[ride]['Coordinates'] = coords[i]
                        else:
                            ride_data[ride] = {'Times' : {}}
                            ride_data[ride]["ID"] = ids[i]
                            ride_data[ride]['Times'][str(datetime(NOW.year, NOW.month, NOW.day, NOW.hour, NOW.minute))] = times[i]
                            ride_data[ride]['Location'] = locations[i].replace(u"\u2013", "-")
                            ride_data[ride]['Park'] = parks[i]
                            ride_data[ride]['Coordinates'] = coords[i]

                print('Finished at {}\n'.format(datetime.now()))
                counter += 1

                with open('checkpoints/ridedata/ridedata-{}-{}-{}.json'.format(TODAY.year, formatDate(str(TODAY.month)), formatDate(str(TODAY.day))), 'w') as f:       #writes ride_data to json file
                    json.dump(ride_data, f)


                if datetime.now() < parkopen or datetime.now() >= parkclose:
                    location_data = {}

                    for key in ride_data:
                        if key != "Orlando" and key != "Anaheim" and key != "last_updated":
                            if ride_data[key]["Park"] in location_data:
                                if ride_data[key]['Location'] in location_data[ride_data[key]["Park"]]:
                                    location_data[ride_data[key]["Park"]][ride_data[key]["Location"]][key] = {}
                                    location_data[ride_data[key]["Park"]][ride_data[key]["Location"]][key]['Times'] = ride_data[key]['Times']
                                    location_data[ride_data[key]["Park"]][ride_data[key]["Location"]][key]['ID'] = ride_data[key]['ID']
                                    location_data[ride_data[key]["Park"]][ride_data[key]["Location"]][key]['Coordinates'] = ride_data[key]['Coordinates']
                                else:
                                    location_data[ride_data[key]["Park"]][ride_data[key]["Location"]] = {}
                                    location_data[ride_data[key]["Park"]][ride_data[key]["Location"]][key] = {}
                                    location_data[ride_data[key]["Park"]][ride_data[key]["Location"]][key]['Times'] = ride_data[key]['Times']
                                    location_data[ride_data[key]["Park"]][ride_data[key]["Location"]][key]['ID'] = ride_data[key]['ID']
                                    location_data[ride_data[key]["Park"]][ride_data[key]["Location"]][key]['Coordinates'] = ride_data[key]['Coordinates']
                            else:
                                location_data[ride_data[key]["Park"]] = {}
                                location_data[ride_data[key]["Park"]][ride_data[key]["Location"]] = {}
                                location_data[ride_data[key]["Park"]][ride_data[key]["Location"]][key] = {}
                                location_data[ride_data[key]["Park"]][ride_data[key]["Location"]][key]['Times'] = ride_data[key]['Times']
                                location_data[ride_data[key]["Park"]][ride_data[key]["Location"]][key]['ID'] = ride_data[key]['ID']
                                location_data[ride_data[key]["Park"]][ride_data[key]["Location"]][key]['Coordinates'] = ride_data[key]['Coordinates']
                        else:
                            location_data[key] = ride_data[key]

                    with open('checkpoints/bylocation/ridedata-location-{}-{}-{}.json'.format(TODAY.year, formatDate(str(TODAY.month)), formatDate(str(TODAY.day))), 'w') as f:       #writes ride_data to json file
                        json.dump(location_data, f)

                    # os.system("git add checkpoints")
                    # os.system('"git commit -m "Newest Data"')
                    # os.system("git push")

                    NOW = datetime.now()
                    if TODAY.month == NOW.month and TODAY.day == NOW.day and NOW.hour < 7:  #may need to adjust hour
                        tomorrowopen, _ = all_hours(TODAY.year, TODAY.month, TODAY.day)
                    else:
                        tomorrowopen, _ = all_hours(TOMORROW.year, TOMORROW.month, TOMORROW.day)

                    print('All parks are closed at {}:{}. They will reopen at {}:{}.'.format(datetime.now().hour, formatDate(str(datetime.now().minute)), tomorrowopen.hour, formatDate(str(tomorrowopen.minute))))
                    time_to_open = tomorrowopen - datetime.now()
                    for _ in eval("{}(range(time_to_open.seconds - 900))".format(bar)):
                        time.sleep(1)
                    break
                else:
                    for _ in eval("{}(range(PAUSE_TIME*60))".format(bar)):
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

    for park in eval("{}(parks)".format(bar)):
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
    raw_attractions = {}
    raw_entertainments = {}
    wdw = Destination(WDW_ID)
    dl = Destination(DL_ID)
    print("Loading attractions...")                                             #Get IDs and load the objects here for better manipulation
    attractions = wdw.getAttractions() + dl.getAttractions()
    print("Loading entertainments...")                                          #Get IDs and load the objects here for better manipulation
    entertainments = wdw.getEntertainments() + dl.getEntertainments()

    print("Sorting {} attractions and entertainments by park...".format(len(attractions)+len(entertainments)))
    for attr in eval("{}(attractions)".format(bar)):
        park = attr.getAncestorThemeParkID()
        if park != None and park != "80007981" and park != "80007834": #removes the waterparks
            if park in raw_attractions:
                raw_attractions[park].append(attr)
            else:
                raw_attractions[park] = [attr]

    for enter in eval("{}(entertainments)".format(bar)):
        park = enter.getAncestorThemeParkID()
        if park != None and park != "80007981" and park != "80007834": #removes the waterparks
            if park in raw_entertainments:
                raw_entertainments[park].append(enter)
            else:
                raw_entertainments[park] = [enter]

    return raw_attractions, raw_entertainments

def load_attractions(raw_attractions, raw_entertainments):

    DATE = datetime.today()
    # DATE = datetime(2018,5,28,7)
    attractions = []
    entertainments = []

    open = 0
    for theme in eval("{}(raw_attractions)".format(bar)):
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
                entertainments += raw_entertainments[theme]
                open+=1
        except:
            pass
    print("{} parks open right now...".format(open))
    return attractions, entertainments


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
            print("\n", e)
            print("Attraction Error")
            print("Restarting...")
