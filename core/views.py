from django.http import HttpResponse, JsonResponse
from core.models import *
from django.shortcuts import get_object_or_404, render_to_response, redirect
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from requests.exceptions import ConnectionError
from django.db import transaction
from django.template import RequestContext
from datetime import datetime, timedelta
import requests
import json


STATION_PORT = '8001'
SET_STATION_ID_ROUTE = 'set-id'
BROADCAST_UUID_ROUTE = 'broadcast-uuid'
TIMEOUT_PERIOD = 30


def index(request):
    data = {}
    stations = getRegisteredStations()
    items = getRegisteredItems()
    expireTime = timezone.now() - timedelta(seconds=TIMEOUT_PERIOD)
    data["rooms"] = getAllRooms()
    data["active_stations"] = stations.filter(lastUpdate__gte=expireTime)
    data["inactive_stations"] = stations.filter(lastUpdate__lt=expireTime)
    data["active_items"] = items.filter(lastUpdate__gte=expireTime)
    data["inactive_items"] = items.filter(lastUpdate__lt=expireTime)
    data["pollingFrequency"] = getPollingFreq()
    return render_to_response("index.html", data,
                              context_instance=RequestContext(request))


def loadUnregistered(request):
    if request.method == "POST":
        response = {}
        unregisteredStations = createStationsArray(getUnregisteredStations())
        unregisteredItems = createItemsArray(getUnregisteredItems())
        registeredItems = createItemsArray(getRegisteredItems())
        response["unregisteredIpAddresses"] = unregisteredStations
        response["unregisteredBeaconIds"] = unregisteredItems
        response["registeredBeaconIds"] = registeredItems
        return HttpResponse(json.dumps(response),
                            content_type="application-json")


@transaction.atomic
def newData(request):
    if request.method == "POST":
        ipAddress = getIpAddress(request)
        print "Request from ipAddress: " + ipAddress
        if "id" in request.POST:
            try:
                station = Station.objects.get(id=int(request.POST["id"]))
                if station.ipAddress != ipAddress:
                    station.ipAddress = ipAddress
                    station.save()
            except ObjectDoesNotExist:
                station = addStation(ipAddress)
        else:
            station = addStation(ipAddress)

        clearDistances()
        data = request.POST["data"]
        dataDict = json.loads(data)
        for beaconId in dataDict.keys():
            item = addItem(beaconId)
            distance = int(dataDict[beaconId])
            addDistance(item, station, distance)
            item.room = findItemsRoom(beaconId)
            item.save()

    return HttpResponse("")


def addRoomView(request):
    response = {}
    if request.method == "POST":
        roomName = request.POST["name"]
        addRoom(roomName)
        return HttpResponse(json.dumps(response),
                            content_type="application-json")


def addStationView(request):
    response = {}
    if request.method == "POST":
        stationName = request.POST["name"]
        stationIP = request.POST["ip"]
        roomName = request.POST["room"]
        room = Room.objects.get(name=roomName)
        station = addStation(stationIP)
        registerStation(stationIP, stationName, room)
        sendIdToStation(station)
        return HttpResponse(json.dumps(response),
                            content_type="application-json")


def addItemView(request):
    response = {}
    if request.method == "POST":
        itemBeaconId = request.POST["beaconId"]
        itemName = request.POST["name"]
        item = addItem(itemBeaconId)
        registerItem(itemBeaconId, itemName)
        if item.room:
            response["room"] = item.room.name
        else:
            response["room"] = "unknown"
        return HttpResponse(json.dumps(response),
                            content_type="application-json")


def getStationsForRoomView(request):
    response = {}
    if request.method == "POST":
        roomName = request.POST["name"]
        try:
            room = Room.objects.get(name=roomName)
            stations = room.station_set.all()
            response["result"] = 1
            response["stations"] = createStationsArray(stations)
        except ObjectDoesNotExist:
            response["result"] = 0
        return HttpResponse(json.dumps(response),
                            content_type="application-json")


def updatePollingFreq(request):
    response = {}
    if request.method == "GET":
        return index(request)
    if request.method == "POST":
        newPollFreq = request.POST["pollFreq"]
    stations = getRegisteredStations()
    for station in stations:
        updateStation(station.name, station.room, newPollFreq)
    response["pollingFrequency"] = newPollFreq
    return HttpResponse(json.dumps(response),
                        content_type="application-json")


def broadcastSearchingBeacon(request):
    response = {}
    if request.method == "POST":
        uuid = request.POST["uuid"]
        data = {"uuid": uuid}
        stations = getAllStations()
        for station in stations:
            try:
                reqURL = "http://%s:%s/%s" % (station.ipAddress,
                                              STATION_PORT,
                                              BROADCAST_UUID_ROUTE)
                requests.post(reqURL, data=data)
            except ConnectionError:
                print "Couldn't broadcast to " + station.ipAddress

        return HttpResponse(json.dumps(response),
                            content_type="application-json")


###################
##### HELPERS #####
###################


