#!/bin/bash

# Description: MarkDown Documentation Extensions [MDDE] - 
# Author:      jlechnar
# Licence:     MIT Licence 
# Source:      https://github.com/jlechnar/mdde

set -x
set -e

python3 -m venv env
source env/bin/activate
pip install --upgrade pip
pip install --upgrade setuptools
pip install markdown

deactivate

