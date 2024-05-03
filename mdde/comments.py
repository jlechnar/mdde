from markdown.preprocessors import Preprocessor
from markdown.extensions import Extension
import re

class Comments(Preprocessor):
    RE_COMMENTS = r'^([^\%]*)(\%.*)$'
    # RE_COMMENTS = r'^\s*(\%.*)$'

    def __init__(self, md, tools, config):
        super().__init__(md)
        self.tools = tools
        self.config = config

    def run(self, lines):
        new_lines = []
        for line in lines:

            m = re.search(self.RE_COMMENTS, line)
            if m:
                if self.config["verbose"]:
                    self.tools.info("Comments: Ignoring comment: <" + m.group(2) + ">")
                m2 = re.search(r'[^ \t]', m.group(1))
                if m2:
                    if self.config["verbose"]:
                        self.tools.info("Comments: Not Ignoring command part of comment: <" + m.group(1) + ">")
                    new_lines.append(m.group(1))
                else:
                    if self.config["verbose"]:
                        self.tools.info("Comments: Ignoring none command part of comment: <" + m.group(1) + ">")
            else:
                new_lines.append(line)
        return new_lines

# -------------------------------------------------------------------------------
class CommentsExtension(Extension):

  def __init__(self, tools, **kwargs):
    self.tools = tools
    self.config = {
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
    md.preprocessors.register(Comments(md.parser, self.tools, self.config), 'comments', 180)

    # ------------
    # Blockprocessors

    # ------------
    # Treeprocessors

    # ------------
    # Inlineprocessors

    # ------------
    # Postprocessors

  def reset(self):

    pass


# -------------------------------------------------------------------------------
class CommentsException(Exception):
  name = "CommentsException"
  message = ""

  def __init__(self, message):
    self.message = message

  def __str__(self):
    if self.message:
      return self.name + ': ' + self.message
    else:
      return self.name + ' has been raised'
