'''
Created on Jan 10, 2018

@author: Scott Caratozzolo

'''
from bs4 import BeautifulSoup
import requests
import time
from datetime import datetime
# import pickle
import json
import os



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

park_id = {'Magic Kingdom':'80007944','Epcot':'80007838','Animal Kingdom':'80007823','Hollywood Studios':'80007998'}


PAUSE_TIME = 15                                     #pause time between wait time gathering in minutes
WAIT_INTERVAL = 15

def get_data():
    
#     print('Waiting for 15 minute interval...')
#     while True:                                     #waits until the time is an interval of 15 minutes
#         if datetime.now().minute % WAIT_INTERVAL == 0:
#             break
#               
#         time.sleep(2)

    counter = 1
    while True:                                     #main program
        
        r = requests.get("https://disneyworld.disney.go.com/authentication/get-client-token", headers={'User-Agent': 'Chrome/63.0.3239.132'})
        auth = json.loads(r.text)
        headers = {"Authorization":"BEARER {}".format(auth['access_token']),'User-Agent': 'Chrome/63.0.3239.132'}

        rides = []
        locations = []
        times = []
        parks = []
            
        YEAR = datetime.now().year
        MONTH = datetime.now().month
        DAY = datetime.now().day
            
        
        for park in park_id:
            s = requests.get("https://api.wdpro.disney.go.com/facility-service/theme-parks/{}/wait-times".format(park_id[park]), headers=headers)
        
            data = json.loads(s.content)
            
            for i in range(len(data['entries'])):
                if 'postedWaitMinutes' in data['entries'][i]['waitTime']:
                    rides.append(data['entries'][i]['name'])
                    times.append(data['entries'][i]['waitTime']['postedWaitMinutes'])
                    parks.append(park)
                    if data['entries'][i]['type'] == 'Attraction':
                        q = requests.get("https://api.wdpro.disney.go.com/facility-service/attractions/{}".format(data['entries'][i]['id']), headers=headers)
                        ride_info = json.loads(q.content)
                        locations.append(ride_info['links']['ancestorLand']['title'])
                    else:
                        locations.append(park)

#         print(len(rides), len(locations), len(times), len(parks))
        if len(rides) != 0:   
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
        
        print('{}. New data added at {}'.format(counter, datetime.now()))
        counter += 1
#         print(ride_data)

        with open('checkpoints/ridedata/ridedata-{}-{}-{}.json'.format(YEAR, MONTH, DAY), 'w') as f:       #writes ride_data to json file
            json.dump(ride_data, f)
        
        
        if datetime.now().hour < 6:                #if time is midnight, waits until 6 am to start again
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
            
            print('All parks closed at {}:{} '.format(datetime.now().hour, datetime.now().minute))
            time.sleep((6-datetime.now().hour)*3600)
            print('Parks opening soon: {}:{}'.format(datetime.now().hour, datetime.now().minute))
        else:
            time.sleep(PAUSE_TIME*60)                             #waits 10 minutes before starting again


if __name__ == '__main__':
    try:
        print('Starting')
        get_data()
    except KeyboardInterrupt:
        print('Keyboard Interruption, program ended')
        
        