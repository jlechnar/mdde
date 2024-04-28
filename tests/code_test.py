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
#from mdde.code import *
from mdde.html_base import *
from mdde.tools_c import *

tools = tools_c() 

with open('code_test.md', 'r') as f:
    text = f.read()
    #    try:
    html = markdown.markdown(text, extensions=[HtmlBaseExtension(title="Code Test")])
    #AbbreviationExtension(tools, debug=True), 
    #    except AbbreviationException as e:
    #        print(str(e))

with open('code_test.html', 'w') as f:
    f.write(html)

with open('code_test.md', 'r') as f:
    text = f.read()
    html = markdown.markdown(text)

with open('code_test_no_extension.html', 'w') as f:
    f.write(html)
