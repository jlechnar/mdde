from markdown.inlinepatterns import InlineProcessor
from markdown.preprocessors import Preprocessor
from markdown.blockprocessors import BlockProcessor
from markdown.treeprocessors import Treeprocessor
from markdown.extensions import Extension
import xml.etree.ElementTree as etree
import re
import copy

# Description: MarkDown Documentation Extensions [MDDE] - 
# Author:      jlechnar
# Licence:     MIT Licence 
# Source:      https://github.com/jlechnar/mdde

# -------------------------------------------------------------------------------
#
# include markdown files and extend headings to common format: #(\d+) <name>
#
# Include markdown files at certain level:
# new command: #include[<+level|level>]{<filepath_and_name_with_extension>}
# new command: #include{<filepath_and_name_with_extension>}
#
# Add headings of arbitrary depth (including sub-hierachies):
# new command: #(\d+) <name>
# normal headings are supported with #, ##, ###, ...
# all headings are converted to the new common format:
#   #(\d+) <index-id> <name>
# where <index-id> is generated from the corresponding levels:
#   e.g.: 1.2.3.
#
class IncludePre(Preprocessor):
    RE_INCLUDE_PLUS   = r'^\s*#\s*include\[\+(\d+)\]\{([^\}]+)\}\s*$'
    RE_INCLUDE_DIRECT = r'^\s*#\s*include\[(\d+)\]\{([^\}]+)\}\s*$'
    RE_INCLUDE_FLAT   = r'^\s*#\s*include\{([^\}]+)\}\s*$'
    RE_HEADING = r'^\s*#\s*(\d+)(\s+.+)$'
    RE_HEADING_FLAT = r'^\s*(#+)(\s+[^\d].*$)'

    def __init__(self, tools, md, config):
        super().__init__(md)
        self.tools = tools
        self.config = config

    def read_include(self, level, filename):
        lines = []

        if self.config["debug"]:
            self.tools.debug(' ' * int(level) + "INCLUDE: " + filename)

        with open(filename, 'r', encoding='UTF-8') as file:
            while line := file.readline():
                line.rstrip()
                lines.append(line)
        return self.run_with_level(level, lines)

    def run_with_level(self, level, lines):
        new_lines = []

        level_actual = level

        # -----------------------------
        # for all lines in file search for headings and includes
        for line in lines:

            # ----------------------
            # just replace "# <title>", "## <title>", "### <title>", ... to common format "#\d+ <title>"

            m = re.search(self.RE_HEADING_FLAT, line)

            if m:
                line = re.sub('(^\s*(#+))', "#" + str(len(m.group(1))), line)

            # ----------------------
            # set level according to include level

            m = re.search(self.RE_HEADING, line)

            if m:
                level_actual = int(m.group(1)) + int(level)

                if len(self.md.toc_index_id_list) > level_actual:
                    while len(self.md.toc_index_id_list) > level_actual:
                        self.md.toc_index_id_list.pop()
                    self.md.toc_index_id_list[-1] += 1

                elif len(self.md.toc_index_id_list) == level_actual:
                    self.md.toc_index_id_list[-1] += 1

                else: # len(self.md.toc_index_id_list) < level_actual:
                    while len(self.md.toc_index_id_list) < level_actual:
                        self.md.toc_index_id_list.append(1)

                # merge current toc_index_id_list to index_id string e.g. [1, 3, 4] => "1.3.4."
                index_id = ""
                for i in range(len(self.md.toc_index_id_list)):
                    index_id += str(self.md.toc_index_id_list[i]) + "."

                line = "#" + str(level_actual) + " " + index_id + m.group(2)

                if self.config["debug"]:
                    self.tools.debug(' ' * int(level_actual) + "HEADING: " + index_id + m.group(2))

                # [index_id, heading text]
                self.md.toc_toc.append([index_id, " " * level_actual + m.group(2)])

            # ----------------------
            # handle includes recursively
            mp = re.search(self.RE_INCLUDE_PLUS, line)
            md = re.search(self.RE_INCLUDE_DIRECT, line)
            mf = re.search(self.RE_INCLUDE_FLAT, line)

            if mp:
                level_calculated = level_actual + int(mp.group(1))
                new_lines.append("<!-- " + mp.group(0) + " => include_plus: " + mp.group(2) + " @(actual level +) " + str(level_actual) + " + " + mp.group(1) + " = " + str(level_calculated) + " -->")
                new_lines.extend(self.read_include(level_calculated, mp.group(2)))
                level_actual = level_calculated
                new_lines.append("<!-- " + mp.group(0) + " => include_plus end: " + " @(actual level) " + str(level_actual) + " -->")
            elif md:
                new_lines.append("<!-- " + md.group(0) + " => include_direct: " + md.group(2) + " @(direct level) " + md.group(1) + " -->")
                new_lines.extend(self.read_include(md.group(1), md.group(2)))
                level_actual = md.group(1)
                new_lines.append("<!-- " + md.group(0) + " => include_direct end: " + " @(actual level) " + str(level_actual) + " -->")
            elif mf:
                new_lines.append("<!-- " + mf.group(0) + " => include_flat: " + mf.group(1) + " @(actual level) " + str(level_actual) + " -->")
                new_lines.extend(self.read_include(level_actual, mf.group(1)))
                new_lines.append("<!-- " + mf.group(0) + " => include_flat end: " + " @(actual level) " + str(level_actual) + " -->")
            else:
                new_lines.append(line)

        return new_lines

    def run(self, lines):
      return self.run_with_level(0, lines)

