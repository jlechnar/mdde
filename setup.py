#! /usr/bin/env python

# Description: MarkDown Documentation Extensions [MDDE] - 
# Author:      jlechnar
# Licence:     MIT Licence 
# Source:      https://github.com/jlechnar/mdde

from setuptools import setup

setup(
    name='mdde',
    version='0.1',
    author='jlechnar',
    author_email='',
    description='MarkDown Documentation Extensions - Extensions for creating documentations.',
    long_description=open('README.md').read(),
    url='https://github.com/jlechnar/mdde',
    py_modules=['mdde'],
    install_requires=['Markdown>=3.3.6',],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Developers',
        'Environment :: Web Environment',
        'Programming Language :: Python',
        'Topic :: Text Processing :: Filters',
        'Topic :: Text Processing :: Markup :: HTML'
    ]
)
