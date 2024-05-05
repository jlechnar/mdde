# MarkDown Documentation Extensions [MDDE] - Extensions for creating documentation.
The following sub modules are provided:

* `inht` = [I]nclude other markdown files at selectable level, add [N]umbered [H]eadings of infinite depth and linked [T]able of contents
  Python Markdown extension which enables including other markdown files at selectable levels, adds numbered headings of infinte depth and linked table of contents.
* `html_base`: HTML basic environment wrapper generating 'valid html files' according to [W3C Markup Validation Service](https://validator.w3.org/). It adds an external css style sheet and document title selection.
* `abbreviation`: 
* `artefact`: Defines artefacts. Special html classes are defined for formatting the html output with cascading style sheets (css). Is the main class where below classes are inherited from:
  * `bug`: Defines bugs with links to bug tracker.
  * `issue`: Defines issues with links to issue tracker.
  * `milestone`: Defines milestones.
* `description`: Is used to defines descriptions within list elements. Text headings are defined per list element instead of bullets. Nested descriptions are supported. The user can format the sections using css.
* `image`: Defines images with label texts. Also list of images can be generated with links back and forth.
* `labels_references.py`: Enables to define lables and referenes to these labels. Links are generated for the references. Further, list with links of references and labels can be generated as document index.
* `comments.py`: support for single line comments starting with 
* `codes.py`: provides headings for code sections, list of codes and links back and forth

Furthermore there is a vim folder that shows how to add syntax highlighting for new commands.
See `vim/readme.md` for more details.

## Features
* Files
  * include of files to others
  * define section id level of included file
    * relative to local section id where including is done
    * absolute
* Sections (=heading)
  * individual section id per section header
  * infinite section id depth (subsections of sections)
  * table of contents (toc) with all section id's
    * links from sections to toc
    * links from toc to sections
* images
  * definition
  * list of images (loi)
    * links back and forth
  * click on image to enlarge
  * adds a link to base file if existing for editing
    * base file must be located in parallel to image and named like the image without the image extension
* abbreviations
  * definition of abbreviations
  * list of abbreviations (loa)
* links/references
  * define user defined lables and references to these labels
  * list of links/references
  * works also for section/heading definitions
* artefacts
  * define artefacts
  * artefacts can easily be reused for defining new classes of elements
  * supports list of artefacts generation (loa)
  * can be links (e.g. to issue tracker)
* comments
  * single line comments
* code section
  * titles for code sections
  * list of codes
* description table/list
  * bold items and detailed description
  * provided by normal lists with follow with a bold text followed by a double dot

### TODO
* tables ?
* title
* show other features of markdown
  * lists
  * list of lists
  * quotes
  * html
* external links / direct links
  * list of links
  * links to links
* reformat python code to common format pep8 ?
* inht
  * disable heading id printing for lists (lor, ...)
  * count with symbols for appendix
* more differnt commands for lists => lor => list_of_references
  * add selection of codes via configuration

## Usage
tbw.

### For Documentation

### Test
```
cd tests
./run.sh
```

## Requirements
* python >= 2.7.18 (older version may also work but are not tested)
* markdown >= 3.3.6 (older version may also work but are not tested)
