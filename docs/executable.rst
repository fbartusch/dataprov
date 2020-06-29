=====================
Executing Dataprov
=====================

This part of the documentation describes the ``snakemake`` executable.  Snakemake
is primarily a command-line tool, so the ``snakemake`` executable is the primary way
to execute, debug, and visualize workflows.

Useful Command Line Arguments
===================================

If called without parameters, i.e.

.. code-block:: console

    $ snakemake

Snakemake tries to execute the workflow specified in a file called ``Snakefile`` in the same directory (instead, the Snakefile can be given via the parameter ``-s``).

By issuing

.. code-block:: console

    $ snakemake -n

a dry-run can be performed.
This is useful to test if the workflow is defined properly and to estimate the amount of needed computation.
Further, the reason for each rule execution can be printed via


.. code-block:: console

    $ snakemake -n -r

Importantly, Snakemake can automatically determine which parts of the workflow can be run in parallel.
By specifying the number of available cores, i.e.

.. code-block:: console

    $ snakemake -j 4

one can tell Snakemake to use up to 4 cores and solve a binary knapsack problem to optimize the scheduling of jobs.
If the number is omitted (i.e., only ``-j`` is given), the number of used cores is determined as the number of available CPU cores in the machine.


-------------
Cloud Support
-------------

Snakemake 4.0 and later supports execution in the cloud via Kubernetes.
This is independent of the cloud provider, but we provide the setup steps for GCE below.


-------------
Visualization
-------------

To visualize the workflow, one can use the option ``--dag``.
This creates a representation of the DAG in the graphviz dot language which has to be postprocessed by the graphviz tool ``dot``.
E.g. to visualize the DAG that would be executed, you can issue:

.. code-block:: console

    $ snakemake --dag | dot | display

For saving this to a file, you can specify the desired format:

.. code-block:: console

    $ snakemake --dag | dot -Tpdf > dag.pdf

To visualize the whole DAG regardless of the eventual presence of files, the ``forceall`` option can be used:

.. code-block:: console

    $ snakemake --forceall --dag | dot -Tpdf > dag.pdf

Of course the visual appearance can be modified by providing further command line arguments to ``dot``.


.. _cwl_export:

----------
CWL export
----------

Snakemake workflows can be exported to `CWL <http://www.commonwl.org/>`_, such that they can be executed in any `CWL-enabled workflow engine <https://www.commonwl.org/#Implementations>`_.
Since, CWL is less powerful for expressing workflows than Snakemake (most importantly Snakemake offers more flexible scatter-gather patterns, since full Python can be used), export works such that every Snakemake job is encoded into a single step in the CWL workflow.
Moreover, every step of that workflow calls Snakemake again to execute the job. The latter enables advanced Snakemake features like scripts, benchmarks and remote files to work inside CWL.
So, when exporting keep in mind that the resulting CWL file can become huge, depending on the number of jobs in your workflow.
To export a Snakemake workflow to CWL, simply run

.. code-block:: console

    $ snakemake --export-cwl workflow.cwl

The resulting workflow will by default use the `Snakemake docker image <https://quay.io/repository/snakemake/snakemake>`_ for every step, but this behavior can be overwritten via the CWL execution environment.
Then, the workflow can be executed in the same working directory with, e.g.,

.. code-block:: console

    $ cwltool workflow.cwl

Note that due to limitations in CWL, it seems currently impossible to avoid that all target files (output files of target jobs), are written directly to the workdir, regardless of their relative paths in the Snakefile.


.. _all_options:

-----------
All Options
-----------

.. argparse::
   :module: dataprov.__main__
   :func: get_parser
   :prog: dataprov

   All command line options can be printed by calling ``dataprov -h``.