#!/bin/bash

is_installed=$(grep "compunaut-raspi" /var/lib/piserver/installed_distros.json)

if [[ -z ${is_installed} ]]; then
  echo "compunaut-raspi is not installed!"
  exit 1
else
  echo "compunaut-raspi is installed!"
fi
