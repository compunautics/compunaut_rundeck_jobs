.. |compunaut_pic| image:: images/compunaut-logo.png
   :alt: Compunaut Logo
   :width: 7%
.. |rundeck_pic| image:: images/rundeck-logo.png
   :alt: Rundeck Logo
   :width: 5%

******************************************
|compunaut_pic| Compunaut Fleet Controller
******************************************

|rundeck_pic| Rundeck Job Documentation
=======================================

Rundeck is an operations focused automation platform developed by Rundeck. Detailed documentation on Rundeck 
can be found at their documentation website `here <https://docs.rundeck.com/docs/>`_.

For Compunaut, Rundeck is a relatively simple way to program command line tasks (jobs ) into a GUI interface 
and then expose those tasks to floor technicians so that they may manage the platform or manage the printers.

These docs will focus on the way that Rundeck is implemented operationally within the Compunaut platform.

Project Structure
=================

The jobs in Rundeck are divided into two projects, which are documented below.

Node_Ops
--------

Node Ops jobs focus on operating system and platform level tasks. These jobs are not a part of the printer 
workflow, and only high level admins should have access to these jobs. The jobs are subdivided into folders
by their general function. 

To read more information on the jobs within particular folders, please click on the links below:

.. toctree::
   :maxdepth: 2

   node_ops/index.rst

Print_Ops
---------

Print Ops jobs focus on the actual operation of the printers in the fleet. The jobs are carefully organized
into a workflow that will need to be followed in order to manage the printers effectively. Technicians with
access to this project do not require access to the Node Ops project in order to do their work.

To read more information on the jobs within this project, please link on the links below:

.. toctree::
   :maxdepth: 2

   print_ops/index.rst

Operations
==========

The previous sections discuss the jobs in technical detail. This section will describe the optimal operational
workflow that engineers should use with Compunaut Fleet Controller.

In some cases, the assumed workflow will be described. In others, protips based on testing and experience will be
documented.

.. toctree::
   :maxdepth: 2

   operations/index.rst