# -------------------------------------------------------------------------------
#
# creates html elements with anchor and refrence to table-of-contents from elements of the form:
#   #(\d+) <index-id> <name>
#
# if level is <= 6 then <h1>-<h6> are used all higher numbers are replaced with <p class="h?"> elements
#
class AdvancedHeadingBlockProcessor(BlockProcessor):
    RE_HEADING_PLUS_INDEX_ID = r'^\s*#\s*(\d+)\s+((([\d\.]+\.)(\s+))([^\n]+))'

    def test(self, parent, block):
        return re.match(self.RE_HEADING_PLUS_INDEX_ID, block)

    def run(self, parent, blocks):

        m = re.search(self.RE_HEADING_PLUS_INDEX_ID, blocks[0])

        if m:
            if int(m.group(1)) > 6:
                # <p class="h{\d+}">...</p>
                e = etree.SubElement(parent, 'p')
                e.set('class', 'h' + m.group(1))
            else:
                # <h{\d+}>...</h{\d+}>
                e = etree.SubElement(parent, 'h' + m.group(1))

            # add anchor to/from toc
            # <p ...><a id="anchor_for_link_from_toc" href="link_to_toc">...</a></p>
            # <h...><a id="anchor_for_link_from_toc" href="link_to_toc">...</a></h...>
            a = etree.SubElement(e, 'a')

            heading_id = "heading:" + m.group(4) + ":"
            heading_ref = "toc:" + m.group(4) + ":"

            a.set('id', heading_id)
            a.set('href', "#" + heading_ref)
            a.set('class', 'heading_toc_links')

            # add index
            s1 = etree.SubElement(a, 'span')
            s1.set('class', 'heading_index')
            s1.text = m.group(4)

            # add space between index and text
            s2 = etree.SubElement(a, 'span')
            s2.set('class', 'heading_space')
            s2.text = " "

            # heading text in s2, mark as heading_text class for later replace of surrounding <p>...</> that gets added automatically by the tool !
            s3 = etree.SubElement(a, 'span')
            s3.set('class', 'heading_text')

            # remove parsed heading block
            blocks[0] = re.sub(re.escape(m.group(0)), '', blocks[0])

            # parse heading text if it is more complex
            self.parser.parseBlocks(s3, [m.group(6)])

            return True
        else:
            return False

# -------------------------------------------------------------------------------
#
# Note that contents of <p class="h?"> elements are wrapped by a <p> by the tool.
# This leads to issues in headings being wrapped in html view.
# This gets corrected below by changing the <p> to a <span> element.
#

class AdvancedHeadingCorrectTreeProcessor(Treeprocessor):
    def run(self, root):
        self.remove_p_from_heading_text(root)
        return None

    def remove_p_from_heading_text(self, element):
        for child in element:
            if child.tag == "span":
                if child.get("class") is not None:
                    m = re.match(r'heading_text', child.get("class"))
                    if m:
                        for sub_child in child:
                            if sub_child.tag == "p":
                                sub_child.tag = "span"
            self.remove_p_from_heading_text(child)

# -------------------------------------------------------------------------------
# find location / command to insert TOC and replace command with element to be filled later

class TocPositionBlockProcessor(BlockProcessor):
    RE_TOC = r'^{toc}$'

    def test(self, parent, block):
        return re.match(self.RE_TOC, block)

    def run(self, parent, blocks):

        m = re.search(self.RE_TOC, blocks[0])

        if m:
            d = etree.SubElement(parent, 'div')
            d.set('class', 'toc')

            blocks[0] = re.sub(re.escape(m.group(0)), '', blocks[0])
            return True
        else:
            return False

