#!/bin/bash

set -e
set -x

# all
make test.odt.jpg
make test.odt.png

# missing base document
cp -f test.odt test2.odt
make test2.odt.jpg
make test2.odt.png
rm -rf test2.odt

# missing image
cp -f test.odt test3.odt

# missing all
# nothing to do
# test4.odt
