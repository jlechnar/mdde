from mdde.tools_c import *
from mdde.artefact import *

# -------------------------------------------------------------------------------
class IssueExtension(ArtefactExtension):

  def __init__(self, tools, **kwargs):

    super().__init__(tools, **kwargs)

    self.config['message_identifier'][0] = 'ISSUE'

    self.config['tag'][0] = "issue"

    self.config['id'][0] = "issue"

    self.config['link'][0] = True

    self.config['text_prefix'][0] = "issue"

    self.config['text_postfix'][0] = ""

    self.config['link_prefix'][0] = "http://my.issue.tracker.org/issue"

    self.config['link_postfix'][0] = "/details"

    self.config['title'][0] = 'List of Issues'
