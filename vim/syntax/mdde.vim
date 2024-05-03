runtime! syntax/markdown.vim

syn region mddeIssue     start=+{issue:+          end=+}+ keepend
syn region mddeBug       start=+{bug:+            end=+}+ keepend
syn region mddeArtefact  start=+{artefact:+       end=+}+ keepend
syn region mddeMilestone start=+{milestone:+      end=+}+ keepend
syn region mddeComment   start=+%+                end=+$+ keepend
"syn region mddeLists     start=+{l+      end=+}+ keepend
syn match  mddeLists     display '{toc}'
syn match  mddeLists     display '{loi}'
syn match  mddeLists     display '{lor}'
syn match  mddeLists     display '{loa}'
syn match  mddeLists     display '{loa:issue}'
syn match  mddeLists     display '{loa:artefact}'
syn match  mddeLists     display '{loa:milestone}'
syn match  mddeLists     display '{loa:bug}'
syn region mddeAbbreviation   start=+{a:+      end=+}+ keepend
syn region mddeAbbreviation   start=+{abbr:+      end=+}+ keepend

hi def link mddeComment                   Comment
hi def link mddeArtefact                  mddeArtefact
hi def link mddeBug                       mddeBug
hi def link mddeIssue                     mddeIssue
hi def link mddeMilestone                 mddeMilestone
hi def link mddeAbbreviation              mddeAbbreviation

hi def link mddeLists                     mddeLists


" vim:set sw=2:
