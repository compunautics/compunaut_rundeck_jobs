**********
Components
**********

Components are a sub-category of jobs that are used within the Workflow jobs. They're sorta like functions, in that they're
programmed once and then used over and over again as needed elsewhere within this project.

You can find descriptions of the various categories and jobs within them below.

Gcodes
======

There is only one gcode job, and it is not actually a part of any workflow job. It's placed in components because it should only
ever rarely be used.

Flush Gcode Files
-----------------

This job will delete all Gcode files that have been uploaded to Rundeck. It's the equivalent of wiping the system clean so that you
can start over from scratch.

This job works by accessing nodes that have the 'rundeck_server' tag, logging in with the 'rundeck-svc' user (rundeck for the 
executing server), and then running the following command.::

   # delete the directory where gcodes are uploaded
   sudo rm -rfv /var/rundeck/projects/Print_Ops/gcodes/

This job will time out after 5 minutes.

Filaments
=========

Filament components deal with the basics of managing filament registration. Several Workflow jobs make use of these components 
when issuing print orders.

Filament management is a critical part of the way that the Compunaut Fleet Controller manages printers. 3D printers cannot function
unless a specific filament is loaded into them, and Compunaut requires the printer technician to register the filament at the time
that it is loaded. This creates a new consul service, which we can then target to issue print orders to filaments directly instead
of at specific printers.

Register Filament
-----------------

This job registers a filament with a printer. It presents the technician with a list of filaments, which is derived from whatever
gcode files the technician has loaded to Rundeck. No list will be presented if no gcodes have been uploaded.

The technician selects the desired filament and then can select any arbitrary printer (derived from those nodes that have the 
'octoprint_printer' tag). When the job is executed, Rundeck logs into the node via the 'rundeck-svc' user and runs the command
below.::
   
   # This script registers the filament into consul
   sudo /etc/consul.d/scripts/register_filament.py -f ${option.filament}

The script itself is presented below. It checks to see if there is an existing registration and "print bool," which is just a simple
file that marks the filament as available or not. If neither are present, it will create them. Else, it will error out so that 
no existing registrations will be overwritten by accident.

.. literalinclude:: scripts/register_filament.py

Once the new registration is created, the job will reload consul so that the new registration will take effect.

This job is used in the Workflow `03 Exchange Filament <https://compunaut-rundeck-jobs.readthedocs.io/en/latest/print_ops/workflow.html#exchange-filament>`_ and `06 Issue Print Order by Printer <https://compunaut-rundeck-jobs.readthedocs.io/en/latest/print_ops/workflow.html#issue-print-order-by-printer>`_ jobs, and it will timeout after 5 minutes.

De-register Filament
--------------------

This job deletes an existing filament registration. This is often the prelude to exchanging the filament for something else. 

Compared to the `Register Filament <https://compunaut-rundeck-jobs.readthedocs.io/en/latest/print_ops/components.html#register-filament>`_ job, this one is markedly simpler. It allows the technician to target any node with the 'octoprint_printer' tag, and then runs these commands as the 'rundeck-svc' user in sequence.::

   # delete any filament registration that exists
   sudo rm -fv /etc/consul.d/{filament.json,filament_bool}

   # reload consul so that it takes effect
   sudo systemctl reload consul

This job is used in the Workflow `03 Exchange Filament <https://compunaut-rundeck-jobs.readthedocs.io/en/latest/print_ops/workflow.html#exchange-filament>`_ and `06 Issue Print Order by Printer <https://compunaut-rundeck-jobs.readthedocs.io/en/latest/print_ops/workflow.html#issue-print-order-by-printer>`_ jobs, and will timeout after 5 minutes.

Mark Filament Available
-----------------------

Just because a filament has been registered does not mean that the printer is ready to accept orders. In order to allow the
technician to complete preparations - or clean a finished print - the concept of "filament availability" is present in Compunaut 
as well.

Recall the 'print bool' from the `Register Filament <https://compunaut-rundeck-jobs.readthedocs.io/en/latest/print_ops/components.html#register-filament>`_ job. This is how a filament is marked available and unavailable. In this job the bool is changed to mark the filament available and open the printer up to receiving new print orders.

It works by allowing the technician to target any node with the 'octoprint_printer' tag, logs in as the 'rundeck-svc' user, and then
executes the script below.

.. literalinclude:: scripts/make_available.py

This job is used as part of the Workflow `04 Mark Filament Available <https://compunaut-rundeck-jobs.readthedocs.io/en/latest/print_ops/workflow.html#mark-filament-available>`_ job, and it will timeout after 5 minutes.

