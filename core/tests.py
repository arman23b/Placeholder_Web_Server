from django.test import TestCase
from core.models import *
from core.views import *


class RoomTestCase(TestCase):

    def setUp(self):
        addRoom("Living Room")
        addRoom("Bedroom")
        addRoom("Bathroom")
        addRoom("Kitchen")

    def test_addRoom(self):
        addRoom("Kitchen")
        self.assertEqual(len(getAllRooms()), 4)


class StationTestCase(TestCase):

    def setUp(self):
        room = addRoom("Bedroom")
        addStation("Station #1", room)

    def test_addStation(self):
        addStation("Station #1", addRoom("Bathroom"))
        self.assertEqual(len(getAllStations()), 1)

    def test_updateStation(self):
        room = addRoom("Living Room")
        station = updateStation("Station #1", room, "300")
        self.assertEqual(station.room.name, "Living Room")
        self.assertEqual(station.pollingFrequency, "300")


class ItemTestCase(TestCase):

    def setUp(self):
        addItem("Phone", "beacon1")
        addItem("Car keys", "beacon2")
        addItem("Tablet", "beacon3")

    def test_addItem(self):
        addItem("Phone", "beacon4")
        self.assertEqual(len(getAllItems()), 3)

    def test_updateItemsRoom(self):
        item = updateItemsRoom("Phone", addRoom("Bedroom"))
        self.assertEqual(item.room.name, "Bedroom")
        item = updateItemsRoom("Phone", addRoom("Bathroom"))
        self.assertEqual(item.room.name, "Bathroom")

    def test_getAllItemsInRoom(self):
        room = addRoom("Bedroom")
        updateItemsRoom("Phone", room)
        updateItemsRoom("Car keys", room)
        updateItemsRoom("Tablet", room)
        self.assertEqual(len(getAllItemsInRoom(room)), 3)


class DistanceTestCase(TestCase):

    def setUp(self):
        phone = addItem("Phone", "beacon1")
        station1 = addStation("Station #1", addRoom("Bedroom"))
        station2 = addStation("Station #2", addRoom("Bathroom"))
        station3 = addStation("Station #3", addRoom("Kitchen"))
        addDistance(phone, station1, 300)
        addDistance(phone, station2, 200)
        addDistance(phone, station3, 100)

    def test_findItemsRoom(self):
        self.assertEqual(findItemsRoom("Phone").name, "Kitchen")
        
        phone = addItem("Phone", "beacon1")
        station1 = addStation("Station #1", addRoom("Bedroom"))
        addDistance(phone, station1, 400)
        self.assertEqual(findItemsRoom("Phone").name, "Kitchen")

        addDistance(phone, station1, 50)
        self.assertEqual(findItemsRoom("Phone").name, "Bedroom")

        station2 = addStation("Station #2", addRoom("Bathroom"))
        addDistance(phone, station2, 10)
        self.assertEqual(findItemsRoom("Phone").name, "Bathroom")