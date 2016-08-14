# -*- coding: utf-8 -*-
#
# DebOps documentation build configuration file
# Copyright (C) 2014-2016 DebOps Project http://debops.org/
#
# This file is execfile()d with the current directory set to its
# containing dir.
#
# Note that not all possible configuration values are present in this
# autogenerated file.
#
# All configuration values have a default; values that are commented out
# serve to show the default.

import sys
import os
import fnmatch
import re

#  import git

# Generate documentation on the fly based on Ansible default variables
import yaml2rst

for element in os.listdir('ansible/roles'):
    if os.path.isdir('ansible/roles/' + element):
        yaml2rst.convert_file(
            'ansible/roles/' + element + '/defaults/main.yml',
            'ansible/roles/' + element + '/docs/defaults.rst',
            strip_regex=r'\s*(:?\[{3}|\]{3})\d?$',
            yaml_strip_regex=r'^\s{66,67}#\s\]{3}\d?$',
        )

from subprocess import call, check_output
call(['bin/sphinx_conf_pre_hook'])

on_rtd = os.environ.get('READTHEDOCS', None) == 'True'

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
html_theme = 'default'

if not on_rtd:  # only import and set the theme if we're building docs locally
    import sphinx_rtd_theme
    html_theme = 'sphinx_rtd_theme'
    html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]

# Fix "Edit on GitHub" links (((
# Jinja2 Support is only basic Jinja2 without all the good stuff from Ansible. So I am not gonna mess with that or try to extend it as in:
# https://stackoverflow.com/questions/36019670/removing-the-edit-on-github-link-when-using-read-the-docs-sphinx-with-readthed
# What I am gonna do instead is just recompute source file to URL map in Python and job done.
#
# git_repo.iter_submodules() fails with "unknown encoding: -----BEGIN PGP SIGNATURE-----"


def find_files(directory, pattern):
    for root, dirs, files in os.walk(directory):
        for basename in files:
            if fnmatch.fnmatch(basename, pattern):
                filename = os.path.join(root, basename)
                yield filename


def get_source_file_to_url_map(start_dir='.'):
    skip_page_names = [
        'debops-keyring/docs/entities',  # Auto generated.
    ]

    source_file_to_url_map = {}
    repo_dir_to_url_map = {}
    list_of_submod_paths = []

    cur_dir = os.path.abspath(os.path.dirname(__file__))

    for submodule_path in check_output(['git', 'submodule', '--quiet', 'foreach', 'pwd']).split('\n'):
        if submodule_path.startswith(cur_dir):
            submodule_path = submodule_path[len(cur_dir):].lstrip('/')
        list_of_submod_paths.append(submodule_path)

    for source_file_name in find_files('.', '*.rst'):
        pagename_source_file = source_file_name.lstrip('/.')[:-4]

        if pagename_source_file in skip_page_names:
            continue

        dir_path = os.path.dirname(source_file_name)
        if len(dir_path) > 2:
            dir_path = dir_path.lstrip('/.')

        # Can also contain subdirs in a repo but this optimization should already
        # get factor 10 in performance for git Invokation.
        if dir_path not in repo_dir_to_url_map:
            #  git_repo = git.Repo(dir_path)
            #  repo_dir_to_url_map[dir_path] = git_repo.remotes.origin.url
            for remote_line in check_output(['git', '-C', dir_path, 'remote', '-v']).split('\n'):
                remote_item = re.split(r'\s', remote_line)
                if remote_item[0] == 'origin' and remote_item[2] == '(fetch)':
                    base_url = remote_item[1]
                    if base_url.endswith('.git'):
                        base_url = base_url[:-4]
                    repo_dir_to_url_map[dir_path] = base_url
                    #  print(repo_dir_to_url_map[dir_path])

        relative_pagename = pagename_source_file

        if relative_pagename == 'index':
            relative_pagename = 'docs/' + relative_pagename

        for submod_path in list_of_submod_paths:
            if pagename_source_file.startswith(submod_path + '/'):
                relative_pagename = pagename_source_file[len(submod_path):].lstrip('/')


        #  print('{}: {}'.format(pagename_source_file, repo_dir_to_url_map[dir_path]))
        source_file_to_url_map[pagename_source_file] = {
            'url': repo_dir_to_url_map[dir_path],
            'pagename': relative_pagename,
        }


    #  print(source_file_to_url_map)
    return source_file_to_url_map

html_context = {
    'display_github': True,  # Add 'Edit on Github' link instead of 'View page source'
    'last_updated': True,
    'commit': False,
    'source_file_to_url_map': get_source_file_to_url_map()
}

# https://stackoverflow.com/a/21909382
#  import sphinx.application.TemplateBridge
# )))

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
# sys.path.insert(0, os.path.abspath('.'))

# -- General configuration ------------------------------------------------

suppress_warnings = ['image.nonlocal_uri']

# If your documentation needs a minimal Sphinx version, state it here.
#needs_sphinx = '1.0'

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = []

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# The suffix of source filenames.
source_suffix = '.rst'

# The encoding of source files.
#source_encoding = 'utf-8-sig'

# The master toctree document.
master_doc = 'index'

# General information about the project.
project = u'DebOps'
copyright = u'2014-2016, Maciej Delmanowski, Nick Janetakis, Robin Schneider'

# The version info for the project you're documenting, acts as replacement for
# |version| and |release|, also used in various other places throughout the
# built documents.
#
# The short X.Y version.
version = 'master'
# The full version, including alpha/beta/rc tags.
release = 'master'

# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
#language = None

