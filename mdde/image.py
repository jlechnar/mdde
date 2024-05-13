from markdown.inlinepatterns import InlineProcessor
from markdown.preprocessors import Preprocessor
from markdown.blockprocessors import BlockProcessor
from markdown.treeprocessors import Treeprocessor
from markdown.extensions import Extension
import xml.etree.ElementTree as etree
import re
import copy
from os.path import exists

# Description: MarkDown Documentation Extensions [MDDE] - 
# Author:      jlechnar
# Licence:     MIT Licence 
# Source:      https://github.com/jlechnar/mdde


# -------------------------------------------------------------------------------
#
class ImageBlockProcessor(BlockProcessor):
  # ![<alternative_text_if_image_is_gone>](<image_path> "<hover_text>"): <description>
  #
  # ![...](...):...
  # ![](...):...
  # !(...):...
  RE_IMAGE = r'\!(|\[([^\]]*)\])\(([^\)]+)\)\s*\:\s*(.+)'
  # contents of (...) => (... "...") = (<image_path> "<hover text>")
  #
  RE_IMAGE_HOOVER = r'^(.+)\s+\"([^\"]*)\"\s*$'

  def __init__(self, tools, parser, md, config):
    super().__init__(parser)
    self.md = md
    self.tools = tools
    self.config = config

  def test(self, parent, block):
    return re.search(self.RE_IMAGE, block)

  def run(self, parent, blocks):

    m = re.search(self.RE_IMAGE, blocks[0])

    if m:
      image_alt = ""

      if m.group(2) is None:
        image_description = m.group(4)
        if self.config["verbose"]:
          self.tools.verbose(self.config["message_identifier"], "IMAGE: <" + blocks[0] + ">:\n  <NONE>\n  <" + m.group(3)+ ">\n  <" + m.group(4)+ ">")
      else:
        image_alt = m.group(2)
        image_description = m.group(4)
        if self.config["verbose"]:
          self.tools.verbose(self.config["message_identifier"], "IMAGE: <" + blocks[0] + ">:\n  <" + m.group(2) + ">\n  <" + m.group(3)+ ">\n  <" + m.group(4)+ ">")

      image_src = m.group(3)
      image_title = ""

      mh = re.search(self.RE_IMAGE_HOOVER, m.group(3))
      if mh:
        image_src = mh.group(1)
        image_title = mh.group(2)
        if self.config["verbose"]:
          self.tools.verbose(self.config["message_identifier"], "    <" + mh.group(1) + ">\n    <" + mh.group(2) + ">")
      else:
        if self.config["verbose"]:
          self.tools.verbose(self.config["message_identifier"], "    NO HOVER TEXT")

      # ---------------------------------
      # <p>
      #   <a>[link and id]</a>
      #   [description]
      #   <br>
      #   <img>
      # </p>
      p = etree.SubElement(parent, 'p')

      # ========================================
      # ========================================
      # description
      #
      # <id + link><description>:

      # ---------------------------------
      # add anchor to/from loi
      # <p ...><a id="anchor_for_link_from_loi" href="link_to_loi">...</a></p>
      # <h...><a id="anchor_for_link_from_loi" href="link_to_loi">...</a></h...>
      a = etree.SubElement(p, 'a')

      # FIXME:
      self.md.loi_index_id_list[-1] += 1

      #if len(self.md.loi_index_id_list)
      # image = "1." # FIXME

      # merge current loi_index_id_list to index_id string e.g. [1, 3, 4] => "1.3.4."
      image_id = ""
      for i in range(len(self.md.loi_index_id_list)):
        image_id += str(self.md.loi_index_id_list[i]) + "."

