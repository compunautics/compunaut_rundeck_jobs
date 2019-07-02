#!/usr/bin/python

from argparse import ArgumentParser
import os
import pwd
import grp
import json

# PARSE ARGUMENTS
parser = ArgumentParser()
parser.add_argument("-f", "--filament", type=str, dest="filament", required=True, help="The filament name for this service.")
args = parser.parse_args()

# DEFINE VARIABLES
service_address = "{{ grains.ip4_interfaces.eth0.0 }}"
service_name = "filament_" + args.filament
service_path = "/etc/consul.d/filament.json"
bool_path = "/etc/consul.d/filament_bool"
service_dict = {
  "services": [
    {
      "address": service_address,
      "checks": [
        {
          "args": [
            "/etc/consul.d/checks/check_octoprint.py"
          ],
          "interval": "5s",
          "name": service_name + " Octoprint Status"
        },
        {
          "args": [
            "/etc/consul.d/checks/check_available.py"
          ],
          "interval":"5s",
          "name": service_name + " Available"
        }
      ],
      "name": service_name
    }
  ]
}
bool_dict = {"is_available": "False"}
uid = pwd.getpwnam('consul').pw_uid
gid = grp.getgrnam('consul').gr_gid

# CHECK FOR EXISTING PATHS
if os.path.isfile(service_path):
  print "Cannot overwrite existing service regstration. Please delete /etc/consul.d/filament.json and try again."
  exit(2)

if os.path.isfile(bool_path):
  print "Cannot overwrite existing print bool. Please delete /etc/consul.d/print_bool and try again."
  exit(2)

# CREATE SERVICE FILE WITH SERVICE DATA
with open(service_path, 'w') as outfile:
  json.dump(service_dict, outfile)

os.chown(service_path, uid, gid)

with open(bool_path, 'w') as outfile:
  json.dump(bool_dict, outfile)

os.chown(bool_path, uid, gid)
