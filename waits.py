import sys
sys.path.append('D:/Program Projects/MouseTools/')

from datetime import datetime, timedelta
from secretkey import weather_key
import MouseTools
import sqlite3
import json
import time
import requests



class Waits:

    def __init__(self):

        self.DB_NAME = "waits.db"
        self.PAUSE_TIME = 300
        self.today = str(datetime.today()).split(" ")[0]

        self.MouseTools_db = MouseTools.DisneyDatabase()
        self.dests = [MouseTools.Destination(80007798, False), MouseTools.Destination(80008297, False)]
        self.parks = self.dests[0].get_park_ids() + self.dests[1].get_park_ids()
        self.evs = self.dests[0].get_entertainment_venue_ids() + self.dests[1].get_entertainment_venue_ids()

        for id in self.parks + self.evs:
            self.create_park_hours_table(id)
        self.update_park_hours()

        self.create_details_table()
        self.create_weather_table()

        self.main()

    def main(self):

        while True:
            try:
                if self.today < str(datetime.today()).split(" ")[0]:
                    self.today = str(datetime.today()).split(" ")[0]
                    self.update_park_hours()

                self.update()
                time.sleep(self.PAUSE_TIME)
            except Exception as e:
                print(e)


    def create_wait_table(self, id):

        self.c.execute("CREATE TABLE IF NOT EXISTS id_{} (last_pull TEXT PRIMARY KEY, wait_time TEXT, status TEXT)".format(id))


    def create_details_table(self):
        conn = sqlite3.connect(self.DB_NAME)
        c = conn.cursor()

        c.execute("CREATE TABLE IF NOT EXISTS details (id TEXT PRIMARY KEY, name TEXT, last_pull TEXT, last_updated TEXT, wait_time TEXT, status TEXT, dest_id TEXT, park_id TEXT, land_id TEXT, entertainment_venue_id TEXT)")

        conn.commit()
        conn.close()

    def create_park_hours_table(self, id):
        conn = sqlite3.connect(self.DB_NAME)
        c = conn.cursor()

        c.execute("CREATE TABLE IF NOT EXISTS park_{} (date TEXT PRIMARY KEY, operating_open TEXT, operating_close TEXT, extra_magic_open TEXT, extra_magic_close TEXT, status TEXT)".format(id))

        conn.commit()
        conn.close()

    def create_weather_table(self):
        conn = sqlite3.connect(self.DB_NAME)
        c = conn.cursor()

        c.execute("CREATE TABLE IF NOT EXISTS weather_orlando (last_pull TEXT PRIMARY KEY, weather TEXT)")
        c.execute("CREATE TABLE IF NOT EXISTS weather_anaheim (last_pull TEXT PRIMARY KEY, weather TEXT)")

        conn.commit()
        conn.close()

    def update(self):
        conn = sqlite3.connect(self.DB_NAME)
        self.c = conn.cursor()

        conn_mt = sqlite3.connect(self.MouseTools_db.db_path)
        c_mt = conn_mt.cursor()

        for dest in self.dests:

            wait_times = dest.get_wait_times_detailed()
            current_timestamp = datetime.now().timestamp()

            for id, body in wait_times.items():
                self.create_wait_table(id)

                self.c.execute("INSERT INTO id_{} (last_pull, wait_time, status) VALUES (?, ?, ?)".format(id), (current_timestamp, body['wait_time'], body['status'],))
                park_id, land_id, ev_id = c_mt.execute("SELECT park_id, land_id, entertainment_venue_id FROM facilities WHERE id = ?", (id,)).fetchone()
                self.c.execute("INSERT OR REPLACE INTO details (id, name, last_pull, last_updated, wait_time, status, dest_id, park_id, land_id, entertainment_venue_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (id, body['name'], current_timestamp, body["last_updated"].timestamp(), body["wait_time"], body["status"], dest.get_id(), park_id, land_id, ev_id))

        orlando_weather = requests.get("https://api.openweathermap.org/data/2.5/weather?lat=28.388195&lon=-81.569324&units=imperial&appid={}".format(weather_key)).json()
        anaheim_weather = requests.get("https://api.openweathermap.org/data/2.5/weather?lat=33.808666&lon=-117.918955&units=imperial&appid={}".format(weather_key)).json()
        self.c.execute("INSERT INTO weather_orlando (last_pull, weather) VALUES (?, ?)", (current_timestamp, json.dumps(orlando_weather),))
        self.c.execute("INSERT INTO weather_anaheim (last_pull, weather) VALUES (?, ?)", (current_timestamp, json.dumps(anaheim_weather),))

        conn.commit()
        conn.close()
        conn_mt.commit()
        conn_mt.close()

        print("Update waits successful, time: " + str(datetime.now()))

    def update_park_hours(self):

        conn = sqlite3.connect(self.DB_NAME)
        c = conn.cursor()

        for id in self.parks:
            park = MouseTools.Park(id)

            operating_open, operating_close, extra_magic_open, extra_magic_close = park.get_hours()
            try:
                operating_open = operating_open.timestamp()
            except:
                pass
            try:
                operating_close = operating_close.timestamp()
            except:
                pass
            try:
                extra_magic_open = extra_magic_open.timestamp()
            except:
                pass
            try:
                extra_magic_close = extra_magic_close.timestamp()
            except:
                pass

            c.execute("INSERT OR REPLACE INTO park_{} (date, operating_open, operating_close, extra_magic_open, extra_magic_close, status) VALUES (?, ?, ?, ?, ?, ?)".format(id), (self.today, operating_open, operating_close, extra_magic_open, extra_magic_close, park.get_status()))

        for id in self.evs:
            ev = MouseTools.EntertainmentVenue(id)

            operating_open, operating_close, extra_magic_open, extra_magic_close = ev.get_hours()
            try:
                operating_open = operating_open.timestamp()
            except:
                pass
            try:
                operating_close = operating_close.timestamp()
            except:
                pass
            try:
                extra_magic_open = extra_magic_open.timestamp()
            except:
                pass
            try:
                extra_magic_close = extra_magic_close.timestamp()
            except:
                pass

            c.execute("INSERT OR REPLACE INTO park_{} (date, operating_open, operating_close, extra_magic_open, extra_magic_close, status) VALUES (?, ?, ?, ?, ?, ?)".format(id), (self.today, operating_open, operating_close, extra_magic_open, extra_magic_close, ev.get_status()))


        conn.commit()
        conn.close()

        print("Update hours successful, time: " + str(datetime.now()))

if __name__ == '__main__':

    waits_obj = Waits()
