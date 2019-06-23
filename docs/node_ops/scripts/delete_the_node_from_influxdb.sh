#!/bin/bash

node_list="@option.node_to_remove@"

for node in ${node_list}; do
  echo "Deleting node ${node}..."
  sudo influx --database=compunaut_telegraf -execute "drop series where host='${node}'"
done
