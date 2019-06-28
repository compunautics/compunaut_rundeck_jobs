*********
Octoprint
*********

These jobs are primarily focused on Octoprint related tasks. Descriptions of the jobs and how they work are given below.

Check Updates
-------------

This job will check for any available Octoprint updates. It works by displaying all nodes with the 'octoprint_printer' tag, allowing
the admin to select any arbitrary printer node.

It then logs into the node via the 'rundeck-svc' user, and then running this command::

  sudo -u octoprint /opt/octoprint/OctoPrint/venv/bin/octoprint plugins softwareupdate:check

The Log Output of the job will display any available updates.

Perform Updates
---------------

This job will actually perform updates on Octoprint and its plugins. It works by displaying all nodes with the 'octoprint_printer'
tag, allowing the admin to select any arbitrary printer node.

It then logs into the node via the 'rundeck-svc' user, and then running this command::

  /opt/octoprint/OctoPrint/venv/bin/octoprint plugins softwareupdate:update

The Log Output of the job will display the results of the update.

Promote Octoprint User
----------------------

This job will promote users - who have already logged into a given Octoprint node - to the 'admin' role. This job will only work
if the user that you are trying to promote has already logged into the selected Octoprint node once.

The admin can select any node that has the 'octoprint_printer' tag to run this on. The job will log into the node via the 
'rundeck-svc' user, and will then execute these scripts and commands in sequence::

   # Verify that the users.yaml file is present
   sudo ls /opt/octoprint/.octoprint/users.yaml

.. literalinclude:: scripts/verify_user_is_present.sh

.. literalinclude:: scripts/promote_user_to_admin.sh

Once these commands/scripts have been run, Rundeck will restart Octoprint by executing the '`Restart Octoprint <https://compunaut-rundeck-jobs.readthedocs.io/en/latest/node_ops/octoprint.html#restart-octoprint>`_' job so that the 
changes will take effect in Octoprint.

Refresh Octoprint Configuration
-------------------------------

Saltstack does not automatically update the Octoprint configuration when it is changed in the salt repository. This is because we
do not want Octoprint to be inadvertently restarted without manual admin attention. This job accomplishes this. 

It targets nodes with the 'octoprint_printer' tag, logs into them via the 'rundeck-svc' user, deletes the 
/opt/octoprint/.octoprint/config.yaml file, and then executes the '`Run Salt <https://compunaut-rundeck-jobs.readthedocs.io/en/latest/node_ops/saltstack.html#run-salt>`_' job - which applies the
compunaut_octoprint state on the raspberry pi - and the '`Restart Octoprint <https://compunaut-rundeck-jobs.readthedocs.io/en/latest/node_ops/octoprint.html#restart-octoprint>`_' job so that the new config takes effect.

Restart Octoprint
-----------------

This job is very simple. It will restart the Octoprint service on the targeted nodes. Targets can be selected from a list of nodes
that have the 'octoprint_printer' tag. The job will log into the node via the 'rundeck-svc' user and will then execute this command.::

   sudo systemctl restart octoprint
