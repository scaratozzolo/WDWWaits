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
import sys

sys.setrecursionlimit(5000)


locations = []
times = []
ride_data = {}
loops = 5
counter = 0

while loops != counter:
    html = requests.get('https://www.easywdw.com/waits/?&park=All&sort=time&showOther=false').content
    soup = BeautifulSoup(html, 'lxml')
    
    all_h2 = soup.find_all('h2')
    
    for i, elm in enumerate(all_h2[:-2]):
        if elm.string == 'Ride' or elm.string == 'Location' or elm.string == 'Time':
            continue
        elif (i+1) % 3 == 1:
            if elm.string in ride_data:
                continue
            else:
                ride_data[elm.string] = {'Times' : []}
        elif (i+1) % 3 == 2:
            locations.append(elm.string)
        elif (i+1) % 3 == 0:
            times.append(elm.string)
    
         
    for i, ride in enumerate(ride_data):
        ride_data[ride]['Times'].append([datetime.now(), times[i]])
        ride_data[ride]['Location'] = locations[i]
        
    print(ride_data)
    counter += 1
    pickle.dump(ride_data, open('ridedata' , 'wb'))
    time.sleep(900)