#      image_text = "image_" + index_id

      #self.md.loi_loi.append([index_id, image_description])
      self.md.loi_loi.append([image_id, image_title])

      image_id2 = "image:" + image_id + ":"
      image_ref = "loi:" + image_id + ":"

      p.set('id', image_id2) # set anchor to paragraph so that we can move the description before/after image
      a.set('href', "#" + image_ref)
      a.set('class', 'image_loi_links')

      s0 = etree.SubElement(a, 'span')
      s0.set('class', 'image_prefix')
      s0.text = "Image "

      # add index
      s1 = etree.SubElement(a, 'span')
      s1.set('class', 'image_index')
      s1.text = image_id

      # add space between index and text
      s2 = etree.SubElement(a, 'span')
      s2.set('class', 'image_space')
      s2.text = " "

      # ---------------
      image_description_text = image_description
      if image_description_text == "":
        image_description_text = image_title
      if image_description_text == "":
        image_description_text = image_alt
      if image_description_text == "":
        image_description_text = "TBD"

      # ---------------
      image_title_text = image_title
      if image_title_text == "":
        image_title_text = image_alt
      if image_title_text == "":
        image_title_text = image_description
      if image_title_text == "":
        image_title_text = "TBD"

      # ---------------
      # image text in s2, mark as image_text class for later replace of surrounding <p>...</> that gets added automatically by the tool !
      s3 = etree.SubElement(a, 'span')
      s3.set('class', 'image_text')
      s3.set('text', image_description_text)

      #s4 = etree.SubElement(a, 'span')
      #s4.set('class', 'image_title')
      #s4.set('title', image_title_text)

      ## s4 = etree.SubElement(a, 'span')
      ## s4.set('class', 'image_postfix')
      ## s4.text = ": "

      # ----------------
      s = etree.SubElement(p, 'span')
      s.text = image_description_text

      # ----------------
      # add link to base if exists
      image_src_base = re.sub(r'\.([^\.]+)$', '', image_src)

      if image_src != image_src_base:
        if exists(image_src_base):

          s = etree.SubElement(p, 'span')
          s.text = " ("

          a = etree.SubElement(p, 'a')
          a.text = image_src_base
          a.set('href', image_src_base)

          s = etree.SubElement(p, 'span')
          s.text = ")"

      # ========================================
      # ========================================
      b = etree.SubElement(p, 'br')

      # ========================================
      # ========================================
      a = etree.SubElement(p, 'a')
      a.set('href', image_src)

      e = etree.SubElement(a, 'img')
      e.set('src', image_src)
      if image_alt != "":
        e.set('alt', image_alt)
      if image_title != "":
        e.set('title', image_title)

      # ---------------------------------
      # remove parsed image block
      blocks[0] = re.sub(re.escape(m.group(0)), '', blocks[0])
#
#      # parse image text if it is more complex
#      self.parser.parseBlocks(s3, [m.group(6)])

      return True
    else:
      return False

# -------------------------------------------------------------------------------
class LoiPositionBlockProcessor(BlockProcessor):
  RE_LOI = r'^{loi}$'

  def test(self, parent, block):
    return re.match(self.RE_LOI, block)

  def run(self, parent, blocks):

    m = re.search(self.RE_LOI, blocks[0])

    if m:
      d = etree.SubElement(parent, 'div')
      d.set('class', 'loi')

      blocks[0] = re.sub(re.escape(m.group(0)), '', blocks[0])
      return True
    else:
      return False

# ---------------------------------------------------------------
class LoiReplaceTreeProcessor(Treeprocessor):

  def __init__(self, tools, md, config):
    super().__init__(md)
    self.config = config
    self.tools = tools

  def run(self, root):
    self.replace_loi(root)
    return None

  def replace_loi(self, element):
    for child in element:
      if child.tag == "div":
        if child.get("class") is not None:
          m = re.match(r'loi', child.get("class"))
          if m:
             if self.config["title_enable"]:
               eloi_image = etree.SubElement(child, "p")
               eloi_image.set("class", 'loi_image')
               eloi_image.text = self.config["title"]

             eloi_div = etree.SubElement(child, "div")
             eloi_table = etree.SubElement(eloi_div, "table")
             eloi_table.set('class', "loi")
             for loi in self.md.loi_loi:
               eloi_row = etree.SubElement(eloi_table, "tr")

               eloi_data = etree.SubElement(eloi_row, "td")
               eloi_a = etree.SubElement(eloi_data, "a")
               # Only one link valid ! skipped below intentionally
               #eloi_a.set('id', "loi:" + loi[0] + ":")
               eloi_a.set('href', "#" + "image:" + loi[0] + ":")
               eloi_a.set('class', 'loi_image_links_index')
               eloi_a.text = loi[0]

               eloi_data = etree.SubElement(eloi_row, "td")
               eloi_a = etree.SubElement(eloi_data, "a")
               eloi_a.set('id', "loi:" + loi[0] + ":")
               eloi_a.set('href', "#" + "image:" + loi[0] + ":")
               eloi_a.set('class', 'loi_image_links_text')
               eloi_a.text = loi[1]

      self.replace_loi(child)