# There are two options for replacing |today|: either, you set today to some
# non-false value, then it is used:
#today = ''
# Else, today_fmt is used as the format for a strftime call.
#today_fmt = '%B %d, %Y'

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# 'includes/*.rst': https://github.com/debops/docs/issues/144
exclude_patterns = ['_build', 'debops/*.rst', 'debops-playbooks/*.rst', 'ansible/roles/ansible-*/*.rst', 'ansible/roles/ansible-*/docs/parts', '**includes/*.rst', 'debops-api/README.rst', 'debops-api/tests/**.rst', 'debops-policy/README.rst']

# The reST default role (used for this markup: `text`) to use for all
# documents.
#default_role = None

# If true, '()' will be appended to :func: etc. cross-reference text.
#add_function_parentheses = True

# If true, the current module name will be prepended to all description
# unit titles (such as .. function::).
#add_module_names = True

# If true, sectionauthor and moduleauthor directives will be shown in the
# output. They are ignored by default.
#show_authors = False

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'sphinx'

# The default language to highlight source code in. The default is 'python'.
# The value should be a valid Pygments lexer name, see Showing code examples
# for more details.
highlight_language = 'YAML'

## TODO: Change later to this when it can handle:
## enabled: '{{ True if (owncloud_database_name != owncloud_database_user) else False }}'
#  highlight_language = 'YAML+Jinja'

# A list of ignored prefixes for module index sorting.
#modindex_common_prefix = []

# If true, keep warnings as "system message" paragraphs in the built documents.
#keep_warnings = False


# -- Options for HTML output ----------------------------------------------

# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for each theme, see the
# documentation.
#html_theme_options = {}

# Add any paths that contain custom themes here, relative to this directory.
#html_theme_path = []

# The name for this set of Sphinx documents.  If None, it defaults to
# "<project> v<release> documentation".
#html_title = None

# A shorter title for the navigation bar.  Default is the same as html_title.
#html_short_title = None

# The name of an image file (relative to this directory) to place at the top
# of the sidebar.
#html_logo = None

# The name of an image file (within the static path) to use as favicon of the
# docs.  This file should be a Windows icon file (.ico) being 16x16 or 32x32
# pixels large.
#html_favicon = None

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

# Add any extra paths that contain custom files (such as robots.txt or
# .htaccess) here, relative to this directory. These files are copied
# directly to the root of the documentation.
#html_extra_path = []

# If not '', a 'Last updated on:' timestamp is inserted at every page bottom,
# using the given strftime format.
#html_last_updated_fmt = '%b %d, %Y'

# http://www.sphinx-doc.org/en/stable/config.html#confval-html_use_smartypants
# If true, SmartyPants will be used to convert quotes and dashes to
# typographically correct entities.
html_use_smartypants = False
# Disabled because it will render :command:`iptables --list` as `iptables –list`.


# Custom sidebar templates, maps document names to template names.
#html_sidebars = {}

# Additional templates that should be rendered to pages, maps page names to
# template names.
#html_additional_pages = {}

# If false, no module index is generated.
#html_domain_indices = True

# If false, no index is generated.
#html_use_index = True

# If true, the index is split into individual pages for each letter.
#html_split_index = False

# If true, links to the reST sources are added to the pages.
#html_show_sourcelink = True

# If true, "Created using Sphinx" is shown in the HTML footer. Default is True.
#html_show_sphinx = True

# If true, "(C) Copyright ..." is shown in the HTML footer. Default is True.
#html_show_copyright = True

# If true, an OpenSearch description file will be output, and all pages will
# contain a <link> tag referring to it.  The value of this option must be the
# base URL from which the finished HTML is served.
#html_use_opensearch = ''

# This is the file name suffix for HTML files (e.g. ".xhtml").
#html_file_suffix = None

# Output file base name for HTML help builder.
htmlhelp_basename = 'DebOpsdoc'


# -- Options for LaTeX output ---------------------------------------------

latex_elements = {
# The paper size ('letterpaper' or 'a4paper').
#'papersize': 'letterpaper',

# The font size ('10pt', '11pt' or '12pt').
#'pointsize': '10pt',

# Additional stuff for the LaTeX preamble.
#'preamble': '',
}

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title,
#  author, documentclass [howto, manual, or own class]).
latex_documents = [
    (
        'index',
        'DebOps.tex',
        u'DebOps Documentation',
        u'Maciej Delmanowski, Nick Janetakis, Robin Schneider',
        'manual'
    ),
]

# The name of an image file (relative to this directory) to place at the top of
# the title page.
#latex_logo = None

# For "manual" documents, if this is true, then toplevel headings are parts,
# not chapters.
#latex_use_parts = False

# If true, show page references after internal links.
#latex_show_pagerefs = False

# If true, show URL addresses after external links.
#latex_show_urls = False

# Documents to append as an appendix to all manuals.
#latex_appendices = []

# If false, no module index is generated.
#latex_domain_indices = True


# -- Options for manual page output ---------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [
    ('index', 'debops', u'DebOps Documentation',
     [u'Maciej Delmanowski, Nick Janetakis, Robin Schneider'], 1)
]

# If true, show URL addresses after external links.
#man_show_urls = False


# -- Options for Texinfo output -------------------------------------------

# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
#  dir menu entry, description, category)
texinfo_documents = [
    (
        'index',
        'DebOps',
        u'DebOps Documentation',
        u'Maciej Delmanowski, Nick Janetakis, Robin Schneider',
        'DebOps',
        'One line description of project.',
        'Miscellaneous'
    ),
]

# Documents to append as an appendix to all manuals.
#texinfo_appendices = []

# If false, no module index is generated.
#texinfo_domain_indices = True

# How to display URL addresses: 'footnote', 'no', or 'inline'.
#texinfo_show_urls = 'footnote'

# If true, do not generate a @detailmenu in the "Top" node's menu.
#texinfo_no_detailmenu = False
