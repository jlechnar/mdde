from markdown.inlinepatterns import InlineProcessor
from markdown.preprocessors import Preprocessor
from markdown.blockprocessors import BlockProcessor
from markdown.treeprocessors import Treeprocessor
from markdown.postprocessors import Postprocessor
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
    self.re_artefact = r'(.*)\{(' + config["tag"] + r':)([^\}]+)\}(.*)'

  def test(self, parent, block):
    return re.search(self.re_artefact, block)

  def run(self, parent, blocks):
    tag = self.config['tag']

    # multiple artefacts per line are possible so we iterate over them!
    seenany = False
    for match in re.finditer(self.re_artefact, blocks[0], re.DOTALL):
      seenany = True
      artefact = match.group(3)

      # number the artefacts to uniquify them
      if not artefact in self.md.loa_id_nr[tag]:
        self.md.loa_id_nr[tag][artefact] = 0
      self.md.loa_id_nr[tag][artefact] += 1

      # unique id by extending with number
      artefact_id = tag + ":" + artefact + ":" + str(self.md.loa_id_nr[tag][artefact])

      self.md.loa_artefact_id_to_id_nr[tag][artefact_id] = self.md.loa_id_nr[tag][artefact]

      # each artefact may be there multiple times
      # we need a list of uniqe ids so that we can print the loa
      if not artefact in self.md.loa[tag]:
        self.md.loa[tag][artefact] = []
      self.md.loa[tag][artefact].append(artefact_id)

      if self.config["verbose"]:
        self.tools.verbose(self.config["message_identifier"], "A (" + tag + "): " + artefact_id + " => " + artefact)

      self.md.loa_id_map[tag][artefact_id] = artefact

      # -----------------
      # reference => 3 cases
      # * matching (reference_seen)
      # * defined in reference but not in document (inverse list of reference_seen - evaluation possible after document is processed)
      # * defined in document but not in reference (reference_addon_seen)

      if artefact in self.md.reference_list[tag]:
        if not artefact in self.md.reference_seen[tag]:
          self.md.reference_seen[tag][artefact] = 0
        self.md.reference_seen[tag][artefact] += 1
      else:
        if not artefact in self.md.reference_addon_seen[tag]:
          self.md.reference_addon_seen[tag][artefact] = 0
        self.md.reference_addon_seen[tag][artefact] += 1

      # -----------------
      blocks[0] = match.group(1) + "{DONE:" + match.group(2) + artefact_id + "}" + match.group(4)

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
      self.re_loa = r'\{loa:' + config["tag"] + r'\}'

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

# -------------------------------------------------------------------------------
# Detects the 'list of missing artefacts' command and adds an etree element for later replacement
#
class ArtefactLoaMissingPositionBlockProcessor(BlockProcessor):

    def __init__(self, parser, tools, md, config):
      super().__init__(parser)
      self.md = md
      self.tools = tools
      self.config = config
      self.re_loam = r'\{loam:' + config["tag"] + r'\}'

    def test(self, parent, block):
      return re.match(self.re_loam, block)

    def run(self, parent, blocks):
      tag = self.config["tag"]

      m = re.search(self.re_loam, blocks[0])

      if m:
        d = etree.SubElement(parent, 'div')
        d.set('class', 'loam__' + self.config["tag"])
        self.md.loam_seen[tag] = True

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

  def __init__(self, md, tools, config):
    super().__init__(md)
    self.config = config
    self.tools = tools

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

            # --------------------
            if self.config["title_enable"]:
              e_loa_references = etree.SubElement(child, "p")
              e_loa_references.set("class", 'loa_' + tag + '_heading')
              e_loa_references.text = self.config["title"]

            # --------------------
            e_loa_div = etree.SubElement(child, "div")

            # e_loa_dl = etree.SubElement(e_loa_div, "dl")

            e_loa_table = etree.SubElement(e_loa_div, "table")
            e_loa_table.set('class', "loa__" + tag)

            # --------------------
            for artefact in sorted(self.md.loa[tag], key=natural_sortkey):

              e_loa_row = etree.SubElement(e_loa_table, "tr")

              e_loa_data = etree.SubElement(e_loa_row, "td")

              # --------------------
              if self.config["link"]:
                e1 = etree.SubElement(e_loa_data, 'a')
              else:
                e1 = etree.SubElement(e_loa_data, 'span')

              artefact_text = self.config["text_prefix"] + artefact + self.config["text_postfix"]

              #if self.numbered_links:
              #  e1.text = "[" + str(self.md.loa_labels_nr[label_link_id]) + "]"
              #else:
              e1.text = "[" + artefact_text + "]"

              if self.config["link"]:
                if artefact in self.md.reference_list[tag]:
                  if self.config["link_extend"]:
                    e1.set('href', self.md.reference_list[tag][artefact]['link'] + self.config["link_prefix"] + artefact + self.config["link_postfix"])
                  else:
                    e1.set('href', self.md.reference_list[tag][artefact]['link'])
                elif not self.config["no_link_for_missing_in_reference_list"]:
                  e1.set('href', self.config["link_prefix"] + artefact + self.config["link_postfix"])

              if artefact in self.md.reference_list[tag]:
                e1.set('title', self.md.reference_list[tag][artefact]['text'])
              else:
                a_title = ""
                #if self.numbered_links:
                #  a_title = "[" + str(self.md.loa_labels_nr[artefact_id]) + "] = "
                a_title += "[" + artefact_text + "]"
                e1.set('title', a_title)

              e1.set('class', tag + '_internal_reference')
              # e1.set('href', "#" + artefact_id)
              e1.set('id', "loa_"+ tag + ":" + artefact + ":")

              # ---------------
              e_loa_data_links = etree.SubElement(e_loa_row, "td")

              first_element = True

              for artefact_id in sorted(self.md.loa[tag][artefact], key=natural_sortkey):

                if self.config["verbose"]:
                    self.tools.verbose(self.config["message_identifier"], "LOA (" + tag + "): " + artefact_id + " => " + artefact)

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

      # ---------------------------------------------------------------