# ---------------------------------------------------------------
#
# replace contents/text of loi link with the one of the image (same decoded structure)
# heading is decoded further after processing - here we duplicate the decoded text to the one used in the loi, which can still be undecoded due to processing structure
#
class LoiRefineTreeProcessor(Treeprocessor):

  def __init__(self, tools, md, config):
    super().__init__(md)
    self.tools = tools
    self.config = config

  def run(self, root):
    self.refine_loi(root, root)
    return None

  def refine_loi(self, element, root):
    for child in element:
      if child.tag == "a":
        if child.get("class") is not None:
          m = re.match(r'image_loi_links', child.get("class"))
          if m:
            image_index = None
            image_text_copy = None
            for sub_child in child:
              if sub_child.get("class") is not None:
                mi = re.match(r'image_index', sub_child.get("class"))
                if mi:
                  image_index = sub_child.text

                mt = re.match(r'image_text', sub_child.get("class"))
                if mt:
                  # Flatten surrounding span might not be that easy hence keep it
                  # duplicate image_text element to image_text_copy used in loi
                  image_text_copy = copy.deepcopy(sub_child)
                  del image_text_copy.attrib["class"]
                  image_text_copy.text = image_text_copy.get('text')
                  del image_text_copy.attrib["text"]

            if image_index is None:
              raise ImageException("FATAL: LoiRefineTreeProcessor: Could not find not find image_index.")

            if image_text_copy is None:
              raise ImageException("FATAL: LoiRefineTreeProcessor: Could not find image_text.")

            self.refine_replace_loi(root, image_index, image_text_copy)
      self.refine_loi(child, root)

  def refine_replace_loi(self, element, image_index, image_text_copy):
    for child in element:
      if child.tag == "a":
        if child.get("class") is not None:
          m = re.match(r'loi_image_links_text', child.get("class"))
          if m:
            mi = re.match("loi:" + image_index + ":", child.get("id"))
            if mi:
              # Replace temporary text with decoded one from image
              child.text = ""
              child.insert(0, image_text_copy)
      self.refine_replace_loi(child, image_index, image_text_copy)

