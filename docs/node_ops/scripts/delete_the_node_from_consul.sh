#!/bin/bash

node_list="@option.node_to_remove@"

for node in ${node_list}; do
  echo "Deleting node ${node}..."
  sudo consul force-leave ${node}
done