# Creates the 'list of missing artefacts'
#
class ArtefactLoaMissingReplaceTreeProcessor(Treeprocessor):

  def __init__(self, md, tools, config):
    super().__init__(md)
    self.config = config
    self.tools = tools

  def run(self, root):
    self.replace_loam(root)
    return None

  def replace_loam(self, element):
    tag = self.config["tag"]

    for child in element:
      if child.tag == "div":
        if child.get("class") is not None:
          m = re.match(r'loam__' + tag, child.get("class"))
          if m:

            # --------------------
            if self.config["title_missing_enable"]:
              e_loam_references = etree.SubElement(child, "p")
              e_loam_references.set("class", 'loam_' + tag + '_heading')
              e_loam_references.text = self.config["title_missing"]

            # --------------------
            e_loam_div = etree.SubElement(child, "div")

            # e_loam_dl = etree.SubElement(e_loam_div, "dl")

            e_loam_table = etree.SubElement(e_loam_div, "table")
            e_loam_table.set('class', "loam__" + tag)

            # --------------------
            for artefact in sorted(self.md.reference_list[tag], key=natural_sortkey):
              if not artefact in self.md.reference_seen[tag]:

                e_loam_row = etree.SubElement(e_loam_table, "tr")

                e_loam_data = etree.SubElement(e_loam_row, "td")

                # --------------------
                if self.config["link"]:
                  e1 = etree.SubElement(e_loam_data, 'a')
                else:
                  e1 = etree.SubElement(e_loam_data, 'span')

                artefact_text = self.config["text_prefix"] + artefact + self.config["text_postfix"]

                #if self.numbered_links:
                #  e1.text = "[" + str(self.md.loam_labels_nr[label_link_id]) + "]"
                #else:
                e1.text = "[" + artefact_text + "]"

                if self.config["link"]:
                  if artefact in self.md.reference_list[tag]:
                    if self.config["link_extend"]:
                      e1.set('href', self.md.reference_list[tag][artefact]['link'] + self.config["link_prefix"] + artefact + self.config["link_postfix"])
                    else:
                      e1.set('href', self.md.reference_list[tag][artefact]['link'])
                  elif not self.config["no_link_for_missing_in_reference_list"]:
                    e1.set('href', self.config["link_prefix"] + artefact + self.config["link_postfix"])

                if artefact in self.md.reference_list[tag]:
                  e1.set('title', self.md.reference_list[tag][artefact]['text'])
                else:
                  a_title = ""
                  #if self.numbered_links:
                  #  a_title = "[" + str(self.md.loam_labels_nr[artefact_id]) + "] = "
                  a_title += "[" + artefact_text + "]"
                  e1.set('title', a_title)

                e1.set('class', tag + '_internal_reference')
                # e1.set('href', "#" + artefact_id)
                e1.set('id', "loam_"+ tag + ":" + artefact + ":")


      self.replace_loam(child)