# ---------------------------------------------------------------
#
# fill toc element with contents and so heading texts and links corresponding headings and ids for links from headings to toc
#
class TocReplaceTreeProcessor(Treeprocessor):

    def __init__(self, md, config):
        super().__init__(md)
        self.config = config

    def run(self, root):
        self.replace_toc(root)
        return None

    def replace_toc(self, element):
        for child in element:
            if child.tag == "div":
                if child.get("class") is not None:
                    m = re.match(r'toc', child.get("class"))
                    if m:
                         etoc_heading = etree.SubElement(child, "p")
                         etoc_heading.set("class", 'toc_heading')
                         etoc_heading.text = self.config["title"]

                         etoc_div = etree.SubElement(child, "div")
                         etoc_table = etree.SubElement(etoc_div, "table")
                         etoc_table.set('class', "toc")
                         for toc in self.md.toc_toc:
                             etoc_row = etree.SubElement(etoc_table, "tr")

                             etoc_data = etree.SubElement(etoc_row, "td")
                             etoc_a = etree.SubElement(etoc_data, "a")
                             # Only one link valid ! skipped below intentionally
                             #etoc_a.set('id', "toc:" + toc[0] + ":")
                             etoc_a.set('href', "#" + "heading:" + toc[0] + ":")
                             etoc_a.set('class', 'toc_heading_links_index')
                             etoc_a.text = toc[0]

                             etoc_data = etree.SubElement(etoc_row, "td")
                             etoc_a = etree.SubElement(etoc_data, "a")
                             etoc_a.set('id', "toc:" + toc[0] + ":")
                             etoc_a.set('href', "#" + "heading:" + toc[0] + ":")
                             etoc_a.set('class', 'toc_heading_links_text')
                             etoc_a.text = toc[1]

            self.replace_toc(child)

# ---------------------------------------------------------------
#
# replace contents/text of toc link with the one of the heading (same decoded structure)
# heading is decoded further after processing - here we duplicate the decoded text to the one used in the toc, which can still be undecoded due to processing structure
#
class TocRefineTreeProcessor(Treeprocessor):

    def __init__(self, md, config):
        super().__init__(md)

    def run(self, root):
        self.refine_toc(root, root)
        return None

    def refine_toc(self, element, root):
        for child in element:
            if child.tag == "a":
                if child.get("class") is not None:
                    m = re.match(r'heading_toc_links', child.get("class"))
                    if m:
                        heading_index = None
                        heading_text_copy = None
                        for sub_child in child:
                            if sub_child.get("class") is not None:
                                mi = re.match(r'heading_index', sub_child.get("class"))
                                if mi:
                                    heading_index = sub_child.text
                                mt = re.match(r'heading_text', sub_child.get("class"))
                                if mt:
                                    # Flatten sourounding span might not be that easy hence keep it
                                    heading_text_copy = copy.deepcopy(sub_child)
                                    # Found no way to remove class attribute
                                    heading_text_copy.set('class', '')

                        if heading_index is None:
                            raise INHTException("FATAL: TocRefineTreeProcessor: Could not find not find heading_index.")

                        if heading_text_copy is None:
                            raise INHTException("FATAL: TocRefineTreeProcessor: Could not find heading_text.")

                        self.refine_replace_toc(root, heading_index, heading_text_copy)

            self.refine_toc(child, root)

    def refine_replace_toc(self, element, heading_index, heading_text_copy):
        for child in element:
            if child.tag == "a":
                if child.get("class") is not None:
                    m = re.match(r'toc_heading_links_text', child.get("class"))
                    if m:
                        mi = re.match("toc:" + heading_index + ":", child.get("id"))
                        if mi:
                            # Replace temporary text with decoded one from heading
                            child.text = ""
                            child.insert(0, heading_text_copy)
            self.refine_replace_toc(child, heading_index, heading_text_copy)

