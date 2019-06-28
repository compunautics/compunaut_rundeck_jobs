#!/bin/bash

user_list="@option.username@"

for user in ${user_list}; do
  user_present=$(sudo grep -i ${user} /opt/octoprint/.octoprint/users.yaml)
  if [[ -z ${user_present} ]]; then
    echo "User ${user} is not present! Exiting for this node!"
    exit 1
  fi
done

