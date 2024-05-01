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
# Reference->Label links:
# =======================
# References to lables are defined as       [<reference_text>](#<label_title>)
# Labels are defined as                     [<label_text>][#<label_title>]
#
# References/labels use the original way of markdown to define a redefined link.
# Note that # is used there to differentiate between redefined link and reference/labels.
# The reuse/missuse is not perfect but we automatically get syntax highlighting with this approach.

# -------------------------------------------------------------------------------
#
class LabelBlockProcessor(BlockProcessor):

  RE_LABEL = r'\[([^\]]*)\]\[#([^\]]+)\]'

  def __init__(self, parser, tools, md, config):
    super().__init__(parser)
    self.md = md
    self.tools = tools
    self.config = config

  def test(self, parent, block):
    return re.search(self.RE_LABEL, block)

  def run(self, parent, blocks):

    m = re.search(self.RE_LABEL, blocks[0])

    if m:
      label_text = m.group(1)
      label_link_id = m.group(2)

      if self.config["debug"]:
        self.tools.debug("INT REF: " + label_link_id + ": \"" + label_text + "\"")

      if label_link_id in self.md.lor_labels:
        LabelsReferencesException("FATAL: Duplicated definition of internal reference: " + label_link_id)
      else:
        self.md.lor_labels[label_link_id] = label_text

      self.md.lor_labels_nr_cnt = self.md.lor_labels_nr_cnt + 1
      self.md.lor_labels_nr[label_link_id] = self.md.lor_labels_nr_cnt

      # prepare for later replacement
      blocks[0] = re.sub(re.escape(m.group(0)), "{LABEL:" + label_link_id + "}", blocks[0])

      return True
    else:
      return False

# -------------------------------------------------------------------------------
#
class ReferenceBlockProcessor(BlockProcessor):

  RE_REFERENCE = r'\[([^\]]*)\]\(#([^\]]+)\)'

  def __init__(self, parser, tools, md, config):
    super().__init__(parser)
    self.md = md
    self.tools = tools
    self.config = config

  def test(self, parent, block):
    return re.search(self.RE_REFERENCE, block)

  def run(self, parent, blocks):

    m = re.search(self.RE_REFERENCE, blocks[0])

    if m:
      reference_text = m.group(1)
      reference_link = m.group(2)

      if self.config["debug"]:
        self.tools.debug("INT LINK: " + reference_link + ": \"" + reference_text + "\"")

      # FIXME: we need a check but we need it later when everything is read in !
      # if not self.lor.ilor[]

      if not reference_link in self.md.lor_labels:
        LabelsReferencesException("FATAL: Undefined label for reference to: " + reference_link)

      if not reference_link in self.md.lor_references_index:
        self.md.lor_references_index[reference_link] = 0
      self.md.lor_references_index[reference_link] += 1
      reference_link_id = str(reference_link + ":" + str(self.md.lor_references_index[reference_link]))
      if reference_link_id in self.md.lor_references:
        raise LabelsReferencesException("FATAL: exists already")
      self.md.lor_references[reference_link_id] = [reference_link, reference_text]

      self.md.lor_references_nr_cnt = self.md.lor_references_nr_cnt + 1
      self.md.lor_references_nr[reference_link_id] = self.md.lor_references_nr_cnt

      if not reference_link in self.md.lor_labels_references:
        self.md.lor_labels_references[reference_link] = []
      self.md.lor_labels_references[reference_link].append(reference_link_id)

      # prepare for later replacement
      blocks[0] = re.sub(re.escape(m.group(0)), "{REFERENCE:" + reference_link_id + "}", blocks[0])

      return True

    else:
      return False

# -------------------------------------------------------------------------------
class LorPositionBlockProcessor(BlockProcessor):
  RE_LOR = r'^{lor}$'

  def test(self, parent, block):
    return re.match(self.RE_LOR, block)

  def run(self, parent, blocks):

    m_lor = re.search(self.RE_LOR, blocks[0])

    if m_lor:
      d = etree.SubElement(parent, 'div')
      d.set('class', 'lor')

      blocks[0] = re.sub(re.escape(m_lor.group(0)), '', blocks[0])
      return True
    else:
      return False

