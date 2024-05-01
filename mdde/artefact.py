from markdown.inlinepatterns import InlineProcessor
from markdown.preprocessors import Preprocessor
from markdown.blockprocessors import BlockProcessor
from markdown.treeprocessors import Treeprocessor
from markdown.extensions import Extension
import xml.etree.ElementTree as etree
import re
import copy
import collections
from mdde.tools_c import *

# Description: MarkDown Documentation Extensions [MDDE] - 
# Author:      jlechnar
# Licence:     MIT Licence 
# Source:      https://github.com/jlechnar/mdde

# -------------------------------------------------------------------------------
# Artefact:
# ============
# Artefacts are defined as
# {<artefact>:id}
#
# A prefix and postfix can be given to create links
# => links to <link_prefix><id><link_postfix>
#
# The identifier can be selected
# <artefact> => <issue>, ...
#
# A List of artefacts can be created with links to items.
#
  
# -------------------------------------------------------------------------------
# parses the code and detects and uniquifies each found artefact by adding a artefact number / replacing the original artefact for later unique processing.
#
# code:
#   {artefact:<artefact_identifier>}
#
class ArtefactBlockProcessor(BlockProcessor):

  def __init__(self, parser, tools, md, config):
    super().__init__(parser)
    self.md = md
    self.tools = tools
    self.config = config
    self.re_artefact = r'(.*)\{(' + config["tag"] + ':)([^\}]+)\}(.*)'

  def test(self, parent, block):
    return re.search(self.re_artefact, block)

  def run(self, parent, blocks):
    tag = self.config['tag']

    seenany = False
    for match in re.finditer(self.re_artefact, blocks[0], re.DOTALL):
      seenany = True
      artefact = match.group(3)
      if not artefact in self.md.loa_id_nr[tag]:
        self.md.loa_id_nr[tag][artefact] = 0
      self.md.loa_id_nr[tag][artefact] += 1

      artefact_id = tag + ":" + artefact + ":" + str(self.md.loa_id_nr[tag][artefact])
      
      self.md.loa_artefact_id_to_id_nr[tag][artefact_id] = self.md.loa_id_nr[tag][artefact]
      
      # each artefact may be there multiple times
      # we need a list of uniqe ids so that we can print the loa
      if not artefact in self.md.loa[tag]:
        self.md.loa[tag][artefact] = [] # collections.defaultdict(list)
      self.md.loa[tag][artefact].append(artefact_id) # FIXME: does not work as append is not part of defaultdict(list) ??? # create own class for this ???
        
      if self.config["verbose"]:
        print("A (" + tag + "): " + artefact_id + " => " + artefact)

      self.md.loa_id_map[tag][artefact_id] = artefact

      blocks[0] = match.group(1) + "{DONE:" + match.group(2) + artefact_id + "}" + match.group(4)
      #re.sub(re.escape(match.group(0)), "{DONE:" + match.group(1) + artefact_id + "}", blocks[0])

    if seenany:
      return True
    return False

# -------------------------------------------------------------------------------
# Detects the 'list of artefacts' command and adds an etree element for later replacement
#
class ArtefactLoaPositionBlockProcessor(BlockProcessor):

    def __init__(self, parser, tools, md, config):
      super().__init__(parser)
      self.md = md
      self.tools = tools
      self.config = config
      self.re_loa = r'\{loa:' + config["tag"] + '\}'

    def test(self, parent, block):
      return re.match(self.re_loa, block)

    def run(self, parent, blocks):
      tag = self.config["tag"]

      m = re.search(self.re_loa, blocks[0])

      if m:
        d = etree.SubElement(parent, 'div')
        d.set('class', 'loa__' + self.config["tag"])
        self.md.loa_seen[tag] = True

        blocks[0] = re.sub(re.escape(m.group(0)), '', blocks[0])
        return True
      else:
        return False

# ---------------------------------------------------------------
# natural sorting of alphanumeric numbers
tokenize = re.compile(r'(\d+)|(\D+)').findall
def natural_sortkey(string):          
    return tuple(int(num) if num else alpha for num, alpha in tokenize(string))
  
