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
# Description:
# ============
# descriptions are normal lists but with a descriptive label at the beginning
# * [description]: details
#
# the idea is to reuse the normal list decoding and reformat the lists to descption list elements
# element:       => <ul> -> <dl>              <= replace
# [description]: => <dt>description</dt>      <= new elmement
# details        => <li> => <dd>details</dd>  <= replace type and content of li element !

# -------------------------------------------------------------------------------
class DescriptionTreeProcessor(Treeprocessor):

#  RE_DESCRIPTION_LIST = r'^\s*\[([^\]]+)\]\:\s*(.+)$'
  RE_DESCRIPTION_LIST = r'^\s*\*\*([^\*]+)\*\*:\s*(.+)$'

  def __init__(self, md, tools, config):
    super().__init__(md)
    self.tools = tools
    self.config = config

  def run(self, root):
    self.replace_list_with_descriptionlist(root)
    return None

  def replace_list_with_descriptionlist(self, element):
    li_cnt = 0
    if element.tag == "ul":
      li_cnt = 0
      dl_cnt = 0
      if self.config["verbose"]:
        self.tools.verbose(self.config["message_identifier"], "")
        self.tools.debug_etree(self.config["message_identifier"], "", element)

    for child in element:
      if element.tag == "ul":
        if child.tag == "li":
          li_cnt += 1
          if self.config["verbose"]:
              self.tools.verbose(self.config["message_identifier"], "LI: " + str(dl_cnt) + "/" + str(li_cnt) + " => " + str(child.text))
          matched = False
          if child.text:
            #mr = re.compile(self.RE_DESCRIPTION_LIST,  re.DOTALL)
            #m = mr.match(child.text)
            m = re.match(self.RE_DESCRIPTION_LIST, child.text, re.DOTALL)
            if m:
              dl_cnt += 1
              matched = True
              if self.config["verbose"]:
                  self.tools.verbose(self.config["message_identifier"], "  DL: " + str(dl_cnt) + "/" + str(li_cnt) + " => " + m.group(1) + " : " + m.group(2))
          if not matched:
            for subchild in child:
              if self.config["verbose"]:
                  self.tools.verbose(self.config["message_identifier"], " LI (SC) test: " + str(dl_cnt) + "/" + str(li_cnt) + " => " + str(subchild.text))
              if subchild.tag == "p":
                 m = re.match(self.RE_DESCRIPTION_LIST, subchild.text, re.DOTALL)
                 if m:
                   dl_cnt += 1
                   if self.config["verbose"]:
                       self.tools.verbose(self.config["message_identifier"], "    DL (SC): " + str(dl_cnt) + "/" + str(li_cnt) + " => " + m.group(1) + " : " + m.group(2))
        else:
          # we expect that ul elements only contain li elements !
          raise DescriptionException("ERROR: unexpected element not li in ul list instead it is of type " + child.tag)

      self.replace_list_with_descriptionlist(child)

    # return

    if li_cnt > 0 and dl_cnt > 0:
      # if there are any li elements (li_cnt>0) in ul element and any dl item to replace is seen (dl_cnt>0) then:

      if dl_cnt != li_cnt:
        # in case not all li elements follow descriptive defintion
        raise DescriptionException("ERROR: Only " + str(dl_cnt) + " of " + str(li_cnt) + " list items are proper description list items.")
      else:
        element.tag = 'dl' # replace ul with dl
        position = 0
        for child in element:
          position += 1

          # we expect li tags or previous with dd replaced li tags
          if not child.tag == "li" and not child.tag == "dd":
            raise DescriptionException("ERROR: (lic_cnt>0) unexpected element not li in ul list instead it is of type " + child.tag)

          # FIXME: implement check for <p> within list item ! => also check if we could have here more complex / different stuff too ?!

          matched = False
          if child.text:
            m = re.match(self.RE_DESCRIPTION_LIST, child.text, re.DOTALL)
            if m:
              matched = True
              child.tag = 'dd' # replace li with dd
              child.text = m.group(2) # replace text with "details"
              child.set('class', 'description_list')
              e_dt = etree.Element('dt')
              e_dt.text = m.group(1)
              e_dt.set('class', 'description_list')
              element.insert(position-1, e_dt)
          if not matched:
            for subchild in child:
              if subchild.tag == "p":
                 m = re.match(self.RE_DESCRIPTION_LIST, subchild.text, re.DOTALL)
                 if m:
                   child.tag = 'dd' # replace li with dd
                   child.set('class', 'description_list')
                   subchild.text = m.group(2) # replace text with "details"
                   e_dt = etree.Element('dt')
                   e_dt.text = m.group(1)
                   e_dt.set('class', 'description_list')
                   element.insert(position-1, e_dt)

# -------------------------------------------------------------------------------
class DescriptionExtension(Extension):

  DescriptionTreeProcessorClass = DescriptionTreeProcessor

  def __init__(self, tools, **kwargs):
    self.tools = tools
    self.config = {
      'message_identifier': [
        'DESCRIPTION',
        'Message Identifier',
        'Default: DESCRIPTION`.'
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

    # replace lists with description lists
    description_ext = self.DescriptionTreeProcessorClass(md, self.tools, self.getConfigs())
    md.treeprocessors.register(description_ext, 'reference__description', 165)

    # ------------
    # Inlineprocessors

    # ------------
    # Postprocessors

  def reset(self):
    # global variables to share between processing sequences

    pass

# -------------------------------------------------------------------------------
class DescriptionException(Exception):
  name = "DescriptionException"
  message = ""

  def __init__(self, message):
    self.message = message

  def __str__(self):
    if self.message:
      return self.name + ': ' + self.message
    else:
      return self.name + ' has been raised'