# ---------------------------------------------------------------
class LorReplaceTreeProcessor(Treeprocessor):

  def __init__(self, md, config):
    super().__init__(md)
    self.config = config

  def run(self, root):
    self.replace_lor(root)
    return None

  def replace_lor(self, element):
    for child in element:
      if child.tag == "div":
        if child.get("class") is not None:
          m = re.match(r'lor', child.get("class"))
          if m:
            if self.config["title_enable"]:
              elor_references = etree.SubElement(child, "p")
              elor_references.set("class", 'lor_heading')
              elor_references.text = self.config["title"]

            elor_div = etree.SubElement(child, "div")

            elor_dl = etree.SubElement(elor_div, "dl")

            elor_table = etree.SubElement(elor_div, "table")
            elor_table.set('class', "lor")

            for label_link_id in self.md.lor_labels:
              label_text = self.md.lor_labels[label_link_id]

              # --------
              elor_row = etree.SubElement(elor_table, "tr")

              elor_data = etree.SubElement(elor_row, "td")
              a = etree.SubElement(elor_data, 'a')
              if self.config["numbered_links"]:
                a.text = "[" + str(self.md.lor_labels_nr[label_link_id]) + "]"
              else:
                a.text = "[" + label_link_id + "]"
              #
              a_title = ""
              if self.config["numbered_links"]:
                a_title = "[" + str(self.md.lor_labels_nr[label_link_id]) + "] = "
              a_title += "[" + label_link_id + "]"
              a.set('title', a_title)
              #
              a.set('class', 'internal_reference')
              a.set('href', "#" + label_link_id)
              a.set('id', "lor:" + label_link_id + ":")

              elor_data = etree.SubElement(elor_row, "td")
              elor_data.text = label_text

              # --------
              if label_link_id in self.md.lor_labels_references:
                for reference_link_id in self.md.lor_labels_references[label_link_id]:

                  if reference_link_id in self.md.lor_references:
                    [reference_link, reference_text] = self.md.lor_references[reference_link_id]

                    elor_row = etree.SubElement(elor_table, "tr")

                    elor_data = etree.SubElement(elor_row, "td")
                    a = etree.SubElement(elor_data, 'a')
                    if self.config["numbered_links"]:
                      a.text = "&nbsp;&nbsp;" + "&#x21b3;" + "[" + str(self.md.lor_references_nr[reference_link_id]) + "]"
                    else:
                      a.text = "&nbsp;&nbsp;" + "&#x21b3;" + "[" + reference_link_id + "]"
                    #
                    a_title = ""
                    if self.config["numbered_links"]:
                      a_title = "[" + str(self.md.lor_references_nr[reference_link_id]) + "] = "
                    a_title += "[" + reference_link_id + "]"
                    a.set('title', a_title)
                    #
                    a.set('class', 'internal_reference_link')
                    a.set('href', "#" + reference_link_id)

                    elor_data = etree.SubElement(elor_row, "td")
                    elor_data.text = reference_text
                  else:
                    LabelsReferencesException("missing ID for <" + reference_link_id + "> in lor_references.")

      self.replace_lor(child)

# ---------------------------------------------------------------
class LABELTOCReplaceTreeProcessor(Treeprocessor):

  RE_LABEL = r'^(.*\{)(LABEL:)([^\}]+\}.*)$'

  def __init__(self, md, config):
    super().__init__(md)

  def run(self, root):
    self.replace_toc(root, False)
    return None

  def replace_toc(self, element, do_replace):
    for child in element:
      if child.tag == "a":
        if child.get("class") is not None:
          m = re.match(r'toc_heading_links_text', child.get("class"))
          if m:
            do_replace = True

      if do_replace:
        if child.text:
          child.text = re.sub('LABEL', 'TOC_LABEL' , child.text)

      self.replace_toc(child, do_replace)

# ------------------------------------------------------------------------
class LabelReplaceInlineProcessor(InlineProcessor):

  def __init__(self, pat, md, set_id, config):
    super().__init__(pat, md)
    self.config = config
    self.set_id = set_id

  def handleMatch(self, m, md):
    label_link_id = m.group(1)
    label_text = self.md.lor_labels[label_link_id]
    a = etree.Element('a')
    if self.set_id:
      a.set('id', label_link_id)
    a.set('href', '#' + "lor:" + label_link_id + ":")
    a.set('class', 'internal_reference')
    # FIXME: recursive eetree processing for below ???

    a.text = self.config["reference_symbol"]
    #
    a_title = ""
    if self.config["numbered_links"]:
      a_title = "[" + str(self.md.lor_labels_nr[label_link_id]) + "] = "
    a_title += "[" + label_link_id + "]: " + label_text
    a.set('title', a_title)

    return a, m.start(0), m.end(0)

# ------------------------------------------------------------------------
class ReferenceReplaceInlineProcessor(InlineProcessor):

  def __init__(self, pat, md, config):
    super().__init__(pat, md)
    self.config = config

  def handleMatch(self, m, md):
    reference_link_id = m.group(1)
    [reference_link, reference_text] = self.md.lor_references[reference_link_id]

    label_link_id = reference_link
    if not label_link_id in self.md.lor_labels:
      LabelsReferencesException("ERROR: Missing link to refrerence with id: <" + label_link_id + ">")
    label_text = self.md.lor_labels[label_link_id]

    a = etree.Element('a')
    a.set('id', reference_link_id)
    a.set('href', '#' + reference_link)
    a_title = ""
    if self.config["numbered_links"]:
      a_title = "[" + str(self.md.lor_labels_nr[label_link_id]) + "] = "
    a_title += "[" + reference_link_id + "]" + "&#x2794;" + "[" + label_link_id + "]: " + label_text
    a.set('title', a_title)
    a.set('class', 'internal_reference_link')
    if reference_text:
      a.text = reference_text
    else:
      if self.config["numbered_links"]:
        a.text = "[" + str(self.md.lor_labels_nr[label_link_id]) + "]"
      else:
        a.text = "[" + label_link_id + "]"
    return a, m.start(0), m.end(0)

