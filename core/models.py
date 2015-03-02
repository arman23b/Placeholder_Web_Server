from django.db import models
from django import forms


class Room(models.Model):
    name = models.CharField(max_length=200)

    def __unicode__(self):
        return self.name

    class Meta:
        db_table = "room"


class Item(models.Model):
    name = models.CharField(max_length=200)
    beaconId = models.CharField(max_length=200)
    room = models.ForeignKey(Room, null=True)
    activationTime = models.DateTimeField(null=True)

    def __unicode__(self):
        return self.name

    class Meta:
        db_table = "item"


class Station(models.Model):
    name = models.CharField(max_length=200)
    room = models.ForeignKey(Room, null=True)
    pollingFrequency = models.CharField(max_length=200, null=True)
    ipAddress = models.CharField(max_length=200, default="0.0.0.0")

    def __unicode__(self):
        return self.name

    class Meta:
        db_table = "station"


class Distance(models.Model):
    item = models.ForeignKey(Item)
    station = models.ForeignKey(Station)
    dist = models.IntegerField()

    def __unicode__(self):
        return "(%s, %s, %d)" % (self.item.name, self.station.name, self.distance)

    class Meta:
        db_table = "distance"
