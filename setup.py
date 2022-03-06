#!/usr/bin/env python

from setuptools import setup, find_packages

setup(name='makogen',
      version='0.1',
      description='Python package for generating fighting game controllers',
      author='Teddy',
      author_email='teddymori.mako@gmail.com',
      url='https://www.python.org/sigs/distutils-sig/',
      packages=find_packages(include=['makogen', 'makogen.*']),
     )