# -------------------------------------------------------------------------------
class LabelsReferencesExtension(Extension):

  LorReplaceTreeProcessorClass = LorReplaceTreeProcessor

  LABELTOCReplaceTreeProcessorClass = LABELTOCReplaceTreeProcessor

  def __init__(self, tools, **kwargs):
    self.tools = tools
    self.config = {
      'debug': [
        False,
        'Debug mode'
        'Default: off`.'
      ],
      'verbose': [
        False,
        'Verbose mode'
        'Default: off`.'
      ],
      'numbered_links': [
        False,
        'Enable numbered links instead of text'
        'Default: off`.'
      ],
      'reference_symbol': [
        "*", # e.g. "&#x1F517;" => link, "&#x2693;" => anchor
        'Select symbol to be used for references',
        'Default: *`.'
      ],
      'title_enable': [
        True,
        'Enable Title printing'
        'Default: on`.'
      ],
      'title': [
        'List of References',
        'Title for LOR'
        'Default: `List of References`.'
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

    md.parser.blockprocessors.register(LabelBlockProcessor(md.parser, self.tools, md, self.getConfigs()), 'reference_block_processor', 165)
    md.parser.blockprocessors.register(ReferenceBlockProcessor(md.parser, self.tools, md, self.getConfigs()), 'reference_link_block_processor', 164)

    # prepare lor for replacement
    md.parser.blockprocessors.register(LorPositionBlockProcessor(md.parser), 'reference__lor_position', 165)

    # ------------
    # Treeprocessors

    # generate lor
    lor_replace_ext = self.LorReplaceTreeProcessorClass(md, self.getConfigs())
    md.treeprocessors.register(lor_replace_ext, 'reference__lor_replace', 187)

    intref_toc_replace_ext = self.LABELTOCReplaceTreeProcessorClass(md, self.getConfigs())
    md.treeprocessors.register(intref_toc_replace_ext, 'reference__intref_toc_replace', 157)
    # ------------
    # Inlineprocessors

    LABEL_PATTERN = r'\{LABEL:([^\}]+)\}'
    md.inlinePatterns.register(LabelReplaceInlineProcessor(LABEL_PATTERN, md, True, self.getConfigs()), 'reference__intref_replace_inline', 165)

    LABEL_TOC_PATTERN = r'\{TOC_LABEL:([^\}]+)\}'
    md.inlinePatterns.register(LabelReplaceInlineProcessor(LABEL_TOC_PATTERN, md, False, self.getConfigs()), 'reference__intref_replace_inline_toc', 165)

    REFERENCE_PATTERN = r'\{REFERENCE:([^\}]+)\}'
    md.inlinePatterns.register(ReferenceReplaceInlineProcessor(REFERENCE_PATTERN, md, self.getConfigs()), 'reference__intreflink_replace_inline', 165)

    # ------------
    # Postprocessors

  def reset(self):
    # global variables to share between processing sequences

    # lor_labels contains the list of references in the form of dictionary entries:
    # lor_labels[label_link_id] = label_text
    #
    self.md.lor_labels = {}

    # lor_references contains the list of reference links in the form of dictionary consisting of a list of link elements:
    self.md.lor_references = {}

    # lor_references_index containts the running index for backlinks to the label
    self.md.lor_references_index = {}

    # lor_labels_references containts a list per label for finding back the way from a label to its references and vise versa
    self.md.lor_labels_references = {}

    # lor_labels_nr_cnt counts for unique numbers for id's in case of numbered linking (for references)
    self.md.lor_labels_nr_cnt = 0

    # lor_labels_nr defines a backlink to the unique number
    self.md.lor_labels_nr = {}

    # lor_references_nr_cnt counts for unique numbers for id's in case of numbered linking (for refrence links)
    self.md.lor_references_nr_cnt = 0

    # lor_references_nr defines a backlink to the unique number
    self.md.lor_references_nr = {}

    pass

# -------------------------------------------------------------------------------
class LabelsReferencesException(Exception):
  name = "LabelsReferencesException"
  message = ""

  def __init__(self, message):
    self.message = message

  def __str__(self):
    if self.message:
      return self.name + ': ' + self.message
    else:
      return self.name + ' has been raised'
