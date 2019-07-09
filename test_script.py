from MouseTools.parks import Park
from MouseTools.attractions import Attraction
from MouseTools.entertainments import Entertainment
from MouseTools.characters import Character
from MouseTools.facilities import Facility
from MouseTools.pointsofinterest import PointOfInterest
from MouseTools.destinations import Destination
from tqdm import tqdm
import json
import requests
import pydoc
import sys

#test type of returned items for better accuracy

def test_destinations():
    destination_ids = requests.get("https://scaratozzolo.github.io/MouseTools/destination_ids.json").json()
    failed = {}
    for dest in tqdm(destination_ids):
        fails = []
        try:
            destobj = Destination(destination_ids[dest])

            try:
                name = destobj.getName()
                if type(name) != str:
                    fails.append("getName")
            except:
                fails.append("getName")

            try:
                id = destobj.getID()
                if type(id) != str:
                    fails.append("getID")
            except:
                fails.append("getID")

            try:
                destype = destobj.getType()
                if type(destype) != str:
                    fails.append("getType")
            except:
                fails.append("getType")

            try:
                themes = destobj.getThemeParks()
                if type(themes) != list:
                    fails.append("getThemeParks")
            except:
                fails.append("getThemeParks")

            try:
                themesid = destobj.getThemeParkIDs()
                if type(themesid) != list:
                    fails.append("getThemeParkIDs")
            except:
                fails.append("getThemeParkIDs")

            try:
                waters = destobj.getWaterParks()
                if type(waters) != list:
                    fails.append("getWaterParks")
            except:
                fails.append("getWaterParks")

            try:
                watersid = destobj.getWaterParkIDs()
                if type(watersid) != list:
                    fails.append("getWaterParkIDs")
            except:
                fails.append("getWaterParkIDs")

            try:
                enters = destobj.getEntertainments()
                if type(enters) != list:
                    fails.append("getEntertainments")
            except:
                fails.append("getEntertainments")

            try:
                entersid = destobj.getEntertainmentIDs()
                if type(entersid) != list:
                    fails.append("getEntertainmentIDs")
            except:
                fails.append("getEntertainmentIDs")

            try:
                attrs = destobj.getAttractions()
                if type(attrs) != list:
                    fails.append("getAttractions")
            except:
                fails.append("getAttractions")

            try:
                attrsid = destobj.getAttractionIDs()
                if type(attrsid) != list:
                    fails.append("getAttractionIDs")
            except:
                fails.append("getAttractionIDs")

            failed[dest] = fails
        except:
            print("Destination ID {} for {} not valid".format(destination_ids[dest], dest))
    print(failed)

def test_parks():
    park_ids = requests.get("https://scaratozzolo.github.io/MouseTools/park_ids.json").json()
    failed = {}
    for park in tqdm(park_ids):
        fails = []
        try:
            parkobj = Park(park_ids[park])

            try:
                parkobj.getParkID()
            except:
                fails.append("getParkID")

            try:
                parkobj.getParkName()
            except:
                fails.append("getParkName")

            try:
                parkobj.getTodayParkHours()
            except:
                fails.append("getTodayParkHours")

            try:
                parkobj.getParkHours(2018, 5, 31)
            except:
                fails.append("getParkHours")

            try:
                parkobj.getParkAdvisories()
            except:
                fails.append("getParkAdvisories")

            try:
                parkobj.getAttractionIDs()
            except:
                fails.append("getAttractionIDs")

            try:
                parkobj.getAttractions()
            except:
                fails.append("getAttractions")

            try:
                parkobj.getCurrentWaitTimes()
            except:
                fails.append("getCurrentWaitTimes")

            try:
                parkobj.getAncestorResortArea()
            except:
                fails.append("getAncestorResortArea")

            failed[park] = fails
        except:
            print("Park ID {} for {} not valid".format(park_ids[park], park))
    print(failed)

