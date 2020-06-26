.. getting_started-first_steps:

===========
First steps
===========

Personal Information
====================

An important part of the recorded metadata is **who** computed something, e.g. who executed a command/pipeline/workflow/etc.
Information about a person existing in real life is stored in a configuration file at ``~/.dataprov/executor.conf``.
A person can belong to one or more institution. These intitutions can also be described in configuration files. Let's look how this works in practice.

If you start Dataprov for the first time, an empyt template will be created for you. You just have to fill in the information. They will automatically incorporated into the metadata later.

.. code::

   $ dataprov

   No personal information found at: /home/centos/.dataprov/executor.ini
   An empty personal information file will be created at: /home/centos/.dataprov/executor.ini
   Please fill this file with your personal information and try again.

   No organisational information found at /home/centos/.dataprov/organisation.ini
   An empty organisational information file will be created at: /home/centos/.dataprov/organisation.ini
   If desired, fill this file with information about your organisation.
   Specify then the path to this file in your personal information file

In this example the home directory is ``/home/centos``, as we tested the tool in a CentOS virtual machine. A fictional professor, who even possesses an `ORCID iD`_, is used as an example throughout the first steps tutorial.

.. _ORCID iD: https://orcid.org/0000-0002-1825-0097

.. code-block:: ini

   [executor]
   title = Prof.
   firstname = Josiah
   middlename = Stinkney
   surname = Carberry 
   suffix = 
   mail =
   orcid = 0000-0002-1825-0097 

   [affiliations]
   organisationfile = organisation.ini

.. code-block:: ini

    [organisation]
    title = Brown University
    mail = 
    linkedin = 
    github = 
    web = https://library.brown.edu/hay/carberry.php


First Computation
=================

The Dataprov repository contains a small test dataset, which was taken from the Snakemake tutorial. The dataset consists of a small reference genome and two sets of reads.
First, we create a reference using the popular tool ``bwa``. You have to install ``bwa``. If you used conda for installing Dataprov, you may also want to use conda for installing ``bwa``. You can also use Docker or Singularity containers if you want. This first computation will show you:

- How to specify input and output files for single commands
- How the resulting metadata file will look

.. code:: bash

    # bwa is installed already
    $ dataprov -i examples/bwa/genome.fa -o examples/bwa/genome.fa.bwt run bwa index examples/bwa/genome.fa

    # Using Conda
    $ conda config --add channels conda-forge
    $ conda config --add channels bioconda
    $ conda install bwa=0.7.17
    $ dataprov -i examples/bwa/genome.fa -o examples/bwa/genome.fa.bwt run bwa index examples/bwa/genome.fa

    # Using Docker
    $ dataprov -i examples/bwa/genome.fa -o examples/bwa/genome.fa.bwt run docker run -v $PWD/examples/:/tmp/:z -it biocontainers/bwa:v0.7.15_cv4     bwa index /tmp/bwa/genome.fa

    # Using Singularity
    $ dataprov -i examples/bwa/genome.fa -o examples/bwa/genome.fa.bwt run singularity exec bwa.simg bwa index examples/bwa/genome.fa



Everything after the keyword `run` is the command wrapped by dataprov.
The `-i/--input` and `-o/--output` options tell dataprov the input/output files of the wrapped command.
You can take a look at the created metadata file at `examples/bwa/genome.fa.bwt.prov.xml`.

.. code:: bash

   $ ls -go examples/bwa/
   -rw-r--r-- 1 234112 Feb 15 15:37 genome.fa
   -rw-r--r-- 1   2598 Feb 15 15:40 genome.fa.amb
   -rw-r--r-- 1     83 Feb 15 15:40 genome.fa.ann
   -rw-r--r-- 1 230320 Feb 15 15:40 genome.fa.bwt
   -rw-r--r-- 1  18456 Feb 15 15:40 genome.fa.bwt.prov.svg
   -rw-r--r-- 1   6476 Feb 15 15:40 genome.fa.bwt.prov.xml
   -rw-r--r-- 1  57556 Feb 15 15:40 genome.fa.pac
   -rw-r--r-- 1 115160 Feb 15 15:40 genome.fa.sa

It's an xml-file answering the following questions:

  * **Who** computed the result?
  * **When** was the result computed?
  * **How** was the result computed?
  * **What Input** files were used?
  * **How** were the **input files** computed?
  * On which machine were the computation executed?
  * Was the input/output data changed?

Second computation: Inherit metadata
===========================================

We can also incorporate existing metadata into the metadata of new computations.
We map now a small set of reads against the previously computed index.

