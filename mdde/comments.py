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
                    self.tools.verbose(self.config["message_identifier"], "Comments: Ignoring comment: <" + m.group(2) + ">")
                m2 = re.search(r'[^ \t]', m.group(1))
                if m2:
                    if self.config["verbose"]:
                        self.tools.verbose(self.config["message_identifier"], "Comments: Not Ignoring command part of comment: <" + m.group(1) + ">")
                    new_lines.append(m.group(1))
                else:
                    if self.config["verbose"]:
                        self.tools.verbose(self.config["message_identifier"], "Comments: Ignoring none command part of comment: <" + m.group(1) + ">")
            else:
                new_lines.append(line)
        return new_lines

# -------------------------------------------------------------------------------
class CommentsExtension(Extension):

  def __init__(self, tools, **kwargs):
    self.tools = tools
    self.config = {
      'message_identifier': [
        'COMMENTS',
        'Message Identifier',
        'Default: COMMENTS`.'
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
    # level must be abive preprocessor of inht ! higher numbers first !
    # level should be higher than most of the others !
    md.preprocessors.register(Comments(md.parser, self.tools, self.getConfigs()), 'comments', 180)

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
