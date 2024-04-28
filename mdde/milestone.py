from mdde.tools_c import *
from mdde.artefact import *

# -------------------------------------------------------------------------------
class MilestoneExtension(ArtefactExtension):

  def __init__(self, tools, **kwargs):

    super().__init__(tools, **kwargs)

    self.config['tag'][0] = "milestone"

    self.config['id'][0] = "milestone"

    self.config['title'][0] = 'List of Milestones'
