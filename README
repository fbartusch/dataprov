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

Install cwltool, the reference CWL implementation.

```
pip install cwlref-runner
```

## Usage

dataprov is a wrapper that executes CWLCommandLineTools and CWLWorkflows.
dataprov will examine the .cwl file and the input files given and creates provenance data for the resulting files.

### Example: Reference index with bwa

```
dataprov cwltool examples/cwl/bwa-index.cwl examples/cwl/bwa-index-job.yml
```
