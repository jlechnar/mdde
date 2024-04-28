#!/bin/bash

# Description: MarkDown Documentation Extensions [MDDE] - 
# Author:      jlechnar
# Licence:     MIT Licence 
# Source:      https://github.com/jlechnar/mdde

set -x
set -e

source env/bin/activate
# https://github.com/facelessuser/pymdown-extensions/blob/main/docs/src/markdown/installation.md
# superfences
pip install pymdown-extensions

# pip install --editable .

pip install pygments

