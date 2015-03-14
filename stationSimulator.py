import requests, json, time
from random import randint

url = "http://localhost:8000"

while True:
    time.sleep(5)
    data = { "beaconId 0" : "-10",
             "beaconId 1" : "-11",
             "beaconId 2" : "-12",
             "beaconId 3" : "-13",
             "beaconId 4" : "-14",
             "beaconId 5" : "-15",
             "beaconId 6" : "-16",
             "beaconId 7" : "-17",
            }
    post = { "data" : json.dumps(data) }
    requests.post(url + '/newData', data=post)