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
from mdde.labels_references import *
from mdde.html_base import *
from mdde.tools_c import *

tools = tools_c()

with open('labels_references_test.md', 'r') as f:
    text = f.read()
    try:
        html1 = markdown.markdown(text,
                                  extensions=[
                                    LabelsReferencesExtension(tools, verbose=True, numbered_links=True),
                                    HtmlBaseExtension(tools, title="Labels References Test (numbered links)")
                                  ])
        html2 = markdown.markdown(text, extensions=[LabelsReferencesExtension(tools, verbose=True, numbered_links=False), HtmlBaseExtension(tools, title="Labels References Test (normal links)")])
        html3 = markdown.markdown(text, extensions=[LabelsReferencesExtension(tools, verbose=True, numbered_links=True),INHTExtension(tools, verbose=True), HtmlBaseExtension(tools, title="Labels References Test (numbered links and INHT)")])
        html4 = markdown.markdown(text, extensions=[LabelsReferencesExtension(tools, verbose=True, numbered_links=False),INHTExtension(tools, verbose=True), HtmlBaseExtension(tools, title="Labels References Test (normal links and INHT)")])
        html_none = markdown.markdown(text)
    except Labels_ReferencesException as e:
        print(str(e))

with open('labels_references_test_1.html', 'w') as f:
    f.write(html1)

with open('labels_references_test_2.html', 'w') as f:
    f.write(html2)

with open('labels_references_test_3.html', 'w') as f:
    f.write(html3)

with open('labels_references_test_4.html', 'w') as f:
    f.write(html4)

with open('labels_references_test_no_extension.html', 'w') as f:
    f.write(html_none)
