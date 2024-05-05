from markdown.inlinepatterns import InlineProcessor
from markdown.preprocessors import Preprocessor
from markdown.blockprocessors import BlockProcessor
from markdown.treeprocessors import Treeprocessor
from markdown.extensions import Extension
import xml.etree.ElementTree as etree
import re


class Codes(Preprocessor):
    RE_CODES = r'^(\s*```\s*)\[([^\]]+)\](.*)$'

    def __init__(self, md, tools, config):
        super().__init__(md)
        self.tools = tools
        self.config = config

    def run(self, lines):
        new_lines = []
        for line in lines:
            m = re.search(self.RE_CODES, line)
            if m:
                line_code_header = "{code:" + m.group(2) + "}"
                new_lines.append(line_code_header)
                line_code_start = m.group(1) + m.group(3)
                new_lines.append(line_code_start)
                if self.config["verbose"]:
                    self.tools.debug("CODE MOVE: " + line + " => " + line_code_header + " + " + line_code_start)
            else:
                new_lines.append(line)
        return new_lines


class CodesBlockProcessor(BlockProcessor):
   #
   # {code:<title>}
   #
   RE_CODE = r'\{(code:)(.*)\}'

   def __init__(self, parser, tools, md, config):
       super().__init__(parser)
       self.md = md
       self.tools = tools
       self.config = config

   def test(self, parent, block):
       return re.search(self.RE_CODE, block)

   def run(self, parent, blocks):

        m = re.search(self.RE_CODE, blocks[0])

        if m:
            code_description = m.group(2)

            self.md.loc_index_id += 1

            code_id_nr = self.md.loc_index_id

            code_id = "code:" + str(code_id_nr) + ":"


            self.md.loc_loc.append([code_id_nr, code_description])

            # self.md.loc[code_id_nr] = code_description

            if self.config["verbose"]:
                self.tools.debug("CODE: " + code_description)

            blocks[0] = re.sub(re.escape(m.group(0)), "{DONE:" + code_id + m.group(2) + "}", blocks[0])

            return True
        else:
            return False

# -------------------------------------------------------------------------------
class LocPositionBlockProcessor(BlockProcessor):
#  RE_LOC = r'^{loc}$'

  def __init__(self, parser, tools, md, config):
      super().__init__(parser)
      self.md = md
      self.tools = tools
      self.config = config
      self.RE_LOC = r'^\s*(' + self.config['list_commands'] + ')\s*$'

  def test(self, parent, block):
    return re.match(self.RE_LOC, block)

  def run(self, parent, blocks):

    m_loc = re.search(self.RE_LOC, blocks[0])

    if m_loc:
      d = etree.SubElement(parent, 'div')
      d.set('class', 'loc')

      blocks[0] = re.sub(re.escape(m_loc.group(0)), '', blocks[0])
      return True
    else:
      return False

# ------------------------------------------------------------------------
# replaces each code header to the final structure
# adds links, pre/postfixes, etc.
#
class CodeHeaderReplaceInlineProcessor(InlineProcessor):

  def __init__(self, pat, md, config):
    super().__init__(pat, md)
    self.config = config

  def handleMatch(self, m, md):
    code_id = m.group(1)
    code_description = m.group(2)

    e = etree.Element('span')
    ea = etree.SubElement(e, 'a')

    # artefact = self.md.loa_id_map[tag][artefact_id]
    ea.set('class', 'code_header')
    ea.set('id', "code:" + code_id + ":")
    ea.set('href', "#loc:" + code_id + ":")
    ea.text = "Code " + str(code_id) + ":"

    es = etree.SubElement(e, 'span')
    es.set('class', 'code_header_text')
    es.text = " " + code_description

    #if self.md.loa_seen[tag] is True:
    #  e.set('id', artefact_id)
    #e.text = self.config["text_prefix"] + artefact + self.config["text_postfix"]
    #
    #if self.config["link"]:
    #  e.set('href', self.config["link_prefix"] + artefact + self.config["link_postfix"])


    return e, m.start(0), m.end(0)

# -------------------------------------------------------------------------------
# code tag does not honor newlines, we convert to pre tag to handle this
class CodeToPreTreeProcessor(Treeprocessor):

  def __init__(self, md, config):
    super().__init__(md)
    self.config = config

  def run(self, root):
    self.code_to_pre(root)
    return None

  def code_to_pre(self, element):
    for child in element:
      if child.tag == "code":
          # FIXME: check for code header seen before !
          #if child.get("class") is "":
          child.tag = "pre"
      self.code_to_pre(child)


