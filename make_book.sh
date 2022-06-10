#!/bin/bash
xelatex -synctex=1 -interaction=nonstopmode "book.tex" && \
xelatex -synctex=1 -interaction=nonstopmode "book_black.tex"
