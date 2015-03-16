from django.db import models
from django import forms


class Room(models.Model):
    name = models.CharField(max_length=200)

    def __unicode__(self):
        return self.name

    class Meta:
        db_table = "room"


class Item(models.Model):
    beaconId = models.CharField(max_length=200, primary_key=True)
    registered = models.BooleanField(default=False)
    name = models.CharField(max_length=200, null=True)
    room = models.ForeignKey(Room, null=True)
    activationTime = models.DateTimeField(null=True)

    def __unicode__(self):
        return self.beaconId

    class Meta:
        db_table = "item"


class Station(models.Model):
    ipAddress = models.CharField(max_length=200)
    registered = models.BooleanField(default=False)
    name = models.CharField(max_length=200)
    room = models.ForeignKey(Room, null=True)
    pollingFrequency = models.CharField(max_length=200, null=True)

    def __unicode__(self):
        return self.ipAddress

    class Meta:
        db_table = "station"


class Distance(models.Model):
    item = models.ForeignKey(Item)
    station = models.ForeignKey(Station)
    dist = models.IntegerField()

    def __unicode__(self):
        return "(%s, st%s, %d)" % (self.item.beaconId, self.station.ipAddress, self.dist)

    class Meta:
        db_table = "distance"