# ------------------------------------------------------------------------
# replaces each artefact to the final structure
# adds links, pre/postfixes, etc.
#
class ArtefactReplaceInlineProcessor(InlineProcessor):

  def __init__(self, pat, md, config):
    super().__init__(pat, md)
    self.config = config

  def handleMatch(self, m, md):
    artefact_id = m.group(1)
    # label_link_id = m.group(1)
    # label_text = self.md.lor_labels[label_link_id]


    e0 = etree.Element('span')

    # --------------------
    tag = self.config["tag"]

    artefact = self.md.loa_id_map[tag][artefact_id]

    # --------------------
    if self.config["link"]:
      e1 = etree.SubElement(e0, 'a')
    else:
      e1 = etree.SubElement(e0, 'span')

    e1.set('class', tag)

    if self.md.loa_seen[tag] is True:
      e1.set('id', artefact_id)
    e1.text = self.config["text_prefix"] + artefact + self.config["text_postfix"]

    if self.config["link"]:
      if artefact in self.md.reference_list[tag]:
        if self.config["link_extend"]:
          e1.set('href', self.md.reference_list[tag][artefact]['link'] + self.config["link_prefix"] + artefact + self.config["link_postfix"])
        else:
          e1.set('href', self.md.reference_list[tag][artefact]['link'])
      elif not self.config["no_link_for_missing_in_reference_list"]:
        e1.set('href', self.config["link_prefix"] + artefact + self.config["link_postfix"])

    if artefact in self.md.reference_list[tag]:
      e1.set('title', self.md.reference_list[tag][artefact]['text'])
    else:
      artefact_text = self.config["text_prefix"] + artefact + self.config["text_postfix"]
      a_title = ""
      a_title += "[" + artefact_text + "]"
      e1.set('title', a_title)

    # ------------------
    # lor link back in case to loa seen
    if self.md.loa_seen[tag] is True:
      e2 = etree.SubElement(e0, 'a')

      e2.set('href', f"#loa_{tag}:{artefact}:")
      e2.set('class', f"{tag}:internal_reference")
      e2.set('title', f"[{artefact_id}]")

      e2.text = self.config["reference_symbol"]

    return e0, m.start(0), m.end(0)

# -------------------------------------------------------------------------------
# postprocessor is missused below to trigger writeout of information
class ArtefactPostprocessor(Postprocessor):

  def __init__(self, md, config):
    super().__init__(md)
    self.config = config

  def run(self, text):
    tag = self.config['tag']

    if self.config["reference_list_mapped_file_name"]:
      fh = open(self.config["reference_list_mapped_file_name"], "w")

      # output format: [UNUSED/USED/NEW]: <id> <count>
      for artefact in self.md.reference_list[tag]:
        if artefact in self.md.reference_seen[tag]:
          fh.write(f"USED:   {artefact} {self.md.reference_seen[tag][artefact]}\n")
        else:
          fh.write(f"UNUSED: {artefact} 0\n")

      for artefact in self.md.reference_addon_seen[tag]:
        fh.write(f"NEW:    {artefact} {self.md.reference_addon_seen[tag][artefact]}\n")

      fh.close()

    return text

