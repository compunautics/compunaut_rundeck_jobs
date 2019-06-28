*********
Saltstack
*********

These jobs primarily focus on Saltstack related tasks, and are used as components in other jobs that require Saltstack updates. 
Descriptions of the jobs are given below.

Accept Keys
-----------

This job will log into the Salt master node - as determined by which node has the 'salt_master' tag - and will accept salt keys.
This job is a key step in commissioning new nodes, particularly printers.

It works by accepting a glob as an option, logging into the salt master as the 'rundeck-svc' user, and then running these commands.::

   # List all keys before action is taken
   sudo salt-key -L

   # Accept the keys in the glob
   sudo salt-key -a "${option.key_to_accept}" -y

This job will time out after 5 minutes.

Delete Keys
-----------

This job will log into the Salt master node - as determined by which node has the 'salt_master' tag - and will delete salt keys.
This job is a key step in decommissioning existing nodes.

It works by accepting a list of nodes that need to have their salt keys deleted, and then logging into the salt master to run these
commands and scripts.::

  # List all keys before action is taken
  sudo salt-key -L

  # Delete the keys from the list
  #!/bin/bash

  key_list="@option.key_to_delete@"

  for key in ${key_list}; do 
    sudo salt-key -d "${key}" -y
  done

This job will time out after 5 minutes.

Run Salt
--------

This job will log into any node that has been commissioned into the platform and will run a salt state. It works by logging into
the selected nodes as the 'rundeck-svc' user and then executing the states given by the admin as follows.::

   # Run the salt states
   sudo salt-call state.apply ${option.State} --state_output=mixed

The admin can input multiple states so long as they delimit them with commas, like so: "compunaut_salt,compunaut_iptables"

The job will run the states in batches of 8 so that it takes less time for them to be applied to the system. If the job takes longer
than 100 minutes, it will time out.

Update Data
-----------

This job is used to update Saltstack's grains, mine, and pillar data. Since many of Compunaut's configuration information is derived
from these three things, this job is used often when commissioning new nodes.

The job works by targeting the Salt master node - as determined by which node has the 'salt_master' tag - and then logging in with
the 'rundeck-svc' user. Once logged in, the command below is executed.::

   # We use an orch state, which is an orchestrated list of several salt states and functions
   sudo salt-run state.orch orch.update_data --state-output=mixed

This will, in effect, run these states in sequence.::

   # Clear the pillar cache on disk; else we won't get updated data
   clear_cache:
     salt.function:
       - name: cmd.run
       - tgt: 'compunaut_salt:enabled:True'
       - tgt_type: pillar
       - arg:
         - rm -fv /var/cache/salt/master/pillar_cache/*

   grain_update:
     salt.function:
       - name: saltutil.refresh_grains
       - tgt: '*'
       - batch: 4

   first_pillar_update:
     salt.function:
       - name: saltutil.refresh_pillar
       - tgt: '*'
       - batch: 4

   mine_update:
     salt.function:
       - name: mine.update
       - tgt: '*'
       - batch: 4

   second_pillar_update:
     salt.function:
       - name: saltutil.refresh_pillar
       - tgt: '*'

This job will time out after 15 minutes.
