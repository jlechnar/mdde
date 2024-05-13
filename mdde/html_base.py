from markdown.postprocessors import Postprocessor
from markdown.extensions import Extension
import re

class HtmlBasePostprocesor(Postprocessor):

    def __init__(self, md, config):
        super().__init__(md)
        self.config = config

    def run(self, text):
        all  = '<!DOCTYPE html>\n'
        all += '<html lang="en">\n'
        all += '  <head>\n'
        all += '<meta charset="UTF-8">\n'
        all += '    <title>' + self.config["title"] + '</title>\n'
        all += '    <link rel="stylesheet" href="mdde.css">\n'
        all += '  </head>\n'
        all += '  <body>\n'
        all += text + '\n'
        all += '  </body>\n'
        all += '</html>\n'

        return all

class HtmlBaseExtension(Extension):

    HtmlBasePostprocessorClass = HtmlBasePostprocesor

    def __init__(self, tools, **kwargs):
        self.tools = tools
        self.config = {
            'message_identifier': [
                'HTML_BASE',
                'Message Identifier',
                'Default: HTML_BASE`.'
            ],
            'verbose': [
                False,
                'Verbose mode',
                'Default: off`.'
            ],
            'title': [
                'Document Title',
                'Title for Document',
                'Default: `Document Title`.'
            ],
        }
        """ Default configuration options. """

        super().__init__(**kwargs)

    def extendMarkdown(self, md):
        md.registerExtension(self)
        self.md = md

        html_base_ext = self.HtmlBasePostprocessorClass(md, self.getConfigs())
        md.postprocessors.register(html_base_ext, 'html_base', 175)
