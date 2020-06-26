.. _getting_started-installation:

============
Installation
============

Dataprov is available from GitHub. You can use pip to install Dataprov as Python package on your system, but we recommended to use a new Conda environment if you try Dataprov for the first time.

Create new Conda environment
============================

This is an optional step, but it is highly recommended to use a fresh conda environment for your first steps. This ensures that you don't mess up your Python environment with Dataprov's dependencies.
If you haven't installed conda already, `install the newest Miniconda release`_. Then you can create a new Conda environment for Dataprov.

.. _install the newest Miniconda release: https://conda.io/projects/conda/en/latest/user-guide/install/linux.html

.. code:: bash

    $ conda create -n dataprov python=3.7
    $ conda activate dataprov


Installation via PyPI
=====================

Just grab the official package from PyPI and you're good to go.
  
.. code:: bash

    $ pip install dataprov2

If you want to use additional features (like support for Snakemake workflows), you have to add this to the `pip install` command.

.. code:: bash

    $ pip install .[snakemake]

Currently, the features are:

- Provenance for operations using Singularity containers: `singularity`
- Provenance for operations using Docker containers: `docker`
- Provenance for Snakemake workflows: `snakemake`
- Provenance for CWL tools: `cwl`


Installation via Github
=======================

If you want the latest development version, install Dataprov via Github. If the conda environment is active, every dependency will be installed into it.

.. code:: bash

    $ git clone https://github.com/jonasgloning/dataprov2.git
    $ cd dataprov2
    $ pip install .

Using additional features is the same as for the installation from PyPI.


Build Documentation
===================

This is an optional step if you want to contribute to the documentation.
The dependencies for the documentation are installed via.

.. code:: bash

    $ pip install dataprov[docs]

The documentation is then created in the following way.

.. code:: bash

    $ # Rebuild api information if new functions/classes were added to the code
    $ cd docs
    $ sphinx-apidoc -o api/internal ../dataprov2

    $ # Build documentation in html format
    $ make html