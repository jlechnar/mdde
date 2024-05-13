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
from mdde.image import *
from mdde.title import *
from mdde.artefact import *
from mdde.milestone import *
from mdde.issue import *
from mdde.bug import *
from mdde.abbreviation import *
from mdde.labels_references import *
from mdde.description import *
from mdde.html_base import *
from mdde.comments import *
from mdde.codes import *
from mdde.tools_c import *

tools = tools_c()

with open('all_test.md', 'r') as f:
    text = f.read()
    try:
        html = markdown.markdown(text, tab_length=2, extensions=[
          LabelsReferencesExtension(tools, verbose=True, numbered_links=False, title_enable=False, ignore_duplicates=True),
          INHTExtension(tools, verbose=True),
          AbbreviationExtension(tools, verbose=True, title_enable=False),
          TitleExtension(tools, verbose=True, title_enable=False),
          ArtefactExtension(tools, verbose=True, title_enable=False),
          MilestoneExtension(tools, verbose=True, title_enable=False),
          IssueExtension(tools, verbose=True, title_enable=False),
          BugExtension(tools, verbose=True, title_enable=False),
          ImageExtension(tools, verbose=True, title_enable=False),
          CodesExtension(tools, verbose=True, title_enable=False),
          DescriptionExtension(tools, verbose=True),
          CommentsExtension(tools, verbose=True),
          HtmlBaseExtension(tools, title="All Test")])
    except INHTException as e:
        print(str(e))
    except ImageException as e:
        print(str(e))
    except AbbreviationException as e:
        print(str(e))
    except LabelsReferencesException as e:
        print(str(e))
    except Exception as e:
        print(str(e))

with open('all_test.html', 'w') as f:
    f.write(html)


with open('all_test.md', 'r') as f:
    text = f.read()
    html = markdown.markdown(text)

with open('all_test_no_extension.html', 'w') as f:
    f.write(html)
