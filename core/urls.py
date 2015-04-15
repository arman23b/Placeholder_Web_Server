from django.conf.urls import patterns, url

from core import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^addRoom$', views.addRoomView, name='addRoom'),
    url(r'^addStation$', views.addStationView, name='addStation'),
    url(r'^addItem$', views.addItemView, name='addItem'),

    url(r'^loadUnregistered$', views.loadUnregistered, name='loadUnregistered'),
    url(r'^newData$', views.newData, name='newData'),
    url(r'^getStationsForRoom$', views.getStationsForRoomView, name='getStations'),
    url(r'^updatePollingFreq$', views.updatePollingFreq, name='updatePollingFreq'),
    url(r'^broadcastUuid$', views.broadcastSearchingBeacon, name='broadcastUuid'),
    url(r'^unregisterItem$', views.unregisterItem, name='unregisterItem'),
    url(r'^unregisterStation$', views.unregisterStation, name='unregisterStation'),
)
