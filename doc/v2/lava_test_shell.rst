.. _lava_test_shell:

LAVA Test Shell
***************

The ``lava_test_shell`` action provides a way to employ a more black-box style
testing appoach with the target device. The test definition format is quite
flexible and allows for some interesting things.

Quick start
===========

A minimal test definition looks like this::

  metadata:
    name: passfail
    format: "Lava-Test-Shell Test Definition 1.0"
    description: "A simple passfail test for demo."
    os:
      - ubuntu
      - openembedded
    devices:
      - origen
      - panda
    environment:
      - lava-test-shell

  params:
    TEST_1: pass

  run:
    steps:
      - echo "test-1: $TEST_1"
      - echo "test-2: fail"

  parse:
    pattern: "(?P<test_case_id>.*-*):\\s+(?P<result>(pass|fail))"

.. note::  The parse pattern has similar quoting rules as Python, so
          \\s must be escaped as \\\\s and similar.

However, the parameters such as os, devices, environment are optional in
the metadata section. On the other hand parameters such as name, format,
description are mandatory in the metadata section.

.. _versioned_test_definitions:

Versioned test definitions
--------------------------

If your test definition is not part of a bzr or git repository then it
is mandatory to have a **version** parameter in metadata section. The
following example shows how a test definition metadata section will
look like for a test definition which is not part of bzr or git
repository::

  metadata:
    name: passfail
    format: "Lava-Test-Shell Test Definition 1.0"
    version: "1.0"
    description: "A simple passfail test for demo."
    os:
      - ubuntu
      - openembedded
    devices:
      - origen
      - panda
    environment:
      - lava-test-shell

.. note:: Only if the test definition is referred from a URL the
          version parameter should be explicit.

.. _lava_test_shell_setx:

How a lava test shell is run
----------------------------

A lava-test-shell is run by:

* *compiling* the above test defintion into a shell script.

   .. note:: This shell script will have a ``set -e`` at the top, so a
          failing step will abort the entire test run. If you need to specify
          a step that might fail, but should not cause the run to be aborted,
          make sure you finish the command with ``|| true``.

* copying this script onto the device and arranging for it to be run
  when the device boots
* booting the device and letting the test run
* retrieving the output from the device and turning it into a test
  result bundle
* run subsequent test definitions, if any.

Writing a test for lava-test-shell
==================================

For the majority of cases, the above approach is the easiest thing to
do: write shell code that outputs "test-case-id: result" for each test
case you are interested in.  See the Test Developer Guide:

 * :ref:`test_developer`,
 * :ref:`writing_tests`
 * :ref:`parsing_output`.

The advantage of the parsing approach is that it means your test is
easy to work on independently from LAVA: simply write a script that
produces the right sort of output, and then provide a very small
amount of glue to wire it up in LAVA.  However, when you need it,
there is also a more powerful, LAVA-specific, way of writing tests.
When a test runs, ``$PATH`` is arranged so that some LAVA-specific
utilities are available:

 * ``lava-test-case``
 * ``lava-test-case-attach``
 * ``lava-test-run-attach``
 * ``lava-background-process-start``
 * ``lava-background-process-stop``

lava-test-case
--------------

lava-test-case records the results of a single test case. For example::

  steps:
    - "lava-test-case simpletestcase --result pass"
    - "lava-test-case fail-test --shell false"

It has two forms.  One takes arguments to describe the outcome of the
test case and the other takes the shell command to run -- the exit
code of this shell command is used to produce the test result.

Both forms take the name of the testcase as the first argument.

Specifying results directly
^^^^^^^^^^^^^^^^^^^^^^^^^^^

The first form takes these additional arguments:

 * ``--result $RESULT``: $RESULT should be one of pass/fail/skip/unknown
 * ``--measurement $MEASUREMENT``: A numerical measurement associated with the test result
 * ``--units $UNITS``: The units of $MEASUREMENT

``--result`` must always be specified.  For example::

  run:
    steps:
      - "lava-test-case simpletestcase --result pass"
      - "lava-test-case bottle-count --result pass --measurement 99 --units bottles"

If ``--measurement`` is used, ``--units`` must also be specified, even
if the unit is just a count.

The most useful way to produce output for ``lava-test-case result`` is
:ref:`custom_scripts` which allow preparation of LAVA results from other
sources, complete with measurements. This involves calling ``lava-test-case``
from scripts executed by the YAML file::

 #!/usr/bin/env python

 from subprocess import call


 def test_case():
     """
     Calculate something based on a test
     and return the data
     """
     return {"name": "test-rate", "result": "pass",
         "units": "Mb/s", "measurement": 4.23}


 def main():
     data = test_case()
     call(
         ['lava-test-case',
          data['name'],
          '--result', data['result'],
          '--measurement', data['measurement'],
          '--units', data['units']])
     return 0

 if __name__ == '__main__':
     main()

