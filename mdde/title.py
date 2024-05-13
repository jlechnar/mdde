from mdde.tools_c import *
from mdde.artefact import *

# -------------------------------------------------------------------------------
class TitleExtension(ArtefactExtension):

  def __init__(self, tools, **kwargs):

    super().__init__(tools, **kwargs)

    self.config['message_identifier'][0] = 'TITLE'

    self.config['tag'][0] = "title"

    self.config['id'][0] = "title"

    self.config['link'][0] = False

    self.config['text_prefix'][0] = ""

    self.config['text_postfix'][0] = ""

    self.config['link_prefix'][0] = ""

    self.config['link_postfix'][0] = ""

    self.config['title'][0] = 'List of Titles'
