#!/usr/bin/python

import requests
import json

headers={"X-Api-Key":"@option.apikey@","Content-Type":"application/json"}
payload={"command":"home","axes":["x","y","z"]}
url="http://127.0.0.1:5000/api/printer/printhead"

r = requests.post(url, headers=headers, data=json.dumps(payload))

print "Printer returned:"
print r.status_code