The custom scripts themselves can be called from a ``lava-test-case``
using the ``--shell`` command to test whether failures from the tests
caused a subsequent failure in the custom script.

Using the exit status of a command
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The second form of ``lava-test-case`` is indicated by the ``--shell``
argument, for example::

  run:
    steps:
      - "lava-test-case fail-test --shell false"
      - "lava-test-case pass-test --shell true"

The result of a ``shell`` call will only be recorded as a pass or fail,
dependent on the exit code of the command. The output of the command
can, however, be parsed as a separate result if the command produces
output suitable for the parser in the YAML::

 run:
    steps:
    - lava-test-case echo2 --shell echo "test2b:" "fail"
 parse:
    pattern: "(?P<test_case_id>.*-*):\\s+(?P<result>(pass|fail))"

This example generates **two** test results to indicate that the
shell command executed correctly but that the result of that
execution was a fail::

#. **echo2** - pass
#. **test2b** - fail

lava-test-case-attach
---------------------

.. caution:: ``lava-test-case-attach`` is retained with the
   dispatcher refactoring but the effect of the script needs
   consideration by the test writer. See :ref:`test_attach`.

This attaches a file to a test result with a particular ID, for example::

  steps:
    - "echo content > file.txt"
    - "lava-test-case test-attach --result pass"
    - "lava-test-case-attach test-attach file.txt text/plain"

The arguments are:

 1. test case id
 2. the file to attach
 3. (optional) the MIME type of the file (if no MIME type is passed, a
    guess is made based on the filename)

lava-test-run-attach
--------------------

.. caution:: ``lava-test-run-attach`` is retained with the
   dispatcher refactoring but the effect of the script needs
   consideration by the test writer. See :ref:`test_attach`.

This attaches a file to the overall test run that lava-test-shell is
currently executing, for example::

  steps:
    - "echo content > file.txt"
    - "lava-test-run-attach file.txt text/plain"

The arguments are:

 1. the file to attach
 2. (optional) the MIME type of the file (if no MIME type is passed, a
    guess is made based on the filename)

lava-background-process-start
-----------------------------

This starts process in the background.
For example::

  steps:
    - lava-background-process-start MEM --cmd "free -m | grep Mem | awk '{print $3}' >> /tmp/memusage"
    - lava-background-process-start CPU --cmd "grep 'cpu ' /proc/stat"
    - uname -a
    - lava-background-process-stop CPU
    - lava-background-process-stop MEM --attach /tmp/memusage text/plain --attach /proc/meminfo application/octet-stream

The arguments are:

 1. Name that is used to identify the process later in
    lava-background-process-stop
 2. The process to be run in the background

See :ref:`test_attach`.

lava-background-process-stop
-----------------------------

This stops the process previously started in the background. User can attach files to the test run if there is a need.

For example::

  steps:
    - lava-background-process-start MEM --cmd "free -m | grep Mem | awk '{print $3}' >> /tmp/memusage"
    - lava-background-process-start CPU --cmd "grep 'cpu ' /proc/stat"
    - uname -a
    - lava-background-process-stop CPU
    - lava-background-process-stop MEM --attach /tmp/memusage text/plain --attach /proc/meminfo application/octet-stream

The arguments are:

 1. Name that was specified in lava-background-process-start
 2. (optional) Indicate if you want to attach file(s) the test run
    with specified mime type. See :ref:`test_attach`.

.. _test_attach:

Handling test attachments
=========================

The deprecated dispatcher support for test attachments depends on the
deprecated bundle and `bundle stream` support - the scripts
available in lava-test shell do not actually attach the requested files,
just copy the files to a hard-coded directory where the bundle
processing code expects to find data to put into the bundle. This
relies on the device being booted into an environment with a working
network connection - what was called the master image.

In the pipeline support, master images and bundles have been removed. This
puts the handling of attachments into the control of the test writer. An
equivalent method would be to simply add another deploy and boot action
to get into an environment where the network connection is known to work,
however the eventual location of the file needs to be managed by the
test writer. An alternative method for text based data is simply to
output the contents into the log file. (Individual parts of the log
file can be downloaded separately.)

.. _handling_dependencies:

Handling Dependencies (Debian)
==============================

If your test requires some packages to be installed before its run it can
express that in the ``install`` section with::

  install:
      deps:
          - linux-libc-dev
          - build-essential

