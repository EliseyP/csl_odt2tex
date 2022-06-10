#!/bin/bash
xelatex -synctex=1 -interaction=nonstopmode "single.tex" && \
xelatex -synctex=1 -interaction=nonstopmode "single_black.tex"
