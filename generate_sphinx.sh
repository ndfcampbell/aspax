#!/bin/bash

rm docs/source/modules.rst
sphinx-apidoc -o docs/source src/main/python
cd docs
make clean
make html

