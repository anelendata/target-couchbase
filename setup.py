#!/usr/bin/env python
from setuptools import setup

VERSION = "0.1.1"

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="target-couchbase",
    version=VERSION,
    description="Load data on Couchbase via singer.io",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Daigo Tanaka, Anelen Co., LLC",
    url="https://github.com/anelendata/target_couchbase",

    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: Apache Software License",

        "Operating System :: MacOS :: MacOS X",
        "Operating System :: POSIX :: Linux",

        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],

    install_requires=[
        "singer-python>=5.2.0",
        "couchbase>=3.0.8",
        "simplejson==3.11.1",
        "setuptools>=40.3.0",
    ],
    entry_points="""
    [console_scripts]
    target-couchbase=target_couchbase:main
    """,
    packages=["target_couchbase"],
    package_data={
        # Use MANIFEST.ini
    },
    include_package_data=True
)
