import os

from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand


setup(
    name='sae-postgres',
    author='ikethecoder',
    author_email='',
    version='1.0.0',
    description="Secure Analysis Environment Postgres",
    long_description="",
    license='Apache 2.0',

    packages=find_packages(),
    include_package_data=True
)
