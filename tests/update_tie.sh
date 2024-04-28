#!/bin/bash

# Description: MarkDown Documentation Extensions [MDDE] - 
# Author:      jlechnar
# Licence:     MIT Licence 
# Source:      https://github.com/jlechnar/mdde

set -x
set -e

source env/bin/activate

pip install -force-reinstall -v markdown==3.6 

