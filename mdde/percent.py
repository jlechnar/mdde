from markdown.inlinepatterns import InlineProcessor
from markdown.preprocessors import Preprocessor
from markdown.blockprocessors import BlockProcessor
from markdown.treeprocessors import Treeprocessor
from markdown.extensions import Extension
import xml.etree.ElementTree as etree
import re
from mdde.tools_c import *

# Description: MarkDown Documentation Extensions [MDDE] - 
# Author:      jlechnar
# Licence:     MIT Licence 
# Source:      https://github.com/jlechnar/mdde

# -------------------------------------------------------------------------------
# Percent:
# ============
# Percents are defined as
# {percent}

# ------------------------------------------------------------------------
class PercentReplaceInlineProcessor(InlineProcessor):

  def __init__(self, pat, md, config):
    super().__init__(pat, md)
    self.config = config

  def handleMatch(self, m, md):
    e = etree.Element('span')
    e.text = "&#37;"

    return e, m.start(0), m.end(0)

# -------------------------------------------------------------------------------
class PercentExtension(Extension):

  def __init__(self, tools, **kwargs):
    self.tools = tools
    self.config = {
      'message_identifier': [
          'PERCENT',
          'Message Identifier',
          'Default: PERCENT`.'
      ],
      'debug': [
        False,
        'Debug mode',
        'Default: off`.'
      ],
      'verbose': [
        False,
        'Verbose mode',
        'Default: off`.'
      ],
    }
    """ Default configuration options. """

    super().__init__(**kwargs)

  def extendMarkdown(self, md):
    md.registerExtension(self)
    self.md = md
    self.reset()

    # ------------
    # Processing sequence: pre, block, tree, inline, post
    # index defines processing sequence withing sequences (higher numbers first !)

    # ------------
    # Preprocessors

    # ------------
    # Blockprocessors

    # ------------
    # Treeprocessors

    # ------------
    # Inlineprocessors

    PERCENT_PATTERN = r'(\{percent\})'
    md.inlinePatterns.register(PercentReplaceInlineProcessor(PERCENT_PATTERN, md, self.getConfigs()), 'replace_percent_inline', 175)

    # ------------
    # Postprocessors

  def reset(self):
    # global variables to share between processing sequences

    pass

# -------------------------------------------------------------------------------
class PercentException(Exception):
  name = "PercentException"
  message = ""

  def __init__(self, message):
    self.message = message

  def __str__(self):
    if self.message:
      return self.name + ': ' + self.message
    else:
      return self.name + ' has been raised'
