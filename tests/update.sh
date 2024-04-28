#!/bin/bash

# Description: MarkDown Documentation Extensions [MDDE] - 
# Author:      jlechnar
# Licence:     MIT Licence 
# Source:      https://github.com/jlechnar/mdde

set -x
set -e

source env/bin/activate

# pip list --outdated | grep -v '^\-e' | cut -d = -f 1 | xargs -n1 pip install -U

pip install markdown --upgrade 

