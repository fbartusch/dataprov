import os

from setuptools import find_packages, setup

import dataprov

setup(
    name="dataprov",
    version=dataprov.__version__,
    description="Automatic provenance metadata creator",
    url="https://github.com/fbartusch/dataprov",
    author="Felix Bartusch",
    author_email="felix.bartusch@uni-tuebingen.de",
    packages=find_packages(),
    classifiers=["Programming Language :: Python :: 3.8",
                 "Programming Language :: Python :: 3.7",
                 "Programming Language :: Python :: 3.6"],
    install_requires=[
        "distro>=1.0.0",
        "fluent_prov>=0.0.5",
        "mkdir_p",
        "prov==1.5.1",
        "pydot",
        "typing_extensions",
    ],
    extras_require={
        "testing": ["pytest-black", "pytest-cov", "pytest-isort", "pytest-mypy", "pytest-pylint"],
        "docs": ["sphinx", "sphinx-argparse==0.2.5", "sphinx_rtd_theme", "recommonmark"],
        "docker": ["docker>=4.1.0, <5.0"],
        "singularity": ["spython>=0.0.76", "sif>=0.0.11"],
        "snakemake": ["snakemake>=5.10.0, <6.0", "wrapt>=1.11, <1.12"],
        "cwl": ["cwltool>=1.0.20191022103248"],
    },
    entry_points={"console_scripts": ["dataprov=dataprov.__main__:main"]},
)