# ---------------------------------------------------------------
class LocReplaceTreeProcessor(Treeprocessor):

  def __init__(self, tools, md, config):
    super().__init__(md)
    self.config = config
    self.tools = tools

  def run(self, root):
    self.replace_loc(root)
    return None

  def replace_loc(self, element):
    for child in element:
      if child.tag == "div":
        if child.get("class") is not None:
          m = re.match(r'loc', child.get("class"))
          if m:
             if self.config["title_enable"]:
               eloc_image = etree.SubElement(child, "p")
               eloc_image.set("class", 'loc_title')
               eloc_image.text = self.config["title"]

             eloc_div = etree.SubElement(child, "div")
             eloc_table = etree.SubElement(eloc_div, "table")
             eloc_table.set('class', "loc_table")
             for loc in self.md.loc_loc:
               eloc_row = etree.SubElement(eloc_table, "tr")

               code_id = str(loc[0])

               eloc_data = etree.SubElement(eloc_row, "td")
               eloc_a = etree.SubElement(eloc_data, "a")
               # Only one link valid ! skipped below intentionally
               #eloc_a.set('id', "loc:" + code_id + ":")
               eloc_a.set('href', "#" + "code:" + code_id + ":")
               eloc_a.set('id', "loc:" + code_id + ":")
               eloc_a.set('class', 'code_loc')
               eloc_a.text = "Code " + code_id + ": " + loc[1]


      self.replace_loc(child)

# -------------------------------------------------------------------------------
class CodesExtension(Extension):

  LocReplaceTreeProcessorClass = LocReplaceTreeProcessor

  CodeToPreTreeProcessorClass = CodeToPreTreeProcessor

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
      'list_commands': [
          '{loc}|{list_of_codes}',
          'Command to support for list of codes generation'
          'Default: `loc`, `list_of_codes`.'
      ],
      'title_enable': [
        True,
        'Enable Title printing'
        'Default: on`.'
      ],
      'title': [
        'List of Codes',
        'Title for LOC'
        'Default: `List of Codes`.'
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
    md.preprocessors.register(Codes(md.parser, self.tools, self.config), 'codes', 180)

    # ------------
    # Blockprocessors

    md.parser.blockprocessors.register(CodesBlockProcessor(md.parser, self.tools, md, self.config), 'codes_block_processor', 175)

    # prepare loc for replacement
    md.parser.blockprocessors.register(LocPositionBlockProcessor(md.parser, self.tools, md, self.getConfigs()), 'reference__loc_position', 165)

    # ------------
    # Treeprocessors

    code_to_pre_ext = self.CodeToPreTreeProcessorClass(md, self.getConfigs())
    md.treeprocessors.register(code_to_pre_ext, 'code_to_pre_ext', 15)

    # generate loc
    loc_replace_ext = self.LocReplaceTreeProcessorClass(self.tools, md, self.getConfigs())
    md.treeprocessors.register(loc_replace_ext, 'code__loc_replace', 177)

    # ------------
    # Inlineprocessors

    CODE_HEADER_PATTERN = r'\{DONE:code:(\d+):([^\}]+)\}'
    md.inlinePatterns.register(CodeHeaderReplaceInlineProcessor(CODE_HEADER_PATTERN, md, self.getConfigs()), 'code_header_replace_inline', 165)

    # ------------
    # Postprocessors

  def reset(self):

    # line of codes code_id => code_descriptions
    # self.md.loc = {}

    # unique index id for codes and list of codes links
    self.md.loc_index_id = 0

    # # loi_index_id_list is used to define the current index level
    # # the list starts with one entry at 0
    # # it gets incremented/extended/reduced according to the current index level
    # self.md.loc_index_id_list = []
    # self.md.loc_index_id_list.append(0)

    # loc_loc contains the table of contents in the form of list entries (list of lists):
    # [index_id, heading_text]
    #
    self.md.loc_loc = []

    pass


# -------------------------------------------------------------------------------
class CodesException(Exception):
  name = "CodesException"
  message = ""

  def __init__(self, message):
    self.message = message

  def __str__(self):
    if self.message:
      return self.name + ': ' + self.message
    else:
      return self.name + ' has been raised'
