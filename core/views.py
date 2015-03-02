from django.http import HttpResponse, JsonResponse
from core.models import *
from django.shortcuts import get_object_or_404, render_to_response, redirect
from django.core.exceptions import ObjectDoesNotExist
from django.template import RequestContext
from django import forms


from django.utils import timezone


def index(request):
    data = {'projectName': 'placeholder',
            'successMessage': "Great success!"}
    return render_to_response("index.html", data, context_instance=RequestContext(request))


###################
##### HELPERS #####
###################

def addRoom(name):
    try:
        return Room.objects.get(name=name)
    except ObjectDoesNotExist:
        new_room = Room.objects.create(name=name)
        new_room.save()
        return new_room


def getAllRooms():
    return Room.objects.all()


def addStation(name, room, pollingFrequency=None):
    try:
        station = Station.objects.get(name=name)
        station.room = room
        station.pollingFrequency = pollingFrequency
        station.save()
        return station
    except ObjectDoesNotExist:
        new_station = Station.objects.create(name=name,
                                             room=room,
                                             pollingFrequency=pollingFrequency)
        new_station.save()
        return new_station


def getAllStations():
    return Station.objects.all()


def updateStation(name, room, pollingFrequency=None):
    try:
        station = Station.objects.get(name=name)
        station.room = room
        station.pollingFrequency = pollingFrequency
        station.save()
        return station
    except ObjectDoesNotExist:
        print "%s station does not exist" % name


def addItem(name, beaconId):
    try:
        item = Item.objects.get(name=name)
        item.beaconId = beaconId
        item.save()
        return item
    except ObjectDoesNotExist:
        new_item = Item.objects.create(name=name,
                                       beaconId=beaconId,
                                       activationTime=timezone.now())
        new_item.save()
        return new_item


def updateItemsRoom(name, room):
    try:
        item = Item.objects.get(name=name)
        item.room = room
        item.save()
        return item
    except ObjectDoesNotExist:
        print "%s item doesn't exist" % name


def getAllItems():
    return Item.objects.all()


def getAllItemsInRoom(room):
    return room.item.objects.all()


def addDistance(item, station, dist):
    try:
        distance = Distance.objects.get(item=item, station=station)
        distance.dist = dist
        distance.save()
        return distance
    except ObjectDoesNotExist:
        new_distance = Distance.objects.create(item=item,
                                               station=station,
                                               dist=dist)
        new_distance.save()
        return new_distance


def findItemsRoom(itemName):
    # Find the closest station's room
    try:
        item = Item.objects.get(name=itemName)
        distances = Distance.objects.filter(item=item)
        orderedDistances = distances.order_by('dist')
        if len(orderedDistances) == 0:
            print "No distance recorder for item %s" % item.name
        else:
            closestStation = orderedDistances[0].station
            return closestStation.room
    except ObjectDoesNotExist:
        print "Item %s doesn't exist" % itemName

def pollStations():
    stations = getAllStations()
    for station in stations:
        items = getAllItemsInRoom(station.room)
        for item in items:
            updateItemsRoom(item.name, station.room)
    return False