# ---------------------------------------------------------------
# Creates the 'list of artefacts'
#
class ArtefactLoaReplaceTreeProcessor(Treeprocessor):

  def __init__(self, md, config):
    super().__init__(md)
    self.config = config
    # self.numbered_links = config["numbered_links"]

  def run(self, root):
    self.replace_loa(root)
    return None

  def replace_loa(self, element):
    tag = self.config["tag"]

    for child in element:
      if child.tag == "div":
        if child.get("class") is not None:
          m = re.match(r'loa__' + tag, child.get("class"))
          if m:

            if self.config["title_enable"]:
              e_loa_references = etree.SubElement(child, "p")
              e_loa_references.set("class", 'loa_' + tag + '_heading')
              e_loa_references.text = self.config["title"]

            e_loa_div = etree.SubElement(child, "div")

            # e_loa_dl = etree.SubElement(e_loa_div, "dl")

            e_loa_table = etree.SubElement(e_loa_div, "table")
            e_loa_table.set('class', "loa__" + tag)

            for artefact in sorted(self.md.loa[tag], key=natural_sortkey):
              
              e_loa_row = etree.SubElement(e_loa_table, "tr")
                
              e_loa_data = etree.SubElement(e_loa_row, "td")
              if self.config["link"]:
                a = etree.SubElement(e_loa_data, 'a')
              else:
                a = etree.SubElement(e_loa_data, 'span')

              artefact_text = self.config["text_prefix"] + artefact + self.config["text_postfix"]
              
              #if self.numbered_links:
              #  a.text = "[" + str(self.md.loa_labels_nr[label_link_id]) + "]"
              #else:
              a.text = "[" + artefact_text + "]"
              a.set('href', self.config["link_prefix"] + artefact + self.config["link_postfix"])
              
              a_title = ""
              #if self.numbered_links:
              #  a_title = "[" + str(self.md.loa_labels_nr[artefact_id]) + "] = "
              a_title += "[" + artefact_text + "]"
              a.set('title', a_title)
              #
              a.set('class', tag + '_internal_reference')
              # a.set('href', "#" + artefact_id)
              a.set('id', "loa_"+ tag + ":" + artefact + ":")

              e_loa_data_links = etree.SubElement(e_loa_row, "td")

              first_element = True
              
              for artefact_id in sorted(self.md.loa[tag][artefact], key=natural_sortkey):
                
                if self.config["verbose"]:
                  print("LOA (" + tag + "): " + artefact_id + " => " + artefact)

                if not first_element:
                  e_loa_data = etree.SubElement(e_loa_data_links, "span")
                  e_loa_data.text = ", "
                first_element = False
                
                artefact_id_nr = self.md.loa_artefact_id_to_id_nr[tag][artefact_id]
                
                # e_loa_row = etree.SubElement(e_loa_table, "tr")
            
                e_loa_data = etree.SubElement(e_loa_data_links, "span")
                a = etree.SubElement(e_loa_data, 'a')
                #if self.numbered_links:
                #  a.text = "&nbsp;&nbsp;" + "&#x21b3;" + "[" + str(self.md.loa_references_nr[artefact_id]) + "]"
                #else:
                #a.text = "&nbsp;&nbsp;" + "&#x21b3;" + "[" + str(artefact_id_nr) + "]"
                a.text = "[" + str(artefact_id_nr) + "]"
                #
                a_title = ""
                #if self.numbered_links:
                #  a_title = "[" + str(self.md.loa_references_nr[artefact_id]) + "] = "
                a_title += "[" + artefact_id + "]"
                a.set('title', a_title)
                #
                a.set('class', 'internal_reference_link')
                a.set('href', "#" + artefact_id)
                
                
      self.replace_loa(child)

# ------------------------------------------------------------------------
# replaces each artefact to the final structure
# adds links, pre/postfixes, etc.
#
class ArtefactReplaceInlineProcessor(InlineProcessor):

  def __init__(self, pat, md, config):
    super().__init__(pat, md)
    self.config = config
    #self.numbered_links = config["numbered_links"]
    #self.reference_symbol = config["reference_symbol"]
    #self.set_id = set_id

  def handleMatch(self, m, md):
    artefact_id = m.group(1)
    # label_link_id = m.group(1)
    # label_text = self.md.lor_labels[label_link_id]

    # FIXME: check this already before ?!
    if not artefact_id in self.md.loa:
      ArtefactException("ERROR: Unexpected artefact id")

    if self.config["link"]:
      e = etree.Element('a')
    else:
      e = etree.Element('span')

    tag = self.config["tag"]

    artefact = self.md.loa_id_map[tag][artefact_id]
    e.set('class', tag)

    if self.md.loa_seen[tag] is True:
      e.set('id', artefact_id)
    e.text = self.config["text_prefix"] + artefact + self.config["text_postfix"]

    if self.config["link"]:
      e.set('href', self.config["link_prefix"] + artefact + self.config["link_postfix"])

    # if self.set_id:
    #   a.set('id', label_link_id)
    # a.set('href', '#' + "lor:" + label_link_id + ":")
    # a.set('class', 'internal_reference')
    # # FIXME: recursive eetree processing for below ???
    #
    # a.text = self.reference_symbol
    # #
    # a_title = ""
    # if self.numbered_links:
    #   a_title = "[" + str(self.md.lor_labels_nr[label_link_id]) + "] = "
    # a_title += "[" + label_link_id + "]: " + label_text
    # a.set('title', a_title)

    return e, m.start(0), m.end(0)

