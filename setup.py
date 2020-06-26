import os

from setuptools import find_packages, setup

import dataprov2

setup(
    name="dataprov2",
    version=dataprov2.__version__,
    description="Automatic provenance metadata creator",
    url="https://github.com/jonasgloning/dataprov2",
    author="Jonas Gloning",
    author_email="dataprov2.jonas@gloning.name",
    packages=find_packages(),
    classifiers=["Programming Language :: Python :: 3.6", "Programming Language :: Python :: 3.7"],
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
    entry_points={"console_scripts": ["dataprov=dataprov2.__main__:main"]},
)
