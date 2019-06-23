*****
Linux
*****

These jobs are primarily focused on the linux operating system or on updates to system components 
of the platform that are not directly related to the other folders in this project.

Descriptions of the jobs and how they work are given below.

Decommission node from Consul
-----------------------------

This job deletes nodes from Consul, the service discovery and integration mesh that is part of the 
Compunaut platform. 

It works by targeting any node with 'consul' in its hostname. Using a list of hostnames given in the 
options, it logs into the node using the 'rundeck-svc' user and then executes the following BASH 
script:

.. literalinclude:: scripts/delete_the_node_from_consul.sh

The job will timeout after 5 minutes if it has not completed its execution.

This job is used as part of the 'Decommission Printers' job in the 'Netboot' folder, but that does not
mean that it cannot be used for other nodes that are being decommissioned as well.

Decommission node from Influxdb
-------------------------------

This job deletes all entries involving a particular node from Influxdb, which is the metric storage
database that is used by Grafana for time series monitoring. 

It works by targeting any node with 'db' in the hostname. Using a list of hostnames given in the 
options, it logs into the node using the 'rundeck-svc' user and then executes the following BASH 
script: 

.. literalinclude:: scripts/delete_the_node_from_influxdb.sh

It then restarts the influxdb service on that node.

The job will timeout after 5 minutes if it has not completed its execution.

This job is used as part of the 'Decommission Printers' job in the 'Netboot' folder, but that does not
mean that it cannot be used for other nodes that are being decommissioned as well.

Update DNS, Proxy, and Dashboard
--------------------------------

This job is used to update the backend Haproxy and Dnsmasq services, as well as the Mission Control
panel site files. Typically, this is done whenever new printers are being added to the platform so that
they will be accessible via hostname DNS resolution and via the mission control dashboard.

This is done by targeting the salt master node as the 'rundeck-svc' user and then running these three salt 
commands in sequence.::

   sudo salt -I 'compunaut_haproxy:enabled:True' state.apply compunaut_haproxy --state_output=mixed && sleep 10
   sudo salt -I 'compunaut_dns:server:enabled:True' state.apply compunaut_dns --state_output=mixed && sleep 10
   sudo salt -I 'compunaut_mission_control:enabled:True' state.apply compunaut_mission_control.site --state_output=mixed && sleep 10

The job will timeout after 5 minutes if it has not completed its execution.

This job is used as part of the 'Commission Printers' job in the 'Netboot' folder, but it can be run at any 
time for other purposes.

Update Software
---------------

This job will update all software that is installed via the Apt package manager. Any node that is registered in 
saltstack can be arbitrarily targeted by the admin. 

The job works by logging into the targeted nodes via the 'rundeck-svc' user, which then executes this command.::

  sudo apt-get update && sudo apt-get -o Dpkg::Options::='--force-confold' --force-yes -fuy dist-upgrade && sudo apt autoremove -y

The job will timeout after 100 minutes if it has not completed its execution.

Generally, this job would be used to ensure that all of the latest software is installed on the platform nodes.
Some software in compunaut is not installed via apt, however (ie Consul, Consul-Alerts, Guacamole, etc). Also
keep in mind that this job may upgrade rundeck if executed against the rundeck nodes, which will cause an 
interruption in the UI availability.

Update System Clock
-------------------

This job forces the Chronyd time keeping service to step the system clock. In general, Chronyd does its best to
avoid stepping (suddenly changing the time to a completely different time) in favor of slewing (slowing or speeding
up the passing seconds until the system clock matches the remote time source). 

Sometimes, when a system boots up, this can cause the system clock to be wildly out of sync with the desired time, and 
that can cause other issues. For example, telegraf will not correctly monitor and send metrics to influxdb when the
system clock is out of sync with the other nodes in the cluster.

This job works by logging into the nodes targeted by the admin as the 'rundeck-svc' user, and then executing this command.::

  sudo chronyc -a 'burst 1/4' && sudo timeout 60 chronyc -a makestep

It will then display the date to ensure that the new time is correct.
