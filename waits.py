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
import sys
import os

if os.path.exists('ridedata.json'):                 #checks for ride_data.json and loads it to ride_data as a dictionary if it exists
    with open('ridedata.json', 'r') as f:
        ride_data = json.load(f)
else:
    ride_data = {}                                  #if it doesn't exist, ride_data is an empty dictionary


# sys.setrecursionlimit(5000)



def get_data():
    
    print('Waiting for 15 minute interval...')
    while True:                                     #waits until the time is an interval of 15 minutes
        if datetime.now().minute % 15 == 0:
            break
          
        time.sleep(5)

    counter = 1
    while True:                                     #main program
#     for _ in range(5):
        rides = []
        locations = []
        times = []
        
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
        for i, ride in enumerate(rides):            #adds new times and location to ride dictionary...location is added in case its a new location or previously was none
            ride_data[ride]['Times'][str(datetime.now())] = times[i]
            ride_data[ride]['Location'] = locations[i]
        
        print('{}. New data added at {}'.format(counter, datetime.now()))
        counter += 1
#         print(ride_data)

        with open('ridedata.json', 'w') as f:       #writes ride_data to json file
            json.dump(ride_data, f)
#         pickle.dump(ride_data, open('ridedata.p', 'wb'))
        if datetime.now().hour == 0:                #if time is midnight, waits until 7 am to start again, otherwise waits 15 minutes
            print('All parks closed')
            time.sleep(25200)
            print('Parks opening soon')
        else:
            time.sleep(900)


if __name__ == '__main__':
    try:
        print('Starting')
        get_data()
    except KeyboardInterrupt:
        print('Keyboard Interruption, program ended')
        
        