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


PAUSE_TIME = 10                                     #pause time between wait time gathering in minutes

def get_data():
    
#     print('Waiting for 10 minute interval...')
#     while True:                                     #waits until the time is an interval of 15 minutes
#         if datetime.now().minute % PAUSE_TIME == 0:
#             break
#             
#         time.sleep(2)

    counter = 1
    while True:                                     #main program

        rides = []
        locations = []
        times = []
            
        YEAR = datetime.now().year
        MONTH = datetime.now().month
        DAY = datetime.now().day
            
        
        html = requests.get('https://www.easywdw.com/waits/?&park=All&sort=time&showOther=false').content   #get webpage content
        soup = BeautifulSoup(html, 'lxml')          #parse the webpage
        
        all_h2 = soup.find_all('h2')
        
        for i, elm in enumerate(all_h2[:-2]):       #for every h2 tag in page, determines if it is a ride, location, or time and adds it to a list so they all have the same index
            if elm.string == 'Ride' or elm.string == 'Location' or elm.string == 'Time':
                continue
            elif (i+1) % 3 == 1:
                rides.append(elm.string)
                if elm.string in ride_data:
                    continue
                else:
                    ride_data[elm.string] = {'Times' : {}}
            elif (i+1) % 3 == 2:
                locations.append(elm.string)
            elif (i+1) % 3 == 0:
                times.append(int(elm.string.strip()[:-4]))
        
#         print(len(rides), len(locations), len(times))
        if len(rides) != 0:   
            for i, ride in enumerate(rides):            #adds new times and location to ride dictionary...location is added in case its a new location or previously was none
                ride_data[ride]['Times'][str(datetime.now())] = times[i]
                ride_data[ride]['Location'] = locations[i]
        
        print('{}. New data added at {}'.format(counter, datetime.now()))
        counter += 1
#         print(ride_data)

        with open('checkpoints/ridedata/ridedata-{}-{}-{}.json'.format(YEAR, MONTH, DAY), 'w') as f:       #writes ride_data to json file
            json.dump(ride_data, f)
        
        
        if datetime.now().hour < 6:                #if time is midnight, waits until 6 am to start again
            
            location_data = {}

            for key in ride_data:
                if ride_data[key]["Location"] in location_data:
                    location_data[ride_data[key]["Location"]][key] = {}
                    location_data[ride_data[key]["Location"]][key]['Times'] = ride_data[key]['Times']
                else:
                    location_data[ride_data[key]["Location"]] = {}
                    location_data[ride_data[key]["Location"]][key] = {}
                    location_data[ride_data[key]["Location"]][key]['Times'] = ride_data[key]['Times']
                    
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
        
        