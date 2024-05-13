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
from mdde.codes import *
from mdde.html_base import *
from mdde.tools_c import *

from mdde.artefact import *

tools = tools_c()

with open('code_test.md', 'r') as f:
    text = f.read()
    try:
        html = markdown.markdown(text,
                                 extensions=[
                                     #CodesExtension(tools, verbose=True),
                                     CodesExtension(tools, verbose=True, debug=True),
                                     ArtefactExtension(tools, verbose=True, title_enable=False),
                                     HtmlBaseExtension(tools, title="Code Test")])
    except CodesException as e:
        print(str(e))

with open('code_test.html', 'w') as f:
    f.write(html)

with open('code_test.md', 'r') as f:
    text = f.read()
    html = markdown.markdown(text)

with open('code_test_no_extension.html', 'w') as f:
    f.write(html)
