'''
Created on Jan 10, 2018

@author: Scott Caratozzolo

'''
import requests
import time
from datetime import datetime, timedelta
import json
import os
from tqdm import tqdm

#test


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
        ride_data = {}                              #if it doesn't exist, ride_data is an empty dictionary

park_id = {'Magic Kingdom Park':'80007944','Epcot':'80007838',"Disney's Animal Kingdom Theme Park":'80007823',"Disney's Hollywood Studios":'80007998'}


PAUSE_TIME = 15                                     #pause time between wait time gathering in minutes
WAIT_INTERVAL = 15

def get_data():

#     print('Waiting for 15 minute interval...')
#     while True:                                     #waits until the time is an interval of 15 minutes
#         if datetime.now().minute % WAIT_INTERVAL == 0:
#             break
#
#         time.sleep(2)

    parkopen, parkclose = park_hours()

    counter = 1
    while True:                                     #main program

        r = requests.get("https://disneyworld.disney.go.com/authentication/get-client-token", headers={'User-Agent': 'Chrome/63.0.3239.132'})
        auth = json.loads(r.text)
        headers = {"Authorization":"BEARER {}".format(auth['access_token']),'User-Agent': 'Chrome/63.0.3239.132'}

        rides = []
        locations = []
        times = []
        parks = []

        YEAR = datetime.today().year
        MONTH = datetime.today().month
        DAY = datetime.today().day


        for park in park_id:
            s = requests.get("https://api.wdpro.disney.go.com/facility-service/theme-parks/{}/wait-times".format(park_id[park]), headers=headers)

            data = json.loads(s.content)
            print('Getting wait times for {}'.format(park))
            for i in tqdm(range(len(data['entries']))):
                if 'postedWaitMinutes' in data['entries'][i]['waitTime']:
                    rides.append(data['entries'][i]['name'])
                    times.append(data['entries'][i]['waitTime']['postedWaitMinutes'])
                    if data['entries'][i]['type'] == 'Attraction':
                        q = requests.get("https://api.wdpro.disney.go.com/facility-service/attractions/{}".format(data['entries'][i]['id']), headers=headers)
                        ride_info = json.loads(q.content)
                        locations.append(ride_info['links']['ancestorLand']['title'])
                        parks.append(ride_info['links']['ancestorThemePark']['title'])
                    else:
                        locations.append('{} Entertainment'.format(park))
                        parks.append(park)


#         print(len(rides), len(locations), len(times), len(parks), len(status))
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
#         print(ride_data)

        with open('checkpoints/ridedata/ridedata-{}-{}-{}.json'.format(YEAR, MONTH, DAY), 'w') as f:       #writes ride_data to json file
            json.dump(ride_data, f)





        if datetime.now().hour < parkopen or datetime.now().hour >= parkclose:                #if time is midnight, waits until 6 am to start again
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

            tempparkopen = parkopen
            tempparkclose = parkclose

            MINUTE = datetime.now().minute

            if len(str(MINUTE)) < 2:
                MINUTE = '0'+str(MINUTE)

            parkopen, parkclose = park_hours()

            print('All parks are closed at {}:{}. They will reopen at {}:00'.format(datetime.now().hour, MINUTE, tempparkopen))
            time.sleep((tempparkopen-(tempparkclose - 24))*3600)
            print('Parks opening at: {}:00'.format(tempparkopen))
        else:
            time.sleep(PAUSE_TIME*60)                             #waits 10 minutes before starting again


def park_hours():

    print('Getting park hours...')
    r = requests.get("https://disneyworld.disney.go.com/authentication/get-client-token", headers={'User-Agent': 'Chrome/63.0.3239.132'})
    data = json.loads(r.text)
    headers = {"Authorization":"BEARER {}".format(data['access_token']),'User-Agent': 'Chrome/63.0.3239.132'}

    YEAR = str(datetime.today().year)
    MONTH = str(datetime.today().month)
    DAY = str(datetime.today().day)


    if len(MONTH) < 2:
        MONTH = '0'+MONTH

    if len(DAY) < 2:
        DAY = '0'+DAY

    tomorrow = datetime.today() + timedelta(days=1)

    TOMORROWYEAR = str(tomorrow.year)
    TOMORROWMONTH = str(tomorrow.month)
    TOMORROWDAY = str(tomorrow.day)

    if len(TOMORROWMONTH) < 2:
        TOMORROWMONTH = '0'+TOMORROWMONTH

    if len(TOMORROWDAY) < 2:
        TOMORROWDAY = '0'+TOMORROWDAY

    parkopen = 9
    parkclose = 20


    for park in tqdm(park_id):
        # for park in park_id:
        s = requests.get("https://api.wdpro.disney.go.com/global-pool-override-B/facility-service/schedules/{}".format(park_id[park]), headers=headers)
        data = json.loads(s.content)


        for i in range(len(data['schedules'])):
            if data['schedules'][i]['date'] == '{}-{}-{}'.format(TOMORROWYEAR, TOMORROWMONTH, TOMORROWDAY):
                if int(data['schedules'][i]['startTime'][:2]) < parkopen:
                    parkopen = int(data['schedules'][i]['startTime'][:2])

            if data['schedules'][i]['date'] == '{}-{}-{}'.format(YEAR, MONTH, DAY):
                if int(data['schedules'][i]['endTime'][:2]) > parkclose:
                    parkclose = int(data['schedules'][i]['endTime'][:2])

    return parkopen, parkclose


if __name__ == '__main__':
    while True:
        try:
            print('Starting')
            get_data()
        except KeyboardInterrupt:
            print('Keyboard Interruption, program ended')
            break
        except ConnectionError:
            print("Couldn't get new data")
            time.sleep(PAUSE_TIME*60)