# ---------------------------------------------------------------
#
# refine/replace toc link text with decoded text from heading
# refine link names between toc and headings
# link names then contains the heading inside the link for readable references
# note that before only id's are part of the link name hence links are not human readable
# in case of document changes it is easier if heading is part of the link name
#
class TocRefineLinksTreeProcessor(Treeprocessor):

    def __init__(self, md, config):
        super().__init__(md)

    def run(self, root):
        self.refine_links_toc(root, root)
        return None

    def refine_links_toc(self, element, root):
        for child in element:
            if child.tag == "a":
                if child.get("class") is not None:
                    m = re.match(r'heading_toc_links', child.get("class"))
                    if m:
                        heading_index = None
                        heading_text = None
                        for sub_child in child:
                            if sub_child.get("class") is not None:
                                mi = re.match(r'heading_index', sub_child.get("class"))
                                if mi:
                                    heading_index = sub_child.text
                                mt = re.match(r'heading_text', sub_child.get("class"))
                                if mt:
                                    heading_text = self.get_link_text_from_heading(sub_child)

                        if heading_index is None:
                            raise INHTException("FATAL: TocRefineLinksTreeProcessor: Could not find not find heading_index.")

                        if heading_text is None:
                            raise INHTException("FATAL: TocRefineLinksTreeProcessor: Could not find heading_text.")

                        heading_id = "heading:" + heading_index + "_" + heading_text + ":"
                        heading_ref = "toc:" + heading_index + "_" + heading_text + ":"

                        child.set('id', heading_id)
                        child.set('href', "#" + heading_ref)

                        self.refine_links_replace_toc(root, heading_index, heading_ref, heading_id)
            self.refine_links_toc(child, root)

    def get_link_text_from_heading(self, element):
        # get texts from elements as list => remove all attributes
        link_text = "_".join(self.get_link_texts_from_heading(element))
        # replace sequence of spaces/tabs with _
        link_text2 = re.sub(r'(\s+)', r'_', link_text)
        # replace inline statements of the form {<a>:<b>} to <a>_<b> => no formating expected !
        link_text3 = re.sub(r'(\{([^:]+):([^\}]+)\})', r'\2_\3', link_text2)
        return link_text3

    def get_link_texts_from_heading(self, element):
        link_texts = []
        #if element.text:
        #    link_texts.append(element.text)

        for child in element:
            if child.text:
                link_texts.append(child.text)
            link_texts += self.get_link_texts_from_heading(child)

        return link_texts

    def refine_links_replace_toc(self, element, heading_index, heading_id, heading_ref):
        for child in element:
            if child.tag == "a":
                if child.get("class") is not None:
                    m = re.match(r'toc_heading_links_index', child.get("class"))
                    if m:
                        mi = re.match("#" + "heading:" + heading_index + ":", child.get("href"))
                        if mi:
                            # replace entry in toc with new href names
                            child.set('href', "#" + heading_ref)
                    m = re.match(r'toc_heading_links_text', child.get("class"))
                    if m:
                        mi = re.match("toc:" + heading_index + ":", child.get("id"))
                        if mi:
                            # replace entry in toc with new id/href names
                            child.set('id', heading_id)
                            child.set('href', "#" + heading_ref)


            self.refine_links_replace_toc(child, heading_index, heading_id, heading_ref)

# -------------------------------------------------------------------------------
class INHTExtension(Extension):

    IncludePreClass = IncludePre

    TocReplaceTreeProcessorClass = TocReplaceTreeProcessor

    TocRefineTreeProcessorClass = TocRefineTreeProcessor

    TocRefineLinksTreeProcessorClass = TocRefineLinksTreeProcessor

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
            'title': [
                'Table of Contents',
                'Title for TOC'
                'Default: `Table of Contents`.'
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
        include_ext = self.IncludePreClass(self.tools, md, self.getConfigs())
        md.preprocessors.register(include_ext, 'inht__include', 175)

        # ------------
        # Blockprocessors
        md.parser.blockprocessors.register(AdvancedHeadingBlockProcessor(md.parser), 'inht__advanced_heading', 175)

        # prepare toc for replacement
        md.parser.blockprocessors.register(TocPositionBlockProcessor(md.parser), 'inht__toc_position', 175)

        # ------------
        # Treeprocessors

        # remove obsole p in headings
        md.treeprocessors.register(AdvancedHeadingCorrectTreeProcessor(self), 'inht__advanced_heading_correct', 178)

        # generate toc
        toc_replace_ext = self.TocReplaceTreeProcessorClass(md, self.getConfigs())
        md.treeprocessors.register(toc_replace_ext, 'inht__toc_replace', 177)

        # refine toc text
        toc_refine_ext = self.TocRefineTreeProcessorClass(md, self.getConfigs())
        md.treeprocessors.register(toc_refine_ext, 'inht__toc_refine', 176)

        # refine toc/heading links
        toc_refine_links_ext = self.TocRefineLinksTreeProcessorClass(md, self.getConfigs())
        md.treeprocessors.register(toc_refine_links_ext, 'inht__toc_refine_links', 175)

        # ------------
        # Inlineprocessors

        # ------------
        # Postprocessors

    def reset(self):
        # global variables to share between processing sequences

        # toc_index_id_list is used to define the current index level
        # the list starts with one entry at 0
        # it gets incremented/extended/reduced according to the current index level
        self.md.toc_index_id_list = []
        self.md.toc_index_id_list.append(0)

        # toc_toc contains the table of contents in the form of list entries (list of lists):
        # [index_id, heading_text]
        #
        self.md.toc_toc = []

# -------------------------------------------------------------------------------
class INHTException(Exception):
    name = "INHTException"
    message = ""

    def __init__(self, message):
        self.message = message

    def __str__(self):
        if self.message:
            return self.name + ': ' + self.message
        else:
            return self.name + ' has been raised'
