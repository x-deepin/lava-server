LAVA Overview
#############

[ `LAVA V1 <v1/index.html>`_ ]
[ `LAVA V2 <v2/index.html>`_ ]

Return to LAVA site:
[ `Home <../../>`_ ]
[ `Dashboard <../../dashboard/>`_ ]
[ `Results <../../results/>`_ ]
[ `Scheduler <../../scheduler/>`_ ]
[ `API <../../api/help/>`_ ]

.. index:: LAVA

What is LAVA?
*************

LAVA is the Linaro Automation and Validation Architecture.

LAVA is a continuous integration system for deploying operating
systems onto physical and virtual hardware for running tests.
Tests can be simple boot testing, bootloader testing and system
level testing, although extra hardware may be required for some
system tests. Results are tracked over time and data can be
exported for further analysis.

LAVA is a collection of participating components in an evolving
architecture. LAVA aims to make systematic, automatic and manual
quality control more approachable for projects of all sizes.

LAVA is designed for validation - testing whether the code that
engineers are producing "works", in whatever sense that
means. Depending on context, this could be many things, for example:

* testing whether changes in the Linux kernel compile and boot
* testing whether the code produced by gcc is smaller or faster
* testing whether a kernel scheduler change reduces power consumption for a certain workload
* etc.
 
LAVA is good for automated validation. LAVA tests the Linux kernel on
a range of supported boards every day. LAVA tests proposed android
changes in gerrit before they are landed, and does the same for other
projects like gcc. Linaro runs a central validation lab in Cambridge,
containing racks full of computers supplied by Linaro members and the
necessary infrastucture to control them (servers, serial console
servers, network switches etc.)

.. note:: This overview document explains LAVA using
          http://validation.linaro.org/ which is the official
          production instance of LAVA hosted by Linaro. Where examples
          reference ``validation.linaro.org``, replace with the fully
          qualified domain name of your LAVA instance.

LAVA Migration
**************

LAVA is currently in the middle of a lengthy migration from its
original design (known as the V1 model) to a new design, called the
Pipeline model or the V2 model. During this migration, LAVA
installations will be able to support test devices and test jobs
targeting both models. These help pages are divided into V1 and V2
accordingly.

While this migration is taking place, it is expected that some LAVA
instances will only support V2, some will support both versions and
some may only support V1. However, V1 support is **deprecated** and will
be removed at some point in 2017. Instances which do not migrate to V2
will not be able to receive updates beyond that point so users are
strongly encouraged to move to V2 as soon as possible.

.. note:: Please subscribe to the :ref:`mailing_lists` for information
   and support.

LAVA V1
=======

V1 refers to the components of LAVA which are related to:

* JSON job submissions
* Bundles, BundleStreams and the ``submit_results`` action
* Image Reports and Image Reports 2.0

All code supporting V1 is deprecated as of the **2016.2 release** and
is scheduled to be removed from the codebase during 2017.

.. warning:: When the code objects implementing V1 are removed, the
   corresponding database records, tables, indexes and relationships
   will be **deleted** during later upgrades. Instances which want to
   continue using V1 from 2017 onwards **must not** install updates or
   **all V1 data will be lost**.

.. seealso:: `LAVA V1 <v1/index.html>`_

LAVA V2
=======

V2 refers to the **pipeline** model - a new design for how the test
job is constructed. It gives test writers much more freedom to write
new test jobs using new protocols and test methods, and it also
delivers a much simpler way of deploying distributed instances.

* YAML job submissions, supporting comments
* Results, Queries and Charts
* Live result reporting (no final submission stage)
* Simplified setup for distributed instances

The code supporting V2 is being extended to support a wider range of
devices and deployment methods. The migration to V2 is expected to last
until the end of 2016.

.. seealso:: `LAVA V2 <v2/index.html>`_


.. include:: support.rst
.. include:: tables.rst