Mark Filament Unavailable
-------------------------

When a printer accepts a print order, it needs to immediately mark the filament unavailable so that Rundeck will not
inadvertantly assign a second order to it. We also need to ensure that no further orders will be assigned to the printer when the
in-progress order has been completed, as the printer will need to be cleaned by the technician before the printer can take more
orders.

This job accomplishes this task. The technician targets any node with the 'octoprint_printer' tag, and Rundeck logs in with the 
'rundeck-svc' user, executing the script below.

.. literalinclude:: scripts/make_unavailable.py

This job is used as part of the Workflow `05 Issue Print Order by Filament <https://compunaut-rundeck-jobs.readthedocs.io/en/latest/print_ops/workflow.html#issue-print-order-by-filament>`_ job. It is not present in the 
`06 Issue Print Order by Printer <https://compunaut-rundeck-jobs.readthedocs.io/en/latest/print_ops/workflow.html#issue-print-order-by-printer>`_ job because, even though a filament is registered in that job, it is marked unavailable by default.

This job will timeout after 5 minutes.

Temperature
===========

Temperature management is another key part of how Compunaut Fleet Controller manages printers. When filaments are exchanged, printers
prepped for orders, or printers cleaned, their head and bed temperatures will need to be adjusted. 

Heat Printer
------------

This job heats the print head and the bed to the settings input by the technician. The technician then selects any node that has
the 'octoprint_printer' tag.

Rundeck will access the node using the 'rundeck-svc' user, and will then execute these two scripts in sequence. The scripts issue
commands to `Octoprint's REST API <http://docs.octoprint.org/en/master/api/printer.html>`_.

.. literalinclude:: scripts/heat_the_print_head.py

.. literalinclude:: scripts/heat_the_print_bed.py

This job is used as part of the Workflow `03 Exchange Filament <https://compunaut-rundeck-jobs.readthedocs.io/en/latest/print_ops/workflow.html#exchange-filament>`_ job, and it will timeout after 5 minutes.

Cool Printer
------------

This job will cool the printer to a resting state. The technician can select any node that has the 'octoprint_printer' tag. 

Rundeck will access the node using the 'rundeck-svc' user, and will then execute these two scripts in sequence. As before, the
scripts issue commands to `Octoprint's REST API <http://docs.octoprint.org/en/master/api/printer.html>`_.

.. literalinclude:: scripts/cool_the_print_head.py

.. literalinclude:: scripts/cool_the_print_bed.py

This job is not a part of any Workflow job, but it is present in case the technician needs to cool down printers for any reason.

This job will timeout after 5 minutes.

Head
====

The last Component jobs are those that manage the position of the print head, and there are only two positions that Compunaut is
concerned with: an elevated position, and a home position.

Elevate Printer
---------------

This job will elevate the printer to a position that is generally in the middle of the print area. The position is hard coded to
110mm from X origin, 110mm from Y origin, and 110mm from Z origin. This should place the print head roughly in the middle
of any desktop grade printer, where maintenance or filament exchange can take place more easily.

The technician may select any node that has the 'octoprint_printer' tag, after which Rundeck will first execute the 
`Home Printer <https://compunaut-rundeck-jobs.readthedocs.io/en/latest/print_ops/components.html#home-printer>`_ Component job to make sure that the print head starts from a known position. Then, Rundeck will access the node with the 'rundeck-svc' user and execute the script below. The script issues commands to 
`Octoprint's REST API <http://docs.octoprint.org/en/master/api/printer.html#issue-a-print-head-command>`_.

.. literalinclude:: scripts/elevate_the_printer.py

This job is used as part of the Workflow `03 Exchange Filament <https://compunaut-rundeck-jobs.readthedocs.io/en/latest/print_ops/workflow.html#exchange-filament>`_ job, and it will timeout after 5 minutes.

Home Printer
------------

This job will home the printer, which is a predesignated known position that is often used as a starting point for all print jobs.
In Compunaut, this job is actually used by another Component job, `Elevate Printer <https://compunaut-rundeck-jobs.readthedocs.io/en/latest/print_ops/components.html#elevate-printer>`_, to ensure that the print head does not try to go outside of the bounds of the print area - which could potentially damage the printer.

The job works by allowing the technician to select any node that has the 'octoprint_printer' tag. Rundeck will then log into the node
via the 'rundeck-svc' user and execute the following script. As before, the script issues commands to 
`Octoprint's REST API <http://docs.octoprint.org/en/master/api/printer.html#issue-a-print-head-command>`_.

.. literalinclude:: scripts/home_the_printer.py
