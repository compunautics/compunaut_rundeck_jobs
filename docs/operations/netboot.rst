************************
Netboot Operations Guide
************************

A key workflow in Compunaut is to install Raspberry Pis as controllers for the individual printers that make up the fleet.
Raspberry Pis are inexpensive, easy to handle, and remarkably capable machines, but managing a large fleet of dozens of them can
be a chore, especially when you have to have to manage unreliable SD cards.

Thankfully, Raspberry Pis support network boot, which allows you to boot them with no local storage. Their operating systems
and other installed configurations are stored remotely, where they can be easily copied, deleted, and transferred. In a sense,
managing your printer fleet becomes like managing computers in a cloud.

The Netboot workflow accomplishes this and commissions your printer fleet. Once your printers are commissioned within Compunaut,
you will be able to execute print jobs against them with Rundeck, manage access to them, and monitor them with Consul and
Grafana.

This section focuses on protips observed during testing that may improve your operational flow, specifically with regards
to the Netboot suite of jobs.

High Level Overview of the Netboot Workflow
===========================================

When the Compunaut Fleet Controller platform is first installed, you will need to do the following things to set up Netboot
and commission your fleet.

#. Log into Guacamole, launch Piserver, and install the default compunaut-raspi.tar.xz image. Information on using Piserver can be found here: `https://www.raspberrypi.org/blog/piserver/ <The Raspberry Pi PiServer tool>`_ Refer to the section on "How to use PiServer."

#. Use Rundeck to `Provision images <https://compunaut-rundeck-jobs.readthedocs.io/en/latest/node_ops/netboot.html#provision-printer-images>`_ for each printer/raspberry pi pair in your fleet.

#. Revert back to Guacamole, and - using Piserver - power on each of your Raspberry Pis one by one, assigning each to an image.

#. After waiting for each Pi to boot, use Rundeck again to `Commission your printers <https://compunaut-rundeck-jobs.readthedocs.io/en/latest/node_ops/netboot.html#commission-printers>`_. Once commissioned, your printers will be ready for use!

This is just a high level overview. More details on this flow are given in `Netboot <https://compunaut-rundeck-jobs.readthedocs.io/en/latest/node_ops/netboot.html>`_ and in `Pre-commissioning the Default Printer Image <https://compunaut-rundeck-jobs.readthedocs.io/en/latest/operations/netboot.html#how-to-pre-commission-the-default-printer-image>`_.

Enabling Netboot Functionality with your Raspberry Pi
=====================================================

Not all Raspberry Pis support network booting. In general, you will want to use Raspberry Pi 3b+ units only with Compunaut Fleet
Controller. These units do not require any pre-configuration to enable network booting and should work with Compunaut out of the box.

If you have any other type of Raspberry Pi, or if you are just curious about Pis and netbooting, please refer to the guides below:

* `Pi 3 booting part II: Ethernet <https://www.raspberrypi.org/blog/pi-3-booting-part-ii-ethernet-all-the-awesome/>`_ (which Pis will support network booting)

* `Network Booting <https://www.raspberrypi.org/documentation/hardware/raspberrypi/bootmodes/net.md>`_ (more technical information on how network boot with Pis work)

* `Network boot your Raspberry Pi <https://www.raspberrypi.org/documentation/hardware/raspberrypi/bootmodes/net_tutorial.md>`_ (a tutorial on how you can network boot on your own for fun)

* `Bare Metal Raspberry Pi 3B+: Network Boot <https://metebalci.com/blog/bare-metal-rpi3-network-boot/>`_ (a third party guide that explains much of the same things above)

Pre-commissioning the Default Printer Image
===========================================

The Netboot workflow - even for a small group of 4 to 6 printers - can take several hours to complete. Commissioning even one
printer with a Raspberry Pi 3B+ can take about an hour (and for every 6 additional printers you add to your batch, this time
increases by another hour).

To try and cut this time down for your printer fleet, you can optionally pre-commission the default compunaut-raspi printer image. 

Why would this be necessary? The compunaut-raspi image comes with nothing installed on it except for a salt-minion. It's set up 
this way to ensure the cleanest state after the platform is installed, before engineers being working with the system. 
Unfortunately, this means that much more work has to be done to install each individual printer image.

Pre-commissioning the default image will install most of the generic software on that image. You can then use this pre-commissioned
image when provisioning new printer images via Rundeck. With this being done, it will take much less time to commission printers.

How to Pre-commission the Default Printer Image
-----------------------------------------------

To execute these steps, you will need access to Guacamole (for piserver), the Salt Master node, and Rundeck Node_Ops. 
Please makes sure that you have access to each of these systems before proceeding. If you do not have access, then escalate
to your system administrator to obtain access or to have them perform this procedure.

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
     ## Even if this command succeeds, you may still need to wait a minute before the minion accepts states
     /srv/bootstrap/compunaut_minion_wait.sh

     # Configure the salt minion
     salt '*raspberrypi*' state.apply compunaut_salt

     # The salt minion restarts in the prior command, so wait for it to become available again
     ## Even if this command succeeds, you may still need to wait a minute before the minion accepts states
     /srv/bootstrap/compunaut_minion_wait.sh

     # Sync all custom salt modules to the minion
     salt '*raspberrypi*' saltutil.sync_all

     # Apply these modules to the minion
     salt '*raspberrypi*' state.apply compunaut_octoprint.repo,compunaut_default,compunaut_dns,compunaut_sssd,compunaut_chronyd,compunaut_octoprint.motion.install,apache,compunaut_iptables

     # Install these packages to the minion
     salt '*raspberrypi*' cmd.run 'apt-get -o Dpkg::Options::='--force-confold' --force-yes -fuy install git python-pip virtualenv libsasl2-dev python-dev libldap2-dev libssl-dev cura-engine'

#. The above steps should take around 30 to 45 minutes to complete with the default image. Once it is done, you may power off
   the Raspberry Pi that you have been using, and you may click on the "Remove" button in Piserver to remove 'compunaut-raspi'
   as a client from the MAC address that you loaded in step 2 and 3.

#. Once the Pi is powered off, on the salt master node run :code:`salt-key -d raspberrypi -y` to delete the default image
   minion from salt master's registry.

     .. note::
        If it looks like the 'Wait for minions to respond' step in the 'Commission Printers' job is taking longer
        than it should, make sure that the "raspberrypi" salt-key has been deleted.

#. At this point, begin the normal Netboot Workflow as you otherwise would.
