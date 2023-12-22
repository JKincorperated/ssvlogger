#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: skip-file

from setuptools import setup, find_packages

setup(
    name='ssvlogger',
    version='1.0.0',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'ssvlogger = ssvlogger.logger:main'
        ]
    },
    # metadata for upload to PyPI
    author='JKinc',
    author_email='your.email@example.com',
    description='A simple python package to parse SSV node logs and make them legible',
    keywords='SSV logging',
    url='https://github.com/JKincorperated/ssvlogger',  # project home page
)