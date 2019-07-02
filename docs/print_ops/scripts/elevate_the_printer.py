#!/usr/bin/python

import requests
import json

headers={"X-Api-Key":"@option.apikey@","Content-Type":"application/json"}
payload={"command":"jog","absolute":1,"speed":1500,"x":110,"y":110,"z":110}
url="http://127.0.0.1:5000/api/printer/printhead"

r = requests.post(url, headers=headers, data=json.dumps(payload))

print "Printer returned:"
print r.status_code