# Delete distances for inactive stations and items
def clearDistances():
    expireTime = timezone.now() - timedelta(seconds=TIMEOUT_PERIOD)
    inactiveStations = Station.objects.filter(lastUpdate__lt=expireTime)
    inactiveItems = Item.objects.filter(lastUpdate__lt=expireTime)
    for station in inactiveStations:
        Distance.objects.filter(station=station).delete()
    for item in inactiveItems:
        Distance.objects.filter(item=item).delete()
    return


def sendIdToStation(station):
    reqURL = "http://%s:%s/%s" % (station.ipAddress,
                                  STATION_PORT, SET_STATION_ID_ROUTE)
    post = {"data": json.dumps({"id": str(station.id)})}
    try:
        requests.post(reqURL, data=post)
    except ConnectionError:
        print "Couldn't send id to " + station.ipAddress
    return


def getIpAddress(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def createStationsArray(stations):
    arr = []
    for station in stations:
        arr.append({"ipAddress": station.ipAddress,
                    "id": station.id})
    return sorted(arr, key=lambda station: station["ipAddress"])


def createItemsArray(items):
    arr = []
    for item in items:
        if item.room:
            arr.append({"beaconId": item.beaconId, "room": item.room.name, "name": item.name})
        else:
            arr.append({"beaconId": item.beaconId, "room": "undefined", "name": item.name})
    return sorted(arr, key=lambda item: item["beaconId"])


def addRoom(name):
    try:
        return Room.objects.get(name=name)
    except ObjectDoesNotExist:
        new_room = Room.objects.create(name=name)
        new_room.save()
        return new_room


def getAllRooms():
    return Room.objects.all()


@transaction.atomic
def addStation(ipAddress):
    try:
        station = Station.objects.get(ipAddress=ipAddress)
        station.save()
    except ObjectDoesNotExist:
        station = Station.objects.create(ipAddress=ipAddress)
        station.save()
    return station


def registerStation(ipAddress, name, room, pollingFrequency=None):
    try:
        station = Station.objects.get(ipAddress=ipAddress)
        station.registered = True
        station.name = name
        station.room = room
        station.save()
    except ObjectDoesNotExist:
        print "Register Error: Station %s does not exist" % ipAddress


def unregisterItem(request):
  response = {}
  if request.method == "GET":
    return index(request)
  if request.method == 'POST':
    uuid = request.POST['uuid']
    data = {'uuid': uuid}
    item = Item.objects.get(beaconId=uuid)
    item.registered = False
    item.save()
  return HttpResponse(json.dumps(response), content_type="application-json")

def unregisterStation(request):
  response = {}
  if request.method == "GET":
    return index(request)
  if request.method == 'POST':
    ipAddress = request.POST['ipAddress']
    data = {'ipAddress': ipAddress}
    station = Station.objects.get(ipAddress=ipAddress)
    station.registered = False
    station.save()
  return HttpResponse(json.dumps(response), content_type="application-json")

def getAllStations():
    return Station.objects.all()


def getRegisteredStations():
    return Station.objects.filter(registered=True)


def getUnregisteredStations():
    expireTime = timezone.now() - timedelta(seconds=TIMEOUT_PERIOD)
    return Station.objects.filter(registered=False) \
                          .filter(lastUpdate__gte=expireTime)


def updateStation(name, room, pollingFrequency=None):
    try:
        station = Station.objects.get(name=name)
        station.room = room
        station.pollingFrequency = pollingFrequency
        station.save()
        return station
    except ObjectDoesNotExist:
        print "%s station does not exist" % name


def addItem(beaconId):
    try:
        return Item.objects.get(beaconId=beaconId)
    except ObjectDoesNotExist:
        return Item.objects.create(beaconId=beaconId,
                                   activationTime=timezone.now())


def registerItem(beaconId, name):
    try:
        item = Item.objects.get(beaconId=beaconId)
        item.registered = True
        item.name = name
        item.save()
    except ObjectDoesNotExist:
        print "Register Error: Item %s does not exist" % beaconId


def getRegisteredItems():
    return Item.objects.filter(registered=True)


def getUnregisteredItems():
    expireTime = timezone.now() - timedelta(seconds=TIMEOUT_PERIOD)
    return Item.objects.filter(registered=False) \
                       .filter(lastUpdate__gte=expireTime)


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


def findItemsRoom(beaconId):
    # Find the closest station's room
    try:
        item = Item.objects.get(beaconId=beaconId)
        distances = Distance.objects.filter(item=item)
        orderedDistances = distances.order_by('-dist')
        if len(orderedDistances) == 0:
            print "No distance recorder for item %s" % item.name
        else:
            closestStation = orderedDistances[0].station
            return closestStation.room
    except ObjectDoesNotExist:
        print "Item %s doesn't exist" % beaconId


def getInfoFromStations():
    stations = getAllStations()
    for station in stations:
        items = getAllItemsInRoom(station.room)
        for item in items:
            updateItemsRoom(item.name, station.room)
    return False


# poll stations with get request then parse response
# response comes in as JSON
def pollStations():
    stations = getAllStations()
    for station in stations:
        res = requests.get(station.ipAddress)
        # TODO parse JSON response
        for item in res:
            updateItemsRoom(item.name, station.room)
    return True


def getPollingFreq():
    stations = getRegisteredStations()
    if len(stations) > 0:
        return stations[0].pollingFrequency
    else:
        return 5
