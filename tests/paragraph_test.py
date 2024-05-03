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
from mdde.html_base import *
from mdde.inht import *
from mdde.tools_c import *

tools = tools_c() 

with open('paragraph_test.md', 'r') as f:
  text = f.read()
  try:
    html = markdown.markdown(text, extensions=[
        HtmlBaseExtension(title="Paragrapth Test"),
        INHTExtension(tools, debug=True)
      ])
  except INHTException as e:
    print(str(e))
#    except ImageException as e:
#        print(str(e))
#    except AbbreviationException as e:
#        print(str(e))

with open('paragraph_test.html', 'w') as f:
  f.write(html)

with open('paragraph_test.md', 'r') as f:
  text = f.read()
  html = markdown.markdown(text)

with open('paragraph_test_no_extension.html', 'w') as f:
  f.write(html)

