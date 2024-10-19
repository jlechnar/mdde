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
from mdde.newlines import *
from mdde.percent import *

tools = tools_c()

verbose=True

with open('all_test.md', 'r') as f:
    text = f.read()
    try:
        html = markdown.markdown(text,
                                 tab_length=2,
                                 extensions=[
                                     LabelsReferencesExtension(tools, verbose=verbose, numbered_links=False, title_enable=False, ignore_duplicates=True, use_label_text_for_empty_reference_texts=True),
                                     INHTExtension(tools, verbose=verbose),
                                     AbbreviationExtension(tools, verbose=verbose, title_enable=False),
                                     ArtefactExtension(tools, verbose=verbose, title_enable=False, link=True, title_missing_enable=False, reference_list_file_name="artefact.txt", reference_list_mapped_file_name="artefact_mapped.txt"),
                                     TitleExtension(tools, verbose=verbose, title_enable=False),
                                     MilestoneExtension(tools, verbose=verbose, title_enable=False, link=True, link_extend=True, link_prefix="#", link_postfix="", title_missing_enable=False, reference_list_file_name="milestone.txt"),
                                     IssueExtension(tools, verbose=verbose, title_enable=False, title_missing_enable=False, reference_list_file_name="issue.txt", reference_list_mapped_file_name="issue_mapped.txt"),
                                     BugExtension(tools, verbose=verbose, title_enable=False, reference_list_mapped_file_name="bug_mapped.txt"),
                                     ImageExtension(tools, verbose=verbose, title_enable=False),
                                     CodesExtension(tools, verbose=verbose, title_enable=False),
                                     DescriptionExtension(tools, verbose=verbose),
                                     CommentsExtension(tools, verbose=verbose),
                                     NewlinesExtension(tools, verbose=verbose),
                                     PercentExtension(tools, verbose=verbose),
                                     'tables',
                                     'attr_list',
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
