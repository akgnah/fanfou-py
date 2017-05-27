#!/usr/bin/env python
from setuptools import setup
from fanfou import __version__


long_description = open('README.rst').read()

setup(name='fanfou',
      version=__version__,
      description='OAuth of Fanfou',
      author='Akgnah',
      author_email='1024@setq.me',
      url=' http://github.com/akgnah/fanfou-py',
      packages=['fanfou'],
      install_requires=['six'],
      long_description=long_description,
      license="MIT",
      platforms=["any"],
      keywords='fanfou oauth')