.. code:: bash

  $ mkdir data/mapped_reads

  # bwa installed
  $ dataprov -i examples/bwa/genome.fa.bwt -i examples/bwa/samples/A.fastq -o examples/bwa/mapped_reads/A.bam run 'bwa mem examples/bwa/genome.fa   examples/bwa/samples/A.fastq > examples/bwa/mapped_reads/A.bam'

  # bwa not installed
  # Using Docker
  $ dataprov -i examples/bwa/genome.fa.bwt -i examples/bwa/samples/A.fastq -o examples/bwa/mapped_reads/A.bam \
      run 'docker run -v $PWD/examples/:/tmp/:z  docker.io/biocontainers/bwa:latest bwa mem /tmp/bwa/genome.fa /tmp/bwa/samples/A.fastq >   examples/bwa/mapped_reads/A.bam'

  # Using Singularity
  $ dataprov -i examples/bwa/genome.fa.bwt -i examples/bwa/samples/A.fastq -o examples/bwa/mapped_reads/A.bam \
      run 'singularity exec bwa.simg bwa mem examples/bwa/genome.fa examples/bwa/samples/A.fastq > examples/bwa/mapped_reads/A.bam'

This command produces a mapping result file and the corresponding provenance file:

.. code:: bash

  $ ls -go examples/bwa/mapped_reads/
  total 6112
  -rw-r--r-- 1 6254845 Feb 15 15:46 A.bam
  -rw-r--r-- 1    3253 Feb 15 15:46 A.bam.prov

If you look into this file you will see that the history of `A.bam.prov` contains now two operations.
The first operation describes how the index from the first step was computed.
This operation element was inherited from the metadata file of the specified input.
The second operation describes the mapping we just computed.


.. Running Snakemake workflows
.. ===========================

.. The directory `examples/snakemake` contains the snakemake tutorial workflow and example data.

.. .. code:: bash

..   $ cd examples/snakemake
..   $ dataprov run snakemake all

.. This will run the workflow and creates a provenance file for each of the eight output files:

.. .. code:: bash

..    $ ls -go . calls/ mapped_reads/ sorted_reads/
..    .:
..    total 104
..    drwxrwxr-x. 2    41 Mar 27.. toctree::
   :caption: Getting started
   :name: getting_started
   :hidden:
   :maxdepth: 1

   getting_started/installation
   getting_started/examples
   tutorial/tutorial
   tutorial/short 16:00 calls
..    drwxrwxr-x. 2    68 Mar 27 16:00 mapped_reads
..    -rw-rw-r--. 1 92876 Mar 15 16:11 report.html
..    -rw-rw-r--. 1 11974 Mar 27 16:00 report.html.prov
..    drwxrwxr-x. 2   146 Mar 27 16:00 sorted_reads

..    calls/:
..    total 80
..    -rw-rw-r--. 1 66927 Mar 15 16:11 all.vcf
..    -rw-rw-r--. 1 11977 Mar 27 16:00 all.vcf.prov

..    mapped_reads/:
..    total 4436
..    -rw-rw-r--. 1 2256008 Mar 15 16:11 A.bam
..    -rw-rw-r--. 1   11980 Mar 27 16:00 A.bam.prov
..    -rw-rw-r--. 1 2259659 Mar 15 16:11 B.bam
..    -rw-rw-r--. 1   11980 Mar 27 16:00 B.bam.prov

..    sorted_reads/:
..    total 4444
..    -rw-rw-r--. 1 2242429 Mar 15 16:11 A.bam
..    -rw-rw-r--. 1     344 Mar 15 16:11 A.bam.bai
..    -rw-rw-r--. 1   11988 Mar 27 16:00 A.bam.bai.prov
..    -rw-rw-r--. 1   11980 Mar 27 16:00 A.bam.prov
..    -rw-rw-r--. 1 2245385 Mar 15 16:11 B.bam
..    -rw-rw-r--. 1     344 Mar 15 16:11 B.bam.bai
..    -rw-rw-r--. 1   11988 Mar 27 16:00 B.bam.bai.prov
..    -rw-rw-r--. 1   11980 Mar 27 16:00 B.bam.prov

Running CWL CommandLineTools
==================================

This is one example from the CWL user guide.
It just untars a tar archive that contains just one file.

.. code:: bash

   $ cd examples/cwl_command_line
   $ dataprov -i hello.tar -o hello.txt run cwltool tar.cwl tar-job.yml

This example used Java installed in a Docker container to create a class file from Java source code.
The example shows that dataprov can infer the name of the resulting class file from the information provided by the .cwl and .yml file.
It could be the case that you have to disable SELinux to run the Docker container (more precise: allow writing in mounted volumes).

.. code:: bash

   $ cd examples/cwl_command_line
   $ dataprov run cwltool arguments.cwl arguments-job.yml
