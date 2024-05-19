from markdown.preprocessors import Preprocessor
from markdown.extensions import Extension
import re

class Newlines(Preprocessor):
    RE_NEWLINES_BEFORE = r'^(\s*```|^\*)'
    RE_CODE = r'^(\s*```)'

    def __init__(self, md, tools, config):
        super().__init__(md)
        self.tools = tools
        self.config = config

    def run(self, lines):
        new_lines = []
        line_prev = ""
        inside_code = False

        if self.config["debug"]:
            self.tools.debug(self.config["message_identifier"], "[before] " + str(lines))

        for line in lines:

            m = re.search(self.RE_NEWLINES_BEFORE, line)
            if m:
                insert_newline_enable_code = True
                m2 = re.search(self.RE_CODE, line)
                if m2:
                    if inside_code:
                        insert_newline_enable_code = False
                if insert_newline_enable_code is False:
                    if self.config["verbose"]:
                        self.tools.verbose(self.config["message_identifier"], "Newlines: Not adding before as inside code: <" + line_prev + "> => <" + line + ">")
                    new_lines.append(line)
                elif line_prev != "":
                    if self.config["verbose"]:
                        self.tools.verbose(self.config["message_identifier"], "Newlines: Adding between: <" + line_prev + "> => <" + line + ">")
                    new_lines.append("")
                    new_lines.append(line)
                else:
                    if self.config["verbose"]:
                        self.tools.verbose(self.config["message_identifier"], "Newlines: Not adding before as already there: <" + line_prev + "> => <" + line + ">")
                    new_lines.append(line)
            else:
                new_lines.append(line)
            line_prev = line

            m = re.search(self.RE_CODE, line)
            if m:
                if inside_code:
                    inside_code = False
                else:
                    inside_code = True

        if self.config["debug"]:
            self.tools.debug(self.config["message_identifier"], "[after] " + str(new_lines))

        return new_lines

# -------------------------------------------------------------------------------
class NewlinesExtension(Extension):

  def __init__(self, tools, **kwargs):
    self.tools = tools
    self.config = {
      'message_identifier': [
        'NEWLINES',
        'Message Identifier',
        'Default: NEWLINES`.'
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
    md.preprocessors.register(Newlines(md.parser, self.tools, self.getConfigs()), 'newlines', 250)

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
class NewlinesException(Exception):
  name = "NewlinesException"
  message = ""

  def __init__(self, message):
    self.message = message

  def __str__(self):
    if self.message:
      return self.name + ': ' + self.message
    else:
      return self.name + ' has been raised'
