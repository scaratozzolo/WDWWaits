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
        self.create_parks_table()
        self.create_schedules_table()

        self.update_park_hours()
        self.update_entertainment_schedules()

        self.create_details_table()
        self.create_weather_table()

        self.main()

    def main(self):

        while True:
            try:
                if self.today < str(datetime.today()).split(" ")[0]:
                    self.today = str(datetime.today()).split(" ")[0]
                    self.MouseTools_db.sync_database()
                    self.update_park_hours()
                    self.update_entertainment_schedules()

                self.update()
                time.sleep(self.PAUSE_TIME)
            except Exception as e:
                print(e)


    def create_wait_table(self, id):

        self.c.execute("CREATE TABLE IF NOT EXISTS id_{} (last_pull TEXT PRIMARY KEY, wait_time TEXT, status TEXT)".format(id))


    def create_details_table(self):
        conn = sqlite3.connect(self.DB_NAME)
        c = conn.cursor()

        c.execute("CREATE TABLE IF NOT EXISTS details (id TEXT PRIMARY KEY, name TEXT, entityType TEXT, last_pull TEXT, last_updated TEXT, wait_time TEXT, status TEXT, dest_id TEXT, park_id TEXT, land_id TEXT, entertainment_venue_id TEXT, coordinates TEXT)")

        conn.commit()
        conn.close()

    def create_parks_table(self):
        conn = sqlite3.connect(self.DB_NAME)
        c = conn.cursor()

        c.execute("CREATE TABLE IF NOT EXISTS parks (id TEXT PRIMARY KEY, name TEXT, entityType TEXT, last_pull TEXT, operating_open TEXT, operating_close TEXT, extra_magic_open TEXT, extra_magic_close TEXT, status TEXT, dest_id TEXT, coordinates TEXT)")

        conn.commit()
        conn.close()

    def create_schedules_table(self):
        conn = sqlite3.connect(self.DB_NAME)
        c = conn.cursor()

        c.execute("CREATE TABLE IF NOT EXISTS schedules (id TEXT PRIMARY KEY, name TEXT, entityType TEXT, subType TEXT, last_pull TEXT, schedule TEXT, dest_id TEXT, park_id TEXT, land_id TEXT, entertainment_venue_id TEXT, primary_location_id TEXT, coordinates TEXT)")

        conn.commit()
        conn.close()

    def create_weather_table(self):
        conn = sqlite3.connect(self.DB_NAME)
        c = conn.cursor()

        c.execute("CREATE TABLE IF NOT EXISTS weather_orlando (last_pull TEXT PRIMARY KEY, weather TEXT, weather_main TEXT, weather_decription TEXT, temp TEXT, feels_like TEXT)")
        c.execute("CREATE TABLE IF NOT EXISTS weather_anaheim (last_pull TEXT PRIMARY KEY, weather TEXT, weather_main TEXT, weather_decription TEXT, temp TEXT, feels_like TEXT)")

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
                park_id, land_id, ev_id, entityType, doc_id = c_mt.execute("SELECT park_id, land_id, entertainment_venue_id, entityType, doc_id FROM facilities WHERE id = ?", (id,)).fetchone()
                facility_body = json.loads(c_mt.execute("SELECT body FROM sync WHERE id = ?", (doc_id,)).fetchone()[0])
                coordinates = {'latitude': facility_body['latitude'], 'longitude': facility_body['longitude']}
                self.c.execute("INSERT OR REPLACE INTO details (id, name, entityType, last_pull, last_updated, wait_time, status, dest_id, park_id, land_id, entertainment_venue_id, coordinates) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (id, body['name'], entityType, current_timestamp, body["last_updated"].timestamp(), body["wait_time"], body["status"], dest.get_id(), park_id, land_id, ev_id, json.dumps(coordinates),))

        orlando_weather = requests.get("https://api.openweathermap.org/data/2.5/weather?lat=28.388195&lon=-81.569324&units=imperial&appid={}".format(weather_key)).json()
        anaheim_weather = requests.get("https://api.openweathermap.org/data/2.5/weather?lat=33.808666&lon=-117.918955&units=imperial&appid={}".format(weather_key)).json()
        self.c.execute("INSERT INTO weather_orlando (last_pull, weather, weather_main, weather_decription, temp, feels_like) VALUES (?, ?, ?, ?, ?, ?)", (current_timestamp, json.dumps(orlando_weather), orlando_weather['weather'][0]['main'], orlando_weather['weather'][0]['description'], orlando_weather['main']['temp'], orlando_weather['main']['feels_like'],))
        self.c.execute("INSERT INTO weather_anaheim (last_pull, weather, weather_main, weather_decription, temp, feels_like) VALUES (?, ?, ?, ?, ?, ?)", (current_timestamp, json.dumps(anaheim_weather), anaheim_weather['weather'][0]['main'], anaheim_weather['weather'][0]['description'], anaheim_weather['main']['temp'], anaheim_weather['main']['feels_like'],))

        conn.commit()
        conn.close()
        conn_mt.commit()
        conn_mt.close()

        print("Update waits successful, time: " + str(datetime.now()))

    def update_park_hours(self):

        conn = sqlite3.connect(self.DB_NAME)
        c = conn.cursor()

        parks = self.dests[0].get_park_ids() + self.dests[1].get_park_ids()
        for id in parks:
            c.execute("CREATE TABLE IF NOT EXISTS park_{} (date TEXT PRIMARY KEY, operating_open TEXT, operating_close TEXT, extra_magic_open TEXT, extra_magic_close TEXT, status TEXT)".format(id))

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
            c.execute("INSERT OR REPLACE INTO parks (id, name, entityType, last_pull, operating_open, operating_close, extra_magic_open, extra_magic_close, status, dest_id, coordinates) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (id, park.get_name(), park.get_entityType(), self.today, operating_open, operating_close, extra_magic_open, extra_magic_close, park.get_status(), park.get_ancestor_destination_id(), json.dumps(park.get_coordinates()),))

        evs = self.dests[0].get_entertainment_venue_ids() + self.dests[1].get_entertainment_venue_ids()
        for id in evs:
            c.execute("CREATE TABLE IF NOT EXISTS park_{} (date TEXT PRIMARY KEY, operating_open TEXT, operating_close TEXT, extra_magic_open TEXT, extra_magic_close TEXT, status TEXT)".format(id))

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
            c.execute("INSERT OR REPLACE INTO parks (id, name, entityType, last_pull, operating_open, operating_close, extra_magic_open, extra_magic_close, status, dest_id, coordinates) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (id, ev.get_name(), ev.get_entityType(), self.today, operating_open, operating_close, extra_magic_open, extra_magic_close, ev.get_status(), ev.get_ancestor_destination_id(), json.dumps(ev.get_coordinates()),))

        conn.commit()
        conn.close()

        print("Update hours successful, time: " + str(datetime.now()))

    def update_entertainment_schedules(self):

        conn = sqlite3.connect(self.DB_NAME)
        c = conn.cursor()

        entertainments = MouseTools.ids.WDW_ENTERTAINMENT_IDS + MouseTools.ids.DLR_ENTERTAINMENT_IDS

        for id in entertainments:
            try:
                schedule = self.get_schedule(id)
                if schedule != []:
                    enter = MouseTools.Entertainment(id)
                    c.execute("CREATE TABLE IF NOT EXISTS schedule_{} (date TEXT PRIMARY KEY, schedule TEXT, duration TEXT)".format(id))
                    c.execute("INSERT INTO schedule_{} (date, schedule, duration) VALUES (?, ?, ?)".format(id), (self.today, json.dumps(schedule), enter.get_duration_seconds(),))
                    c.execute("INSERT OR REPLACE INTO schedules (id, name, entityType, subType, last_pull, schedule, dest_id, park_id, land_id, entertainment_venue_id, primary_location_id, coordinates) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (id, enter.get_name(), enter.get_entityType(), enter.get_subType(), self.today, json.dumps(schedule), enter.get_ancestor_destination_id(), enter.get_ancestor_park_id(), enter.get_ancestor_land_id(), enter.get_ancestor_entertainment_venue_id(), json.dumps(enter.get_related_location_ids()), json.dumps(enter.get_coordinates()),))
            except Exception as e:
                pass
                print(e)
                # entertainments.extend(id)
        conn.commit()
        conn.close()

        print("Update schedule successful, time: " + str(datetime.now()))

    def get_schedule(self, id, date=""):
        """
        Returns a list of dictionaries of datetime objects for the specified date's schedule in the form of [{start_time, end_time}]
        date = "YYYY-MM-DD"
        If you don't pass a date, it will get today's schedule
        """

        if date == "":
            DATE = datetime.today()
        else:
            year, month, day = date.split('-')
            DATE = datetime(int(year), int(month), int(day))

        strdate = "{}-{}-{}".format(DATE.year, self.__formatDate(str(DATE.month)), self.__formatDate(str(DATE.day)))
        data = requests.get("https://api.wdpro.disney.go.com/facility-service/schedules/{}?date={}".format(id, strdate), headers=MouseTools.auth.getHeaders()).json()

        schedule = []

        try:
            for entry in data['schedules']:
                if entry['type'] == 'Performance Time':
                    this = {}
                    this['start_time'] = datetime.strptime("{} {}".format(entry['date'], entry['startTime']), "%Y-%m-%d %H:%M:%S").timestamp()
                    this['end_time'] = datetime.strptime("{} {}".format(entry['date'], entry['endTime']), "%Y-%m-%d %H:%M:%S").timestamp()
                    schedule.append(this)
        except Exception as e:
            # print(e)
            pass

        return schedule

    def __formatDate(self, num):
        """
        Formats month and day into proper format
        """
        if len(num) < 2:
            num = '0'+num
        return num

if __name__ == '__main__':

    waits_obj = Waits()
