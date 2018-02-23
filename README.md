# dataprov: Automatic provenance metadata generation

Dataprov is a wrapper that produces provenance metadata at the same time the data processing happens.

## Install

It's the best to install dataprov in a new conda environment.

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

## First steps

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
dataprov -i data/index/genome.fa -o data/index/genome.fa.bwt run bwa index data/index/genome.fa

# bwa is not installed already
docker pull biocontainers/bwa
dataprov -i data/index/genome.fa -o data/index/genome.fa.bwt run docker run -v $PWD/data/:/tmp/:z -it docker.io/biocontainers/bwa:latest bwa index /tmp/index/genome.fa
```

Everything after the keyword `run` is the command wrapped by dataprov. The `-i/--input` and `-o/--output` options tell dataprov the input/output files of the wrapped command.
Take a look at the created metadata file at `data/index/genome.bwt.prov`.

```
ls -go data/index/
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
dataprov -i data/index/genome.fa.bwt -i data/samples/A.fastq -o data/mapped_reads/A.bam run 'bwa mem data/index/genome.fa data/samples/A.fastq > data/mapped_reads/A.bam'

# bwa not installed
dataprov -i data/index/genome.fa.bwt -i data/samples/A.fastq -o data/mapped_reads/A.bam \
    run 'docker run -v $PWD/data/:/tmp/:z  docker.io/biocontainers/bwa:latest bwa mem /tmp/index/genome.fa /tmp/samples/A.fastq > data/mapped_reads/A.bam'
```

The resulting metadata file inherits the metadata of the index file: `data/mapped_reads/A.bam.prov`:

```
ls -go data/mapped_reads/
total 6112
-rw-r--r-- 1 6254845 Feb 15 15:46 A.bam
-rw-r--r-- 1    3253 Feb 15 15:46 A.bam.prov
```

## Running CWL CommandLineTools and Workflows

Tool example. Needs input output because they are not parsed from CWL files yet.

```
dataprov -i hello.tar -o hello.txt run cwltool tar.cwl tar-job.yml
```
```
cd data/cwl/tutorial
cwl-runner 1st-workflow.cwl 1st-workflow-job.yml
```