# -------------------------------------------------------------------------------
class ArtefactExtension(Extension):

  ArtefactLoaReplaceTreeProcessorClass = ArtefactLoaReplaceTreeProcessor
  ArtefactLoaMissingReplaceTreeProcessorClass = ArtefactLoaMissingReplaceTreeProcessor
  ArtefactPostprocessorClass = ArtefactPostprocessor

  def __init__(self, tools, **kwargs):
    self.tools = tools
    self.config = {
      'message_identifier': [
          'ARTEFACT',
          'Message Identifier',
          'Default: ARTEFACT`.'
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
      'link': [
        False,
        'is a link or not',
        'Default: off`.'
      ],
      'link_extend': [
        False,
        'Extend the reference list links with ...+link_prefix+artefact+link_postfix',
        'Default: off`.'
      ],
      'no_link_for_missing_in_reference_list': [
        False,
        'Disables link in case of missing in reference list',
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
      'reference_symbol': [
        "*", # e.g. "&#x1F517;" => link, "&#x2693;" => anchor
        'Select symbol to be used for references',
        'Default: *`.'
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
        'Enable Title printing for LOA',
        'Default: on`.'
      ],
      'title': [
        'List of Artefacts',
        'Title for LOA',
        'Default: `List of Artefacts`.'
      ],
      'title_missing_enable': [
        True,
        'Enable Title printing for LOAM',
        'Default: on`.'
      ],
      'title_missing': [
        'List of Missing Artefacts',
        'Title for LOAM',
        'Default: `List of Missing Artefacts`.'
      ],
      'reference_list_file_name': [
        "",
        'Name of file to be used for mapping artefacts to a reference list. The contents is space separated: <name> <base_link>.',
        'Default: \"\"`.'
      ],
      'reference_list_mapped_file_name': [
        "",
        'Name of file to be used for writing map results to. Requires \'reference_list_file_name\' to be set !!!',
        'Default: \"\"`.'
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
    md.parser.blockprocessors.register(ArtefactLoaMissingPositionBlockProcessor(md.parser, self.tools, md, self.getConfigs()), md_id + '__loam_position', 165)

    # ------------
    # Treeprocessors
    md.treeprocessors.register(self.ArtefactLoaReplaceTreeProcessorClass(md, self.tools, self.getConfigs()), md_id + '__loa_replace', 165)
    md.treeprocessors.register(self.ArtefactLoaMissingReplaceTreeProcessorClass(md, self.tools, self.getConfigs()), md_id + '__loam_replace', 165)

    # ------------
    # Inlineprocessors

    ARTEFACT_PATTERN = r'\{DONE:' + self.config["tag"][0] + r':([^\}]+)\}'
    # >190-194 required as else parts inside code sections do not get replaced before code is decoded by python-markdown !!!
    # then the conversion gets ignored !
    # but we also have the issue that the code is then pure text, hence decoding is not that easy anymore in codes :(
    md.inlinePatterns.register(ArtefactReplaceInlineProcessor(ARTEFACT_PATTERN, md, self.getConfigs()), md_id + '_replace_inline', 200)

    # ------------
    # Postprocessors
    self.md.postprocessors.register(self.ArtefactPostprocessorClass(md, self.getConfigs()), md_id + '_postprocess', 165)

  # -------------------------------------------------------------
  def reset(self):
    # global variables to share between processing sequences

    # not that tag's below are required as we could have extended classes with different types of this class.
    # tag's are used for differentiation between different types of classes
    tag = self.config['tag'][0]

    # FIXME: we have an issue here with a not straight forward solution that might break in future
    # we must not initialize the data sets below multiple times but only once as md is shared between all of the classes artefact and derived ones
    # we cannot do this during initialization as md is not available
    # hence we bind it to artefact only which must be first in the list of extensions to be added + exist in the list of extensions
    # we should find a better way to solve this issue as behavior could change in future !
    if tag == "artefact":
      self.md.loa = collections.defaultdict(dict)
      # self.md.loa = collections.defaultdict(lambda: collections.defaultdict(list))
      self.md.loa_id_nr = collections.defaultdict(dict)
      self.md.loa_id_map = collections.defaultdict(dict)
      self.md.loa_seen = collections.defaultdict(dict)
      self.md.loam_seen = collections.defaultdict(dict)
      self.md.loa_artefact_id_to_id_nr = collections.defaultdict(dict)
      self.md.reference_list = collections.defaultdict(dict)
      self.md.reference_seen = collections.defaultdict(dict)
      self.md.reference_addon_seen = collections.defaultdict(dict)

    # FIXME: update below
    # loa contains the table of contents in the form of dictionary entries each consisting of a list of three elements:
    # loa[abbreviation_short_uppercase] = [abbreviation_short, abbreviation_long, abbreviation_description]
    #
    # loa contains a list of unique artefact identifiers for each <artefact_identifier>.
    # The reason for this is that there are multiple references are possible !
    # loa[tag][<artefact>] = list(<artefact_id's>)
    #
    self.md.loa[tag] = {}

    # unique identify counter for all artefacts
    self.md.loa_id_nr[tag] = {}

    # unique identified artefacts
    # artefact elements can be references multiple times
    # for linking we need a unique mapping
    # loa_id_map[artefact_id] = <artefact_text>
    # A unique id is given with the first parsing. This is used as reference later on.
    self.md.loa_id_map[tag] = {}

    # If set the "list of artefacts" was seen and should be created
    # this creates id's and links back an forth between artefacts and the "list of artefacts" index
    self.md.loa_seen[tag] = False

    # If set the "missing list of artefacts" was seen and should be created
    # this creates id's and links back an forth between artefacts and the "missing list of artefacts" index
    self.md.loam_seen[tag] = False

    # map artefact_id to id_nr
    self.md.loa_artefact_id_to_id_nr[tag] = {}

    # map to reference list file for evaluation of seen/missing artefact references
    self.md.reference_list[tag] = {}
    # lists that are used for counting to occurences of references
    self.md.reference_seen[tag] = {}
    # document defined artefacts that are missing in the given reference list
    self.md.reference_addon_seen[tag] = {}

    # ----------------------
    if self.config["reference_list_file_name"][0]:
      try:
        lines2 = self.tools.read_file(self.config["reference_list_file_name"][0],"%",1000000)
      except ToolException as e:
        raise ArtefactException(f"Error when reading from {self.config['reference_list_file_name'][0]}:\n " + str(e))

      # name origin link text
      p = re.compile(r'^(\S+)\s+(\S+)\s+(\S+)(|\s.+)$')

      for line in lines2:
        m = p.match(line)
        if m:
          artefact = m.group(1)
          self.md.reference_list[tag][artefact] = {}
          self.md.reference_list[tag][artefact]['origin'] = m.group(2)
          self.md.reference_list[tag][artefact]['link'] = m.group(3)
          self.md.reference_list[tag][artefact]['text'] = m.group(4)

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
