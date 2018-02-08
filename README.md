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

Run the biocontainer. The command is wrapped by dataprov. 

```
dataprov docker run -v $PWD/data:/tmp:z -it docker.io/biocontainers/bwa:latest bwa index /tmp/index/genome.fa
```