def test_attractions():
    attr_ids = requests.get("https://scaratozzolo.github.io/MouseTools/attraction_ids.json").json()
    failed = {}
    for attr in tqdm(attr_ids):
        fails = []
        try:
            attrobj = Attraction(attr_ids[attr])

            try:
                attrobj.getAttractionName()
            except:
                fails.append("getAttractionName")

            try:
                attrobj.getAttractionID()
            except:
                fails.append("getAttractionID")

            try:
                attrobj.getType()
            except:
                fails.append("getType")

            try:
                attrobj.getAttractionCoordinates()
            except:
                fails.append("getAttractionCoordinates")

            try:
                attrobj.getAncestorDestination()
            except:
                fails.append("getAncestorDestination")

            try:
                attrobj.getAncestorThemeParkID()
            except:
                fails.append("getAncestorThemeParkID")

            try:
                attrobj.getAncestorThemePark()
            except:
                fails.append("getAncestorThemePark")

            try:
                attrobj.getAncestorWaterParkID()
            except:
                fails.append("getAncestorWaterParkID")

            try:
                attrobj.getAncestorWaterPark()
            except:
                fails.append("getAncestorWaterPark")

            try:
                attrobj.getAncestorResortArea()
            except:
                fails.append("getAncestorResortArea")

            try:
                attrobj.getAncestorLand()
            except:
                fails.append("getAncestorLand")

            try:
                attrobj.getTodayAttractionHours()
            except:
                fails.append("getTodayAttractionHours")

            try:
                attrobj.getAttractionHours(2018,5,31)
            except:
                fails.append("getAttractionHours")

            try:
                attrobj.checkForAttractionWaitTime()
            except:
                fails.append("checkForAttractionWaitTime")

            try:
                attrobj.getAttractionStatus()
            except:
                fails.append("getAttractionStatus")

            try:
                attrobj.getAttractionWaitTime()
            except:
                fails.append("getAttractionWaitTime")

            try:
                attrobj.getAttractionWaitTimeFromData()
            except:
                fails.append("getAttractionWaitTimeFromData")

            try:
                attrobj.getAttractionWaitTimeMessage()
            except:
                fails.append("getAttractionWaitTimeMessage")

            try:
                attrobj.getAttractionFastPassAvailable()
            except:
                fails.append("getAttractionFastPassAvailable")

            try:
                attrobj.checkAssociatedCharacters()
            except:
                fails.append("checkAssociatedCharacters")

            try:
                attrobj.getNumberAssociatedCharacters()
            except:
                fails.append("getNumberAssociatedCharacters")

            try:
                attrobj.getAssociatedCharacters()
            except:
                fails.append("getAssociatedCharacters")

            try:
                attrobj.getAssociatedCharacterIDs()
            except:
                fails.append("getAssociatedCharacterIDs")

            failed[attr] = fails
        except:
            print("Attraction ID {} for {} not valid".format(attr_ids[attr], attr))
    print(failed)

def test_entertainments():
    enter_ids = requests.get("https://scaratozzolo.github.io/MouseTools/entertainment_ids.json").json()
    failed = {}
    for enter in tqdm(enter_ids):
        fails = []
        try:
            enterobj = Entertainment(enter_ids[enter])

            try:
                enterobj.getEntertainmentName()
            except:
                fails.append("getEntertainmentName")

            try:
                enterobj.getEntertainmentID()
            except:
                fails.append("getEntertainmentID")

            try:
                enterobj.getEntertainmentSubType()
            except:
                fails.append("getEntertainmentSubType")

            try:
                enterobj.getEntertainmentCoordinates()
            except:
                fails.append("getEntertainmentCoordinates")

            try:
                enterobj.checkAssociatedCharacters()
            except:
                fails.append("checkAssociatedCharacters")

            try:
                enterobj.getNumberAssociatedCharacters()
            except:
                fails.append("getNumberAssociatedCharacters")

            try:
                enterobj.getAssociatedCharacters()
            except:
                fails.append("getAssociatedCharacters")

            try:
                enterobj.getEntertainmentStatus()
            except:
                fails.append("getEntertainmentStatus")

            try:
                attrobj.checkForEntertainmentWaitTime()
            except:
                fails.append("checkForEntertainmentWaitTime")

            try:
                enterobj.getEntertainmentWaitTime()
            except:
                fails.append("getEntertainmentWaitTime")

            try:
                enterobj.getEntertainmentWaitTimeFromData()
            except:
                fails.append("getEntertainmentWaitTimeFromData")

            try:
                enterobj.getEntertainmentWaitTimeMessage()
            except:
                fails.append("getEntertainmentWaitTimeMessage")

            try:
                enterobj.getStartDate()
            except:
                fails.append("getStartDate")

            try:
                enterobj.getEndDate()
            except:
                fails.append("getEndDate")

            try:
                enterobj.getDuration()
            except:
                fails.append("getDuration")

            try:
                enterobj.getDurationMinutes()
            except:
                fails.append("getDurationMinutes")

            try:
                enterobj.getDurationSeconds()
            except:
                fails.append("getDurationSeconds")

            try:
                enterobj.getEntertainmentFastPassAvailable()
            except:
                fails.append("getEntertainmentFastPassAvailable")

            try:
                enterobj.getEntertainmentFastPassPlusAvailable()
            except:
                fails.append("getEntertainmentFastPassPlusAvailable")

            try:
                enterobj.checkRelatedLocations()
            except:
                fails.append("checkRelatedLocations")

            try:
                enterobj.getRelatedLocations()
            except:
                fails.append("getRelatedLocations")

            try:
                enterobj.getAncestorDestination()
            except:
                fails.append("getAncestorDestination")

            try:
                enterobj.getAncestorDestinationID()
            except:
                fails.append("getAncestorDestinationID")

            try:
                enterobj.getAncestorResortArea()
            except:
                fails.append("getAncestorResortArea")

            try:
                enterobj.getAncestorResortAreaID()
            except:
                fails.append("getAncestorResortAreaID")

            try:
                enterobj.getAncestorThemePark()
            except:
                fails.append("getAncestorThemePark")

            try:
                enterobj.getAncestorThemeParkID()
            except:
                fails.append("getAncestorThemeParkID")

            try:
                enterobj.getAncestorWaterPark()
            except:
                fails.append("getAncestorWaterPark")

            try:
                enterobj.getAncestorWaterParkID()
            except:
                fails.append("getAncestorWaterParkID")

            try:
                enterobj.getAncestorLandID()
            except:
                fails.append("getAncestorLand")

            try:
                enterobj.getAncestorLandID()
            except:
                fails.append("getAncestorLand")

            failed[enter] = fails
        except:
            print("Entertainment ID {} for {} not valid".format(enter_ids[enter], enter))
    print(failed)

