from mdde.tools_c import *
from mdde.artefact import *

# -------------------------------------------------------------------------------
class BugExtension(ArtefactExtension):

  def __init__(self, tools, **kwargs):

    super().__init__(tools, **kwargs)

    self.config['message_identifier'][0] = 'BUG'

    self.config['tag'][0] = "bug"

    self.config['id'][0] = "bug"

    self.config['link'][0] = True

    self.config['link_prefix'][0] = "http://my.bugtracker.org/bug"

    self.config['link_postfix'][0] = ""

    self.config['title'][0] = 'List of Bugs'
