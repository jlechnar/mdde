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
from mdde.description import *
from mdde.html_base import *
from mdde.tools_c import *

tools = tools_c()

with open('description_test.md', 'r') as f:
  text = f.read()
  try:
    html = markdown.markdown(text,
                             tab_length=2,
                             extensions=[DescriptionExtension(tools, verbose=True),
                                         HtmlBaseExtension(tools, title="Description Test")])
    html_no_ext = markdown.markdown(text, tab_length=2)
  except DescriptionException as e:
    print(str(e))

with open('description_test.html', 'w') as f:
    f.write(html)

with open('description_test_no_extension.html', 'w') as f:
    f.write(html_no_ext)
