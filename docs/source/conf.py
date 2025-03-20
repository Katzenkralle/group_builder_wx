# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys

sys.path.insert(0, os.path.abspath('../../layout'))
sys.path.insert(0, os.path.abspath('../..'))


# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'Group Builder'
copyright = '2025, Katzenkralle'
author = 'Katzenkralle'
release = '1.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ['myst_parser',
            'sphinx.ext.autodoc',
            'sphinx.ext.todo',
            'sphinx.ext.viewcode',
            'sphinx.ext.napoleon',
            'sphinx.ext.autosummary',
            'sphinx.ext.autodoc.typehints']

templates_path = ['_templates']
exclude_patterns = []

autodoc_default_options = {
    'undoc-members': True,
    'private-members': True,
}

todo_include_todos = True

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'alabaster'
#html_static_path = ['_static']

source_suffix = {
    '.rst': 'restructuredtext',
    '.txt': 'markdown',
    '.md': 'markdown',
}