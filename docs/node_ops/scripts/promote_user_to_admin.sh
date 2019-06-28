#!/usr/bin/python
### IMPORT MODULES
import sys
import ruamel.yaml

### SET VARS
yaml = ruamel.yaml.YAML()
raw_user_list = "@option.username@"
split_user_list = raw_user_list.split(" ")
user_file = "/opt/octoprint/.octoprint/users.yaml"

### PROMOTE USERS
for user in split_user_list:
  with open(user_file, "r") as infile:
    data = yaml.load(infile)
  for user_entry, args in data.iteritems():
    if user_entry == user:
      args['roles'] = ['user', 'admin']
    with open(user_file, "w") as outfile:
      yaml.dump(data, outfile)

