#!/usr/bin/python

import os
import pwd
import grp
import json

# DEFINE VARIABLES
bool_path = "/etc/consul.d/filament_bool"
bool_dict = {"is_available": "True"}
uid = pwd.getpwnam('consul').pw_uid
gid = grp.getgrnam('consul').gr_gid

# MAKE AVAILABLE
with open(bool_path, 'w') as outfile:
  json.dump(bool_dict, outfile)

os.chown(bool_path, uid, gid)
