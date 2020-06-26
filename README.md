<h1 align="center">dataprov: Automatic provenance metadata generation</h1>

<p align="center">
<a href="https://dev.azure.com/zdv-dataprov/fluent_prov/_build/latest?definitionId=3&branchName=master"><img alt="Build Status" src="https://dev.azure.com/zdv-dataprov/fluent_prov/_apis/build/status/jonasgloning.dataprov2?branchName=master"></a>
<a href="https://codecov.io/gh/jonasgloning/dataprov2"><img alt="codecov" src="https://codecov.io/gh/jonasgloning/dataprov2/branch/master/graph/badge.svg?token=uRydlkWAt0"></a>
<a href="https://www.codefactor.io/repository/github/jonasgloning/dataprov2"><img alt="CodeFactor" src="https://www.codefactor.io/repository/github/jonasgloning/dataprov2/badge"></a>
<a href="https://github.com/python/black"><img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg"></a>
<a href="https://dependabot.com"><img alt="Dependabot Status" src="https://api.dependabot.com/badges/status?host=github&repo=jonasgloning/dataprov2&identifier=187416501"></a>
</p>


Dataprov is a wrapper that produces provenance metadata at the same time the data processing happens.

## Install

It's recommended to install dataprov in a new conda environment:
[Howto install conda](https://conda.io/miniconda.html)

```bash
$ conda create -n dataprov python=3.7

$ source activate dataprov # for bash
$ conda  activate dataprov # for any other shell
```

Install dataprov

```bash
$ pip install dataprov2
```

### Install additonal packages.

<!-- You need to enable the [bioconda](https://bioconda.github.io/) channel for the examples in this README:

```bash
$ conda config --add channels bioconda
```

To try the 'First steps' examples without an the Docker container:

```bash
$ conda install bwa
``` -->

For the snakemake example workflow:

```bash
$ pip install snakemake
$ pip install docutils

# Install samtools and bcftools
$ conda install samtools
$ conda install bcftools
```

To support CWL command line tools and workflows:

```bash
$ pip install cwltool
```


# First steps

A important part of the recorded metadata is **who** computed something.
This information is stored at `~/.dataprov/executor.conf`. If you start dataprov for the first time, the file will be created for you. You hjust have to fill in the information.

```bash
$ dataprov
No personal information found at ~/.dataprov/executor.conf
An empy personal information file will be created at ~/.dataprov/executor.conf
Please fill this file with your personal information and try again.
```

## First Computation

The repository contains a very small reference genome. First we compute an index with bwa.

```bash
# bwa is installed already
$ dataprov -i examples/bwa/genome.fa -o examples/bwa/genome.fa.bwt run bwa index examples/bwa/genome.fa

# Using Conda
$ conda config --add channels conda-forge bioconda # https://bioconda.github.io/
$ conda install bwa
$ dataprov -i examples/bwa/genome.fa -o examples/bwa/genome.fa.bwt run bwa index examples/bwa/genome.fa

# Using Docker
$ dataprov -i examples/bwa/genome.fa -o examples/bwa/genome.fa.bwt run docker run -v $PWD/examples/:/tmp/:z -it biocontainers/bwa:v0.7.15_cv4 bwa index /tmp/bwa/genome.fa

# Using Singularity
$ dataprov -i examples/bwa/genome.fa -o examples/bwa/genome.fa.bwt run singularity exec bwa.simg bwa index examples/bwa/genome.fa
```

Everything after the keyword `run` is the command wrapped by dataprov. The `-i/--input` and `-o/--output` options tell dataprov the input/output files of the wrapped command.
You can take a look at the created metadata file at `examples/bwa/genome.fa.bwt.prov.xml`.

```bash
$ ls -go examples/bwa/
-rw-r--r-- 1 234112 Feb 15 15:37 genome.fa
-rw-r--r-- 1   2598 Feb 15 15:40 genome.fa.amb
-rw-r--r-- 1     83 Feb 15 15:40 genome.fa.ann
-rw-r--r-- 1 230320 Feb 15 15:40 genome.fa.bwt
-rw-r--r-- 1  18456 Feb 15 15:40 genome.fa.bwt.prov.svg
-rw-r--r-- 1   6476 Feb 15 15:40 genome.fa.bwt.prov.xml
-rw-r--r-- 1  57556 Feb 15 15:40 genome.fa.pac
-rw-r--r-- 1 115160 Feb 15 15:40 genome.fa.sa
```

It's an xml-file answering the following questions:

  * **Who** computed the result?
  * **When** was the result computed?
  * **How** was the result computed?
  * **What Input** files were used?
  * **How** were the **input files** computed?
  * On which machine were the computation executed?
  * Was the input/output data changed?

## Second computation: Inherit metadata

We can also incorporate existing metadata into the metadata of new computations. We map now a small set of reads against the previously computed index.

```bash
$ mkdir data/mapped_reads

# bwa installed
$ dataprov -i examples/bwa/genome.fa.bwt -i examples/bwa/samples/A.fastq -o examples/bwa/mapped_reads/A.bam run 'bwa mem examples/bwa/genome.fa examples/bwa/samples/A.fastq > examples/bwa/mapped_reads/A.bam'

# bwa not installed
# Using Docker
$ dataprov -i examples/bwa/genome.fa.bwt -i examples/bwa/samples/A.fastq -o examples/bwa/mapped_reads/A.bam \
    run 'docker run -v $PWD/examples/:/tmp/:z  docker.io/biocontainers/bwa:latest bwa mem /tmp/bwa/genome.fa /tmp/bwa/samples/A.fastq > examples/bwa/mapped_reads/A.bam'

# Using Singularity
$ dataprov -i examples/bwa/genome.fa.bwt -i examples/bwa/samples/A.fastq -o examples/bwa/mapped_reads/A.bam \
    run 'singularity exec bwa.simg bwa mem examples/bwa/genome.fa examples/bwa/samples/A.fastq > examples/bwa/mapped_reads/A.bam'
```

This command produces a mapping result file and the corresponding provenance file:

```bash
$ ls -go examples/bwa/mapped_reads/
total 6112
-rw-r--r-- 1 6254845 Feb 15 15:46 A.bam
-rw-r--r-- 1    3253 Feb 15 15:46 A.bam.prov
```

If you look into this file you will see that the history of `A.bam.prov` contains now two operations. The first operation describes how the index from the first step was computed. This operation element was inherited from the metadata file of the specified input. The second operation describes the mapping we just computed.


## Running Snakemake workflows

The directory `examples/snakemake` contains the snakemake tutorial workflow and example data.

```bash
$ cd examples/snakemake
$ dataprov run snakemake all
```

This will run the workflow and creates a provenance file for each of the eight output files:

```bash
$ ls -go . calls/ mapped_reads/ sorted_reads/
.:
total 104
drwxrwxr-x. 2    41 Mar 27 16:00 calls
drwxrwxr-x. 2    68 Mar 27 16:00 mapped_reads
-rw-rw-r--. 1 92876 Mar 15 16:11 report.html
-rw-rw-r--. 1 11974 Mar 27 16:00 report.html.prov
drwxrwxr-x. 2   146 Mar 27 16:00 sorted_reads

calls/:
total 80
-rw-rw-r--. 1 66927 Mar 15 16:11 all.vcf
-rw-rw-r--. 1 11977 Mar 27 16:00 all.vcf.prov

mapped_reads/:
total 4436
-rw-rw-r--. 1 2256008 Mar 15 16:11 A.bam
-rw-rw-r--. 1   11980 Mar 27 16:00 A.bam.prov
-rw-rw-r--. 1 2259659 Mar 15 16:11 B.bam
-rw-rw-r--. 1   11980 Mar 27 16:00 B.bam.prov

sorted_reads/:
total 4444
-rw-rw-r--. 1 2242429 Mar 15 16:11 A.bam
-rw-rw-r--. 1     344 Mar 15 16:11 A.bam.bai
-rw-rw-r--. 1   11988 Mar 27 16:00 A.bam.bai.prov
-rw-rw-r--. 1   11980 Mar 27 16:00 A.bam.prov
-rw-rw-r--. 1 2245385 Mar 15 16:11 B.bam
-rw-rw-r--. 1     344 Mar 15 16:11 B.bam.bai
-rw-rw-r--. 1   11988 Mar 27 16:00 B.bam.bai.prov
-rw-rw-r--. 1   11980 Mar 27 16:00 B.bam.prov
```

## Running CWL CommandLineTools

This is one example from the CWL user guide. It just untars a tar archive that contains just one file.

```bash
$ cd examples/cwl_command_line
$ dataprov -i hello.tar -o hello.txt run cwltool tar.cwl tar-job.yml
```

This example used Java installed in a Docker container to create a class file from Java source code.
The example shows that dataprov can infer the name of the resulting class file from the information provided by the .cwl and .yml file.
It could be the case that you have to disable SELinux to run the Docker container (more precise: allow writing in mounted volumes).

```bash
$ cd examples/cwl_command_line
$ dataprov run cwltool arguments.cwl arguments-job.yml
```

# Documentation

## XML Schema

The generated provenance files follow the XML schema provided with this repository. The schema documentation can be found under `xml/schema_doc`.
The documentation was built with `xsltproc` using the [xs3p XSLT stylesheet](https://xml.fiforms.org/xs3p/) and can be viewed in a browser.
