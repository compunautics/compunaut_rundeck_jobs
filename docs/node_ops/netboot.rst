*******
Netboot
*******

These jobs are primarily focused on provisioning, commissioning, and decommissioning printers within the
Compunaut platform.

Descriptions of the jobs and how they work are given below.

Provision Printer Images
------------------------

This job will create raspberry pi images in Piserver on the netboot server. This is the first job in the Netboot
flow and should be executed first when adding new printers.

In order to execute this job, you must have first logged into Guacamole and installed the default compunaut-raspi.tar.xz
into Piserver. Else, you will receive an error if you attempt to run this job without that first being installed.

This job works by taking a list of image names arbitrarily defined by the admin, targeting the node with 'netboot' in the 
hostname, logging in as the 'rundeck-svc' user, and then executing these scripts.

.. note::
   The image names absolutely MUST include 'prtr' somewhere in the name in order for this and other jobs to work correctly.
   Please select your image name carefully, as this will become the identifier for your printer throughout the system.

.. literalinclude:: scripts/verify_compunaut_raspi_is_installed_in_piserver.sh

.. literalinclude:: scripts/clone_distro_and_create_new_images.sh

The first script verifies that compunaut-raspi.tar.xz is installed, while the second executes a python script called
clone_distro.py. This script copies the default image and updates various piserver configuration files and image files
so that when it is booted up for the first time it boots with the correct settings and hostname.

This job will time out after 10 minutes if it has not completed its execution.

Commission Printers
-------------------

This job will execute salt commands to install printer software on raspberry pis that have been added to the 
Compunaut platform. This is the second job in the Netboot flow.

.. note::
   Note again that in order for this job to work correctly, the images created in 'Provision Printer Images' must have
   'prtr' in their names somewhere. Please make sure to select your image names carefully, as they will become identifiers
   for your printer throughout the entire system.

The job works by specifying a salt target of '\*prtr\*' (or node_to_commission), logging into the salt master 
node as the 'rundeck-svc' user, and then running these commands in sequence.::

   # First, accept the new printer's as valid minions for the master
   sudo salt-key -a "${option.node_to_commission}" -y

   # Wait 60 seconds for the minions to fully come online, then test.ping to verify that they're connected
   sleep 60 && sudo salt "${option.node_to_commission}" test.ping

   # Set up a specific raspbian repo to prevent repo failures
   ## if you use a pool of repos instead of a specific repo, you will intermittently run into broken repos
   ## this makes the job less reliable, so we configure a specific one instead
   sudo salt "${option.node_to_commission}" state.apply compunaut_octoprint.repo --state_output=mixed -b8 --batch-wait 15 && sleep 10

   # Configure the salt minion with mine and tuning parameters
   sudo salt "${option.node_to_commission}" state.apply compunaut_salt --state_output=mixed -b8 --batch-wait 15 && sleep 10

   # Apply default configuration (needed to properly set the hostname of the raspberry pi) and iptables rules
   sudo salt "${option.node_to_commission}" state.apply compunaut_default,compunaut_iptables --state_output=mixed -b6 --batch-wait 15 && sleep 10

   # Using a bootstrap script, we wait for all minions to become responsive again and ready for new commands
   sudo /srv/bootstrap/compunaut_minion_wait.sh

The job will then execute the 'Update Data' job from the SaltStack folder, which refreshes the pillar, grain, 
and mine data on the salt master. Then the job runs these commands.::

  # Sync all custom salt modules to the new printer minions
  sudo salt "${option.node_to_commission}" saltutil.sync_all -b6 --batch-wait 15 && sleep 10

  # Run this state.orch to generate the public key infrastructure for the new printer minions
  ## This will be needed for the apache reverse proxy that is used to reach octoprint and the webcam
  sudo salt-run state.orch orch.generate_pki --state-output=mixed && sleep 10

  # Install dnsmasq and consul
  sudo salt "${option.node_to_commission}" state.apply compunaut_dns,compunaut_consul --state_output=mixed -b6 --batch-wait 15 && sleep 10

  # Install SSSD, the system authentication daemon that allows SSH logins with LDAP credentials
  ## This step fails a lot for unknown reasons, though sssd does get installed, so the failure handler attempts an sssd restart
  sudo salt "${option.node_to_commission}" state.apply compunaut_sssd --state_output=mixed -b6 --batch-wait 15 && sleep 10

  # Install Octoprint and its ancillary components
  sudo salt "${option.node_to_commission}" state.apply compunaut_octoprint --state_output=mixed -b6 --batch-wait 15 && sleep 10

  # Highstate the raspberry pi to ensure that everything is installed as desired
  sudo salt "${option.node_to_commission}" state.highstate --state_output=mixed -b6 --batch-wait 15 && sleep 10

At this point, the job will then execute the 'Update Data' job from the SaltStack folder again, and will then
Run the `Update DNS, Proxy, and Dashboard <https://compunaut-rundeck-jobs.readthedocs.io/en/latest/node_ops/linux.html#update-dns-proxy-and-dashboard>`_ job within the Linux folder to ensure that the platform DNS, haproxy,
and Mission Control dashboard are all updated.

In general, this job can take up to 40-60 minutes to run for a single printer. Many of the steps handle multiple
printers in batches, so it can be expected for this time to double for roughly every 6 additional printers you
add to the system.

This job will time out after 3 hours if it has not completed its execution.

Decommission Printers
---------------------

This job can be used to fully decommission a printer and its raspberry pi from the system. This job is the third
in the Netboot flow. 

In order for this job to work correctly, the raspberry pi must be powered off. It may also be advisable to delete 
the image from Piserver via Guacamole if the pi's hostname will never be used again.

The job works by referring to other jobs in the other folders. 

* The job executes the 'Delete Keys' job in the Saltstack folder, which removes the minions from saltstack.
* Then it executes the `Decommission node from Consul <https://compunaut-rundeck-jobs.readthedocs.io/en/latest/node_ops/linux.html#decommission-node-from-consul>`_ job in the Linux folder, which removes the minions from Consul.
* Then the `Decommission node from Influxdb <https://compunaut-rundeck-jobs.readthedocs.io/en/latest/node_ops/linux.html#decommission-node-from-influxdb>`_ job in the Linux folder is executed, which removes old monitoring data for the minion from influxdb.
* Penultimately the 'Update Data' job from the Saltstack folder is executed to update mine, grain, and pillar information.
* Lately, the `Update DNS, Proxy, and Dashboard <https://compunaut-rundeck-jobs.readthedocs.io/en/latest/node_ops/linux.html#update-dns-proxy-and-dashboard>`_ job from the Linux folder is executed to update haproxy, DNS, and the mission control dashboard.

This job will time out after 5 minutes if it has not completed its execution.
