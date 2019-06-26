************************
Netboot Operations Guide
************************

The Netboot workflow commissions and sets up your printer fleet. Once your printers are commissioned within Compunaut,
you will be able to execute print jobs against them with Rundeck, manage access to them, and monitor them with Consul and
Grafana.

This section focuses on protips observed during testing that may improve your operational flow, specifically with regards
to the Netboot suite of jobs.

High Level Overview of the Netboot Workflow
===========================================

Enabling Netboot Functionality with your Raspberry Pi
=====================================================

Pre-commissioning the Default Printer Image
===========================================

The Netboot workflow - even for a small group of 4 to 6 printers - can take several hours to complete. Commissioning even one
printer with a Raspberry Pi 3B+ can take about an hour (and for every 6 additional printers you add to your batch, this time
increases by another hour).

To try and cut this time down for your printer fleet, you can pre-commission the default compunaut-raspi printer image. 

Why would this be necessary? The compunaut-raspi image comes with nothing installed on it except for a salt-minion. It's set up 
this way to ensure the cleanest state after the platform is installed, before engineers being working with the system. 
Unfortunately, this means that much more work has to be done to install each individual printer image.

Pre-commissioning the default image will install most of the generic software on that image. You can then use this pre-commissioned
image when provisioning new printer images via Rundeck. With this being done, it will take much less time to commission printers.

How to Pre-commission the Default Printer Image
-----------------------------------------------

#. Access Guacamole, and then load Piserver via the desktop icon. Ensure that compunaut-raspi is installed by selecting the
   'Software' tab. If it is not installed, then click on the "Add" button at the top of the menu, opt to "Install operating system
   from local file (.tar.xz), and then navigate to Desktop and select the image.

#. Installing the image will take a minute or two. When it is complete, navigate to the 'Clients' tab in Piserver and click on
   the "Add" button at the top of the menu. At the bottom right, make sure that the selected "Operating system" is 
   compunaut-raspi. Now plug your netboot-enabled Raspberry Pi into the local network and power it on. After a few seconds, you
   should see its MAC address appear in the menu.

#. Quickly ensure that the MAC address is highlighted, and then click on "OK" in the lower right hand corner of the menu. Your
   Raspberry Pi should then start netbooting based on the default image.

#. On the salt master node, run :code:`watch -n1 salt-key -L` and wait for 'raspberrypi' to appear in the "Unaccepted Keys" list. 
   When it does, execute the following commands as root on the salt master node in sequence to pre-commission the default image.::

     # Accept the salt minion
     salt-key -A -y

     # This command will let you know when the new salt minion is available to run commands
     /srv/bootstrap/compunaut_minion_wait.sh

     # Configure the salt minion
     salt '*raspberrypi*' state.apply compunaut_salt

     # The salt minion restarts in the prior command, so wait for it to become available again
     /srv/bootstrap/compunaut_minion_wait.sh

     # Sync all custom salt modules to the minion
     salt '*raspberrypi*' saltutil.sync_all

     # Apply these modules to the minion
     salt '*raspberrypi*' state.apply compunaut_octoprint.repo,compunaut_default,compunaut_dns,compunaut_consul,compunaut_sssd,compunaut_telegraf,compunaut_chronyd,compunaut_iptables

#. The above steps should take around 30 to 45 minutes to complete with the default image. Once it is done, you may power off
   the Raspberry Pi that you have been using.

#. Once the Pi is powered off, on the salt master node run :code:`salt-key -d raspberrypi -y` to delete the default image
   minion from salt master's registry.

#. At this point, begin the normal Netboot Workflow as you otherwise would.