.. _adding_repositories:

Adding Git/BZR Repositories
===========================

If your test needs code from a shared repository, the action can clone this
data on your behalf with::

  install:
      bzr-repos:
          - lp:lava-test
      git-repos:
          - git://git.linaro.org/people/davelong/lt_ti_lava.git

  run:
      steps:
          - cd lt_ti_lava
          - echo "now in the git cloned directory"

This repository information will also be added to resulting bundle's software
context when the results are submitted to the LAVA dashboard.

git-repos
---------
The git-repos section shown above can be customized as follows::

  install:
      git-repos:
          - url: https://git.linaro.org/lava/lava-dispatcher.git
            skip_by_default: False
          - url: https://git.linaro.org/lava/lava-dispatcher.git
            destination:  lava-d-r
            branch:       release
          - url: https://git.linaro.org/lava/lava-dispatcher.git
            destination:  lava-d-s
            branch:       staging

* `url` is the git repository URL.
* `skip_by_default` (optional) accepts a True or False. Repositories
  can be skipped by default in the YAML and enabled for particular
  jobs in the JSON. Similarly, repositories can be set to install by
  default and be disabled for particular jobs in the JSON.
* `destination` (optional) is the directory in which the git
  repository given in `url` should be cloned.
* `branch` (optional) is the branch within the git repository given in
  `url` that should be cloned.

All the above parameters within the `git-repos` section could be
controlled from the JSON job file. See the following JSON job
definition and YAML test definition to get an understanding of how it works.

.. * JSON job definition - https://git.linaro.org/people/senthil.kumaran/job-definitions.git/blob/HEAD:/kvm-git-params-custom.json

* YAML test definition - https://git.linaro.org/people/senthil.kumaran/test-definitions.git/blob/HEAD:/debian/git-params-controlled.yaml

.. TODO: parameter support.

Install Steps
=============

Before the test shell code is executed, it will optionally do some install
work if needed. For example if you needed to build some code from a git repo
you could do::

  install:
      git-repos:
          - git://git.linaro.org/people/davelong/lt_ti_lava.git

      steps:
          - cd lt_ti_lava
          - make

.. note:: The repo steps are done in the dispatcher itself. The install steps
          are run directly on the target.

Advanced Parsing
================

You may need to incorporate an existing test that doesn't output results in
in the required ``pass``/``fail``/``skip``/``unknown`` format required by
LAVA. The parse section has a fixup mechanism that can help::

  parse:
      pattern: "(?P<test_case_id>.*-*)\\s+:\\s+(?P<result>(PASS|FAIL))"
      fixupdict:
          PASS: pass
          FAIL: fail

.. note:: Pattern can be double-quoted or single quoted. If it's double-quoted,
          special characters need to be escaped. Otherwise, no escaping is
          necessary.

Single quote example::

  parse:
      pattern: '(?P<test_case_id>.*-*)\s+:\s+(?P<result>(PASS|FAIL))'
      fixupdict:
          PASS: pass
          FAIL: fail

Adding dependent test cases
===========================

If your test depends on other tests to be executed before you run the
current test, the following definition will help::

  test-case-deps:
    - git-repo: git://git.linaro.org/qa/test-definitions.git
      testdef: common/passfail.yaml
    - bzr-repo: lp:~stylesen/lava-dispatcher/sampletestdefs-bzr
      testdef: testdef.yaml
    - url: http://people.linaro.org/~senthil.kumaran/deps_sample.yaml

The test cases specified within 'test-case-deps' section will be
fetched from the given repositories or url and then executed in the
same specified order. Following are valid repository or url source
keys that can be specified inside the 'test-case-deps' section::

 1. git-repo
 2. bzr-repo
 3. tar-repo
 4. url

.. note:: For keys such as git-repo, bzr-repo and tar-repo testdef name
          within this repo must be specfied with *testdef* parameter else
          *lavatest.yaml* is the name assumed.

.. _circular_dependencies:

.. caution:: lava-test-shell does not take care of circular dependencies
             within these test definitions. If a test definition say ``tc1.yaml``
             is specified within ``test-case-deps`` section of ``tc-main.yaml`` and in
             ``tc1.yaml`` there is a ``test-case-deps`` section which refers to
             ``tc-main.yaml`` then this will create a **circular dependency**.
             ``lava-test-shell`` will fetch the test definitions ``tc1.yaml`` and
             ``tc-main.yaml`` indefinitely and fail after timeout. The log
             for such cases would show many attempts at ``loading test definition...``.
