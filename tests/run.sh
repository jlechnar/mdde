#!/bin/bash

# Description: MarkDown Documentation Extensions [MDDE] - 
# Author:      jlechnar
# Licence:     MIT Licence 
# Source:      https://github.com/jlechnar/mdde

set -x
set -e

source env/bin/activate

python3 all_test.py | tee all_test.log

python3 inht_test.py | tee inht_test.log
python3 image_test.py | tee image_test.log
python3 abbreviation_test.py | tee abbreviation_test.log
python3 labels_references_test.py | tee labels_references_test.log
python3 description_test.py | tee description_test.log
python3 artefact_test.py | tee artefact_test.log
python3 code_test.py | tee code_test.log
python3 link_test.py | tee link_test.log