def test_facilities():
    fac_ids = requests.get("https://scaratozzolo.github.io/MouseTools/facility_ids.json").json()
    failed = {}
    for fac in tqdm(fac_ids):
        fails = []
        try:
            facobj = Facility(fac_ids[fac])

            try:
                facobj.getFacilityName()
            except:
                fails.append("getFacilityName")

            try:
                facobj.getFacilityID()
            except:
                fails.append("getFacilityID")

            try:
                facobj.getFacilitySubType()
            except:
                fails.append("getFacilitySubType")

            try:
                facobj.getAncestorResortArea()
            except:
                fails.append("getAncestorResortArea")

            try:
                facobj.getAncestorThemePark()
            except:
                fails.append("getAncestorThemePark")

            try:
                facobj.getAncestorLand()
            except:
                fails.append("getAncestorLand")

            try:
                facobj.getAncestorDestination()
            except:
                fails.append("getAncestorDestination")

            failed[fac] = fails
        except:
            print("Facility ID {} for {} not valid".format(fac_ids[fac], fac))
    print(failed)

def test_pointsofinterest():
    poi_ids = requests.get("https://scaratozzolo.github.io/MouseTools/pointofinterest_ids.json").json()
    failed = {}
    for poi in tqdm(poi_ids):
        fails = []
        try:
            poiobj = PointOfInterest(poi_ids[poi])

            try:
                poiobj.getPointOfInterestName()
            except:
                fails.append("getPointOfInterestName")

            try:
                poiobj.getPointOfInterestID()
            except:
                fails.append("getPointOfInterestID")

            try:
                poiobj.getPointOfInterestCoordinates()
            except:
                fails.append("getPointOfInterestCoordinates")

            try:
                poiobj.getAncestorDestination()
            except:
                fails.append("getAncestorDestination")

            try:
                poiobj.getAncestorResortArea()
            except:
                fails.append("getAncestorResortArea")

            try:
                poiobj.getAncestorThemePark()
            except:
                fails.append("getAncestorThemePark")

            try:
                poiobj.getAncestorLand()
            except:
                fails.append("getAncestorLand")

            failed[poi] = fails
        except:
            print("Point of Interest ID {} for {} not valid".format(poi_ids[poi], poi))
    print(failed)

def test_characters():
    char_ids = requests.get("https://scaratozzolo.github.io/MouseTools/character_ids.json").json()
    failed = {}
    for char in tqdm(char_ids):
        fails = []
        try:
            charobj = Character(char_ids[char])

            try:
                charobj.getCharacterName()
            except:
                fails.append("getCharacterName")

            try:
                charobj.getCharacterID()
            except:
                fails.append("getCharacterID")

            try:
                charobj.checkRelatedLocations()
            except:
                fails.append("checkRelatedLocations")

            try:
                charobj.getRelatedLocations()
            except:
                fails.append("getRelatedLocations")

            try:
                charobj.getAssociatedEvents()
            except:
                fails.append("getAssociatedEvents")

            failed[char] = fails
        except:
            print("Character ID {} for {} not valid".format(char_ids[char], char))
    print(failed)

if __name__ == "__main__":
    # test_destinations()
    # test_parks()
    # test_attractions()
    # test_entertainments()
    # test_facilities()
    # test_pointsofinterest()
    test_characters()
