.. _project_info-contributing:

============
Contributing
============


----------------------
Code Style and Quality
----------------------


Check Quality Before Commit / Pull Request
==========================================

Several :code:`pytest` extensions shall torture programmers (and ensure some kind of code quality) for
existing and new code.

* isort: Logical and alphabetical sorting of imports
* mypy: Static type checker to ensure suitable types. The type information for variables also give some implicit code documentation
* black: Ensure PEP 8 formatting (although it seems to sacrifices the 80 column line limit)
* pylint: Checks line length (inluding DocStrings, which are untouched by black), checking if variable names are well-formed according to coding standard, checking if imported modules are used

To run these tests, simply execute :code:`pytest`. The extensions are automatically added in :code:`pytest.ini`:

.. code-block:: bash

    # Install test requirements of dataprov
    pip install dataprov[testing]
    # Run tests
    rm -r .mypy_cache/ .pytest_cache/
    pytest .

If these tests return no errors and warnings, feel free to create a pull request.


String Formatting (Especially for Logging)
==========================================

Please use the standard string formatting of Python 3. Otherwise the quality checks report warnings.

.. code-block:: python

    # String formatting OK
    logging.warning("Key in executor ini-file not supported: {}".format(key))

    # String formatting throws errors during pytest -> NOT OK
    logging.warning("Key in executor ini-file not supported: %s", key)

    # f-Strings only works for Python 3.6+ -> NOT OK
    logging.warning(f"Key in executor ini-file not supported: {key}")


---------------------
Dependency Management
---------------------


Adding new Dependencies
=======================

Dataprov's dependencies are stated in the `setup.py` file in the project's root directory.
This is good practice for Python projects.
The main dependencies are stated in the `install_requires` section of `setup.py`.
These basic dependencies should be very minimalistic.
This means, do not add additional dependencies, except it is really necessary.
Also a dependency's version range should be really vague.
This should allow the user to install additional Python packages without getting problems with unfulfillable version constraints.

Dataprov offers functionality for software that is not installed on every computer, like Docker and Singularity.
Python package dependencies handling these special features are listed in the `extras_require` section of `setup.py`.
Dependencies for `pytest` and for creating the documentation are also stated in the `extras_require` section.
As a consequence users has to install these packages only if they want to build documentation or want to run `pytest`.

The following command should install dependencies for each functionality.

.. code-block:: bash

    pip install dataprov[testing,docs,singularity,cwl,docker,snakemake]

In addition to the vague dependency declaration in `setup.py`, we offer a `requirements.txt` file in the projects root directory.
The `requirements.txt` lists every dependency with an exact version needed for every Dataprov feature.
It is created using `pip-compile` on the `setup.py` file.

.. code-block:: bash

    echo "-e .[testing,docs,docker,singularity,snakemake,cwl]" | pip-compile - -qo- | sed '/^-e / d' > requirements.txt


----------------------
Types of Contributions
----------------------


Report Bugs
===========

Report bugs at https://github.com/jonasgloning/dataprov2/issues

If you are reporting a bug, please include:

* Your operating system name and version.
* Dataprov version or commit
* Any details about your local setup that might be helpful in troubleshooting.
* Detailed steps to reproduce the bug.
* Optimal would be a minimal dataset and script reproducing the bug.


Contributing a command or operation
===================================

Command backends are added by implementing an ``Operation``.
All operations are located in `dataprov2/Operations <https://github.com/jonasgloning/dataprov2/tree/master/dataprov2/Operations>`_.
In order to implement a new operation, you have to inherit from the class ``GenericOperation``.
Below you find a skeleton

.. code-block:: python

    class MyCoolNewCommand(GenericOperation):
        """What's your command? and How do you implemented it?"""

        def run(self) -> None:
            """
            Declare this function, if you want to change how your command is run
            e.g. parsing and modifying the command string

            Log STDOUT with logging.info & STDERR with logging.warning
            """
            pass

        def delay(self) -> None:
            """
            Declare this function, if you want to read the files created by the command
            e.g. importing generated metadata
            """
            pass


Write Documentation
===================

Dataprov could always use more documentation, whether as part of the official vcfpy docs, in DocStrings, or even on the web in blog posts, articles, and such.

We use `Sphinx <https://sphinx-doc.org>`_ for the user manual (that you are currently reading).
Have a look in the installation section for instructions that rebuild this documentation


Submit Feedback
===============

The best way to send feedback is to file an issue at https://github.com/jonasgloning/dataprov2/issues
You can also write a mail to felix.bartusch(at)uni-tuebingen.de.


