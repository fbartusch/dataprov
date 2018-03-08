# dataprov: Automatic provenance metadata generation

Dataprov is a wrapper that produces provenance metadata at the same time the data processing happens.

## Install

It's the best to install dataprov in a new conda environment:
[Howto install conda](https://conda.io/miniconda.html)

```
conda create -n dataprov python=3.6
source activate dataprov
```

Install dataprov

```
git clone git clone https://github.com/fbartusch/dataprov.git
cd dataprov
pip install .
```

### Install additonal packages.

You need to enable the [bioconda](https://bioconda.github.io/) channel for the examples in this README:

```
conda config --add channels defaults
conda config --add channels conda-forge
conda config --add channels bioconda
```

To try the 'First steps' examples without an the Docker container:

```
conda install bwa
```

To try the 'First steps' examples with the Docker container. This is just the Docker Python-API, you have to install Docker on your system, too.

```
pip install docker
```

For the snakemake example workflow:

```
pip install snakemake
pip install docutils

# Install samtools and bcftools
conda install samtools
conda install bcftools
```

To support CWL command line tools and workflows:

```
pip install cwltool==1.0.20180302231433
```


# First steps

A important part of the recorded metadata is **who** computed something.
This information is stored at `~/.dataprov/executor.conf`. If you start dataprov for the first time, the file will be created for you. You hjust have to fill in the information. 

```
$ dataprov
No personal information found at ~/.dataprov/executor.conf
An empy personal information file will be created at ~/.dataprov/executor.conf
Please fill this file with your personal information and try again.
```

## First Computation

The repository contains a very small reference genome. First we compute an index with bwa. 

```
# bwa is installed already
dataprov -i examples/bwa/genome.fa -o examples/bwa/genome.fa.bwt run bwa index examples/bwa/genome.fa

# bwa is not installed already
docker pull biocontainers/bwa
dataprov -i examples/bwa/genome.fa -o examples/bwa/genome.fa.bwt run docker run -v $PWD/examples/:/tmp/:z -it docker.io/biocontainers/bwa:latest bwa index /tmp/bwa/genome.fa
```

Everything after the keyword `run` is the command wrapped by dataprov. The `-i/--input` and `-o/--output` options tell dataprov the input/output files of the wrapped command.
You can take a look at the created metadata file at `data/index/genome.bwt.prov`.

```
ls -go examples/bwa/
total 629
-rw-r--r-- 1 234112 Feb 15 15:37 genome.fa
-rw-r--r-- 1   2598 Feb 15 15:40 genome.fa.amb
-rw-r--r-- 1     83 Feb 15 15:40 genome.fa.ann
-rw-r--r-- 1 230320 Feb 15 15:40 genome.fa.bwt
-rw-r--r-- 1   1658 Feb 15 15:40 genome.fa.bwt.prov
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

```
mkdir data/mapped_reads

# bwa installed
dataprov -i examples/bwa/genome.fa.bwt -i examples/bwa/A.fastq -o examples/bwa/mapped_reads/A.bam run 'bwa mem examples/bwa/genome.fa examples/bwa/A.fastq > examples/bwa/mapped_reads/A.bam'

# bwa not installed
dataprov -i examples/bwa/genome.fa.bwt -i examples/bwa/samples/A.fastq -o examples/bwa/mapped_reads/A.bam \
    run 'docker run -v $PWD/examples/:/tmp/:z  docker.io/biocontainers/bwa:latest bwa mem /tmp/bwa/genome.fa /tmp/bwa/samples/A.fastq > data/bwa/mapped_reads/A.bam'
```

The resulting metadata file inherits the metadata of the index file: `examples/bwa/mapped_reads/A.bam.prov`:

```
ls -go examples/bwa/mapped_reads/
total 6112
-rw-r--r-- 1 6254845 Feb 15 15:46 A.bam
-rw-r--r-- 1    3253 Feb 15 15:46 A.bam.prov
```

If you look into this file you will see that the history of `A.bam.prov` contains now two operations. The first operation describes how the index from the first step was computed. This operation element was inherited from the metadata file of the specified input. The second operation describes the mapping we just computed.


## Running Snakemake workflows

Under construction

## Running CWL CommandLineTools

Under construction!

Tool example. Needs input output because they are not parsed from CWL files yet.

```
dataprov -i hello.tar -o hello.txt run cwltool tar.cwl tar-job.yml
```

CWLTool example that uses docker container

```
dataprov run cwltool data/cwl/user_guide/arguments.cwl data/cwl/user_guide/arguments-job.yml
```

Workflow example:

```
cd data/cwl/tutorial
cwl-runner 1st-workflow.cwl 1st-workflow-job.yml
```
