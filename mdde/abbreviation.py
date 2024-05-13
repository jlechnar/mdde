from markdown.inlinepatterns import InlineProcessor
from markdown.preprocessors import Preprocessor
from markdown.blockprocessors import BlockProcessor
from markdown.treeprocessors import Treeprocessor
from markdown.extensions import Extension
import xml.etree.ElementTree as etree
import re
import copy
from mdde.tools_c import *

# Description: MarkDown Documentation Extensions [MDDE] - 
# Author:      jlechnar
# Licence:     MIT Licence 
# Source:      https://github.com/jlechnar/mdde


# -------------------------------------------------------------------------------
#
class AbbreviationBlockProcessor(BlockProcessor):
   #
   # {a:[<short>][<expanded>][<details>]}
   # {abbr:[<short>][<expanded>][<details>]}
   # {abbreviation:[<short>][<expanded>][<details>]}
   #
   # {a:[<short>][<expanded>]}
   # {abbr:[<short>][<expanded>]}
   # {abbreviation:[<short>][<expanded>]}
   #
   RE_ABBREVIATION = r'\{(a|abbr|abbreviation):\[([^\]]+)\]\[([^\]]+)\](\[([^\]]*)\]|)\}'

   def __init__(self, parser, tools, md, config):
       super().__init__(parser)
       self.md = md
       self.tools = tools
       self.config = config

   def test(self, parent, block):
       return re.search(self.RE_ABBREVIATION, block)

   def run(self, parent, blocks):

        m = re.search(self.RE_ABBREVIATION, blocks[0])

        if m:
            abbreviation_short = m.group(2)
            abbreviation_long = m.group(3)
            abbreviation_details = ""

            if not m.group(4) is None:
                abbreviation_details = m.group(5)

            if self.config["verbose"]:
               self.tools.verbose(self.config["message_identifier"], "ABBR: " + abbreviation_short + " => " + abbreviation_long + ": " + abbreviation_details)

            if abbreviation_short.upper() in self.md.loa_loa:
               self.tools.warning(self.config["message_identifier"], "Ignoring abbreviation definition duplicate for <" + abbreviation_short + ">")
            else:
               self.md.loa_loa[abbreviation_short.upper()] = [abbreviation_short, abbreviation_long, abbreviation_details]

            # ---------------------------------
            # remove parsed abbreviation block
            blocks[0] = re.sub(re.escape(m.group(0)), '', blocks[0])

            return True
        else:
            return False

# -------------------------------------------------------------------------------
class LoaPositionBlockProcessor(BlockProcessor):

    def __init__(self, parser, tools, md, config):
        super().__init__(parser)
        self.md = md
        self.tools = tools
        self.config = config
        self.RE_LOA = r'^\s*(' + self.config['list_commands'] + ')\s*$'

    def test(self, parent, block):
        return re.match(self.RE_LOA, block)

    def run(self, parent, blocks):

        m = re.search(self.RE_LOA, blocks[0])

        if m:
            d = etree.SubElement(parent, 'div')
            d.set('class', 'loa')

            blocks[0] = re.sub(re.escape(m.group(0)), '', blocks[0])
            return True
        else:
            return False

# ---------------------------------------------------------------
class LoaReplaceTreeProcessor(Treeprocessor):

    def __init__(self, md, config):
        super().__init__(md)
        self.config = config

    def run(self, root):
        self.replace_loa(root)
        return None

    def replace_loa(self, element):
        for child in element:
            if child.tag == "div":
                if child.get("class") is not None:
                    m = re.match(r'^loa$', child.get("class"))
                    if m:
                         if self.config["title_enable"]:
                             eloa_abbreviation = etree.SubElement(child, "p")
                             eloa_abbreviation.set("class", 'loa_title')
                             eloa_abbreviation.text = self.config["title"]

                         eloa_div = etree.SubElement(child, "div")
                         eloa_table = etree.SubElement(eloa_div, "table")
                         eloa_table.set('class', "loa")

                         eloa_row = etree.SubElement(eloa_table, "tr")
                         eloa_data = etree.SubElement(eloa_row, "th")
                         eloa_data.text = "Short"
                         eloa_data = etree.SubElement(eloa_row, "th")
                         eloa_data.text = "Long"
                         eloa_data = etree.SubElement(eloa_row, "th")
                         eloa_data.text = "Description"

                         for loa in self.md.loa_loa:
                             abbreviation_short = self.md.loa_loa[loa][0]
                             abbreviation_long = self.md.loa_loa[loa][1]
                             abbreviation_description = self.md.loa_loa[loa][2]

                             eloa_row = etree.SubElement(eloa_table, "tr")

                             eloa_data = etree.SubElement(eloa_row, "td")
                             eloa_data.text = abbreviation_short

                             eloa_data = etree.SubElement(eloa_row, "td")
                             eloa_data.text = abbreviation_long

                             eloa_data = etree.SubElement(eloa_row, "td")
                             eloa_data.text = abbreviation_description

            self.replace_loa(child)

# -------------------------------------------------------------------------------
class AbbreviationExtension(Extension):

    LoaReplaceTreeProcessorClass = LoaReplaceTreeProcessor

    def __init__(self, tools, **kwargs):
        self.tools = tools
        self.config = {
            'message_identifier': [
                'ABBREVIATION',
                'Message Identifier',
                'Default: ABBREVIATION`.'
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
            'title_enable': [
                 True,
                 'Enable Title printing',
                 'Default: on`.'
            ],
            'list_commands': [
                '{loa}|{list_of_abbreviations}',
                'Command to support for list of abbreviations generation',
                'Default: `loa`, `list_of_abbreviations`.'
            ],
            'title': [
                'List of Abbreviations',
                'Title for LOA',
                'Default: `List of Abbreviations`.'
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

        md.parser.blockprocessors.register(AbbreviationBlockProcessor(md.parser, self.tools, md, self.getConfigs()), 'abbreviation_block_processor', 175)

        # prepare loa for replacement
        md.parser.blockprocessors.register(LoaPositionBlockProcessor(md.parser, self.tools, md, self.getConfigs()), 'abbreviation__loa_position', 175)

        # ------------
        # Treeprocessors

        # generate loa
        loa_replace_ext = self.LoaReplaceTreeProcessorClass(md, self.getConfigs())
        md.treeprocessors.register(loa_replace_ext, 'abbreviation__loa_replace', 177)

        # ------------
        # Inlineprocessors

        # ------------
        # Postprocessors

    def reset(self):
        # global variables to share between processing sequences

        # loa_loa contains the table of contents in the form of dictionary entries each consisting of a list of three elements:
        # loa_loa[abbreviation_short_uppercase] = [abbreviation_short, abbreviation_long, abbreviation_description]
        #
        self.md.loa_loa = {}

        pass

# -------------------------------------------------------------------------------
class AbbreviationException(Exception):
    name = "AbbreviationException"
    message = ""

    def __init__(self, message):
        self.message = message

    def __str__(self):
        if self.message:
            return self.name + ': ' + self.message
        else:
            return self.name + ' has been raised'
