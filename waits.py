'''
Created on Jan 10, 2018

@author: Scott Caratozzolo

I pledge my honor that I have abided by the Stevens Honor System - scaratoz
'''
from bs4 import BeautifulSoup
import requests
import time
from datetime import datetime
import pickle
import json
import sys
import os

if os.path.exists('ridedata.p'):
    ride_data = pickle.load(open('ridedata.p', 'rb'))
else:
    ride_data = {}


sys.setrecursionlimit(5000)



def get_data():


    for _ in range(5):
        rides = []
        locations = []
        times = []
        
        html = requests.get('https://www.easywdw.com/waits/?&park=All&sort=time&showOther=false').content
        soup = BeautifulSoup(html, 'lxml')
        
        all_h2 = soup.find_all('h2')
        
        for i, elm in enumerate(all_h2[:-2]):
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
        
            
        for i, ride in enumerate(rides):
            ride_data[ride]['Times'][str(datetime.now())] = times[i]
            ride_data[ride]['Location'] = locations[i]
        
        print(datetime.now())
        print(ride_data)

        with open('ridedata.json', 'w') as f:
            json.dump(ride_data, f)
        pickle.dump(ride_data, open('ridedata.p', 'wb'))
        time.sleep(900)


if __name__ == '__main__':
#     while True:
#         if datetime.now().minute % 15 == 0:
#             get_data()
#             break
#         
#         time.sleep(60)

    get_data()