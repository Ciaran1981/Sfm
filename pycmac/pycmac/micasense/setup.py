#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 15 12:16:49 2019

@author: ciaran
"""

"""Alternations to setup.py based on Brandon Rhodes' conda setup.py:
https://github.com/brandon-rhodes/conda-install"""
from setuptools import setup
from setuptools.command.install import install
from io import open
import subprocess

descript = ('an installer for micasense red-edge which I have forked -'
            'the library is the work of micasense in which I have only made a minor alteration')

#with open('README.rst', encoding='utf-8') as f:
#    long_description = f.read()


class CondaInstall(install):
    def run(self):
        try:
            command = ['conda', 'env', 'create', '-f', 'micasense_conda_env.yml']
            #packages = open('conda_modules.txt').read().splitlines()
#            command.extend(packages)
            subprocess.check_call(command)
#            install.do_egg_install(self)
        except subprocess.CalledProcessError:
            print("Conda install failed: do you have Anaconda/miniconda installed and on your PATH?")


setup(
    cmdclass={'install': CondaInstall},
    name="micasense",
    version="0.1",
    packages=['micasense_fork'],
    #install_requires=open('requirements.txt').read().splitlines(),
    # Project uses reStructuredText, so ensure that the docutils get
    # installed or upgraded on the target machine
    include_package_data=True,# {
        # If any package contains *.txt or *.rst files, include them:
        # And include any *.msg files found in the 'hello' package, too:
    #},
    classifiers=[
          'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
#          'Programming Language :: Python :: 3.4',
#          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
          'Topic :: Scientific/Engineering :: GIS',
          'Topic :: Utilities'],
    # metadata for upload to PyPI
    # zip_safe = True,
    author="micasense",
    description=descript,
    #long_description=long_description,
    license='GPLv3+',
#    url="https://github.com/Ciaran1981/geospatial-learn",   # project home page, if any
#    download_url="https://github.com/Ciaran1981/geospatial-learn"
    # could also include long_description, download_url, classifiers, etc.
)