# ---------------------------------------------------------------
#
# refine/replace loi link text with decoded text from image
# refine link names between loi and images
# link names then contains the image inside the link for readable references
# note that before only id's are part of the link name hence links are not human readable
# in case of document changes it is easier if image is part of the link name
#
class LoiRefineLinksTreeProcessor(Treeprocessor):

  def __init__(self, tools, md, config):
    super().__init__(md)
    self.tools = tools
    self.config = config

  def run(self, root):
    self.refine_links_loi(root, root)
    return None

  def refine_links_loi(self, element, root):
    for child in element:
      if child.tag == "a":
        if child.get("class") is not None:
          m = re.match(r'image_loi_links', child.get("class"))
          if m:
            image_index = None
            image_text = None
            for sub_child in child:
              if sub_child.get("class") is not None:
                mi = re.match(r'image_index', sub_child.get("class"))
                if mi:
                  image_index = sub_child.text

                mt = re.match(r'image_text', sub_child.get("class"))
                if mt:
                  # decode link text and flatten contents
                  # image_text element was only used for duplication for loi
                  sub_child.text = sub_child.get("text")
                  image_text = self.get_link_text_from_image(sub_child)
                  sub_child.text = ""
                  del sub_child.attrib['text']

            if image_index is None:
              raise ImageException("FATAL: LoiRefineLinksTreeProcessor: Could not find not find image_index.")

            if image_text is None:
              raise ImageException("FATAL: LoiRefineLinksTreeProcessor: Could not find image_text.")

            image_id = "image:" + image_index + "_" + image_text + ":"
            image_ref = "loi:" + image_index + "_" + image_text + ":"

            child.set('id', image_id)
            child.set('href', "#" + image_ref)

            self.refine_links_replace_loi(root, image_index, image_ref, image_id)
      self.refine_links_loi(child, root)

  def get_link_text_from_image(self, element):
    # get texts from elements as list => remove all attributes
    link_text = "_".join(self.get_link_texts_from_image(element))
    # replace sequence of spaces/tabs with _
    link_text2 = re.sub(r'(\s+)', r'_', link_text)
    # replace inline statements of the form {<a>:<b>} to <a>_<b> => no formating expected !
    link_text3 = re.sub(r'(\{([^:]+):([^\}]+)\})', r'\2_\3', link_text2)
    return link_text3

  def get_link_texts_from_image(self, element):
    link_texts = []
    if element.text:
      link_texts.append(element.text)

    for child in element:
      if child.text:
        link_texts.append(child.text)
      link_texts += self.get_link_texts_from_image(child)

    return link_texts

  def refine_links_replace_loi(self, element, image_index, image_id, image_ref):
    for child in element:
      if child.tag == "a":
        if child.get("class") is not None:
          m = re.match(r'loi_image_links_index', child.get("class"))
          if m:
            mi = re.match("#" + "image:" + image_index + ":", child.get("href"))
            if mi:
              # replace entry in loi with new href names
              child.set('href', "#" + image_ref)
          m = re.match(r'loi_image_links_text', child.get("class"))
          if m:
            mi = re.match("loi:" + image_index + ":", child.get("id"))
            if mi:
              # replace entry in loi with new id/href names
              child.set('id', image_id)
              child.set('href', "#" + image_ref)

      self.refine_links_replace_loi(child, image_index, image_id, image_ref)

# -------------------------------------------------------------------------------
class ImageExtension(Extension):

  LoiReplaceTreeProcessorClass = LoiReplaceTreeProcessor

  LoiRefineTreeProcessorClass = LoiRefineTreeProcessor

  LoiRefineLinksTreeProcessorClass = LoiRefineLinksTreeProcessor

  def __init__(self, tools, **kwargs):
    self.tools = tools
    self.config = {
      'message_identifier': [
          'IMAGE',
          'Message Identifier',
          'Default: IMAGE`.'
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
      'title': [
        'List of Images',
        'Title for LOI',
        'Default: `List of Images`.'
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

    md.parser.blockprocessors.register(ImageBlockProcessor(self.tools, md.parser, md, self.getConfigs()), 'image_block_processor', 175)

    # prepare loi for replacement
    md.parser.blockprocessors.register(LoiPositionBlockProcessor(md.parser), 'image__loi_position', 175)

    # ------------
    # Treeprocessors

    # generate loi
    loi_replace_ext = self.LoiReplaceTreeProcessorClass(self.tools, md, self.getConfigs())
    md.treeprocessors.register(loi_replace_ext, 'image__loi_replace', 177)

    # refine loi text
    loi_refine_ext = self.LoiRefineTreeProcessorClass(self.tools, md, self.getConfigs())
    md.treeprocessors.register(loi_refine_ext, 'image__loi_refine', 176)

    # refine loi/image links
    loi_refine_links_ext = self.LoiRefineLinksTreeProcessorClass(self.tools, md, self.getConfigs())
    md.treeprocessors.register(loi_refine_links_ext, 'image__loi_refine_links', 175)

    # ------------
    # Inlineprocessors

    # ------------
    # Postprocessors

  def reset(self):
    # global variables to share between processing sequences

    # loi_index_id_list is used to define the current index level
    # the list starts with one entry at 0
    # it gets incremented/extended/reduced according to the current index level
    self.md.loi_index_id_list = []
    self.md.loi_index_id_list.append(0)

    # loi_loi contains the table of contents in the form of list entries (list of lists):
    # [index_id, heading_text]
    #
    self.md.loi_loi = []

    pass

# -------------------------------------------------------------------------------
class ImageException(Exception):
  name = "ImageException"
  message = ""

  def __init__(self, message):
    self.message = message

  def __str__(self):
    if self.message:
      return self.name + ': ' + self.message
    else:
      return self.name + ' has been raised'
