#!/bin/bash

image_list="@option.image_names@"

for image in ${image_list}; do
  echo "Cloning ${image}..."
  sudo /var/lib/piserver/scripts/clone_distro.py -d ${image}
  echo "Done!"
done