# -------------------------------------------------------------------------------
class ArtefactExtension(Extension):

  ArtefactLoaReplaceTreeProcessorClass = ArtefactLoaReplaceTreeProcessor

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
      'link': [
        False,
        'is a link or not',
        'Default: off`.'
      ],
      'text_prefix': [
        "",
        'text prefix to use before text',
        'Default: None`.'
      ],
      'text_postfix': [
        "",
        'text postfix to use after text',
        'Default: None`.'
      ],
      'link_prefix': [
        "",
        'link prefix to use before data',
        'Default: None`.'
      ],
      'link_postfix': [
        "",
        'link postfix to use after data',
        'Default: None`.'
      ],
      'tag': [
        "artefact",
        'Unique identifier tag string that is used as part of the language {<tag>:<data>}. It is also used as html class tag',
        'Default: off`.'
      ],
      'id': [
        "artefact",
        'Identifier used for separating processors/class instances in case of inherited classes',
        'Default: "artefact"`.'
      ],
      'title_enable': [
        True,
        'Enable Title printing'
        'Default: on`.'
      ],
      'title': [
        'List of Artefacts',
        'Title for LOA'
        'Default: `List of Artefacts`.'
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

    md_id = self.config['id'][0]
    md.parser.blockprocessors.register(ArtefactBlockProcessor(md.parser, self.tools, md, self.getConfigs()), md_id + '_block_processor', 165)

    # prepare loa for replacement
    md.parser.blockprocessors.register(ArtefactLoaPositionBlockProcessor(md.parser, self.tools, md, self.getConfigs()), md_id + '__loa_position', 165)

    # ------------
    # Treeprocessors

    loa_replace_ext = self.ArtefactLoaReplaceTreeProcessorClass(md, self.getConfigs())
    md.treeprocessors.register(loa_replace_ext, md_id + '__loa_replace', 165)

    # ------------
    # Inlineprocessors

    ARTEFACT_PATTERN = r'\{DONE:' + self.config["tag"][0] + ':([^\}]+)\}'
    md.inlinePatterns.register(ArtefactReplaceInlineProcessor(ARTEFACT_PATTERN, md, self.getConfigs()), md_id + '_replace_inline', 165)

    # ------------
    # Postprocessors

  def reset(self):
    # global variables to share between processing sequences

    # not that tag's below are required as we could have extended classes with different types of this class.
    # tag's are used for differentiation between different types of classes
    tag = self.config['tag'][0]

    # FIXME: update below
    # loa contains the table of contents in the form of dictionary entries each consisting of a list of three elements:
    # loa[abbreviation_short_uppercase] = [abbreviation_short, abbreviation_long, abbreviation_description]
    #
    # loa contains a list of unique artefact identifiers for each <artefact_identifier>.
    # The reason for this is that there are multiple references are possible !
    # loa[tag][<artefact>] = list(<artefact_id's>)
    #
    self.md.loa = collections.defaultdict(dict)
    # self.md.loa = collections.defaultdict(lambda: collections.defaultdict(list))
    self.md.loa[tag] = {}

    # unique identify counter for all artefacts
    self.md.loa_id_nr = collections.defaultdict(dict)
    self.md.loa_id_nr[tag] = {}

    # unique identified artefacts
    # artefact elements can be references multiple times
    # for linking we need a unique mapping
    # loa_id_map[artefact_id] = <artefact_text>
    # A unique id is given with the first parsing. This is used as reference later on.
    self.md.loa_id_map = collections.defaultdict(dict)
    self.md.loa_id_map[tag] = {}

    # If set the "list of artefacts" was seen and should be created
    # this creates id's and links back an forth between artefacts and the "list of artefacts" index
    self.md.loa_seen = collections.defaultdict(dict)
    self.md.loa_seen[tag] = False

    # map artefact_id to id_nr
    self.md.loa_artefact_id_to_id_nr = collections.defaultdict(dict)
    self.md.loa_artefact_id_to_id_nr[tag] = {}
    
    pass

# -------------------------------------------------------------------------------
class ArtefactException(Exception):
  name = "ArtefactException"
  message = ""

  def __init__(self, message):
    self.message = message

  def __str__(self):
    if self.message:
      return self.name + ': ' + self.message
    else:
      return self.name + ' has been raised'
