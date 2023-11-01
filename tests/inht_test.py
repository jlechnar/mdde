import sys
import os

# Description: MarkDown Documentation Extensions [MDDE] - 
# Author:      jlechnar
# Licence:     MIT Licence 
# Source:      https://github.com/jlechnar/mdde

current_dir = os.path.dirname(os.path.realpath(__file__))
relative_path = os.path.join(current_dir, '..')
sys.path.append(relative_path)

import markdown
from mdde.inht import *

with open('inht_test.md', 'r') as f:
    text = f.read()
    try:
        html = markdown.markdown(text, extensions=[INHTExtension(verbose=True)])
    except INHTException as e:
        print(str(e))

with open('inht_test.html', 'w') as f:
    f.write(html)

