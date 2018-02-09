# dataprov: Automatic provenance data generation

## Install

Create new Python 3 environment

```
conda create -n dataprov python=3.6
source activate dataprov
```

Install dataprov

```
git clone git clone https://github.com/fbartusch/cwltool.git
cd dataprov
pip install .
```

TODO
Create executor information

Install cwltool, the reference CWL implementation.

```
pip install cwlref-runner
```

## Usage

dataprov is a wrapper that executes CWLCommandLineTools and CWLWorkflows.
dataprov will examine the .cwl file and the input files given and creates provenance data for the resulting files.

### Example: Compute reference index with bwa on command line

First, get bwa from the  biocontainer project.

```
docker pull biocontainers/bwa
```

Get the reference genome. We will use data from a snakemake tutorial for this purpose. The command downloads the archive, untars it into the data directory and annotates the genome.fa file. Usually the wrapped command needs no quotes, but here they are needed because of the '&&'.

```
dataprov -d -o data/genome.fa -m "Download of snakemake tutorial test data" run 'wget https://bitbucket.org/snakemake/snakemake-tutorial/get/v3.11.0.tar.bz2 && mkdir data && tar xvjf  v3.11.0.tar.bz2 -C data --strip-components 2'
```

Run bwa in the biocontainer. The command is wrapped by dataprov and genome.fa.bwt is annotated with provenance metadata. 

```
dataprov -d -o data/genome.fa.bwt -m "Test dataprov" run docker run -v $PWD/data:/tmp:z -it docker.io/biocontainers/bwa:latest bwa index /tmp/genome.fa
```

If you want to annotate all files created by bwa.

```
cd data/index
dataprov -d -o genome.fa.amb genome.fa.ann genome.fa.bwt genome.fa.pac genome.fa.sa -m "Test dataprov" run docker run -v $PWD:/tmp/:z -it docker.io/biocontainers/bwa:latest bwa index /tmp/genome.fa
```

The commands tend to be very long and unreadable if you want to annotate more result files.
TODO: Option to annotate all files in one directory (except the input files)
