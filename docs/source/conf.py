# Configuration file for the Sphinx documentation builder.

# -- Project information

project = 'helyOS Developer Manual'
copyright = '2023, Fraunhofer IVI'
author = 'Fraunhofer IVI'

release = '2.1.0'
version = '2.1.0'

# -- General configuration

extensions = [
    'sphinx.ext.duration',
    'sphinx.ext.doctest',
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.intersphinx',
]

intersphinx_mapping = {
    'python': ('https://docs.python.org/3/', None),
    'sphinx': ('https://www.sphinx-doc.org/en/master/', None),
}
intersphinx_disabled_domains = ['std']

templates_path = ['_templates']

# -- Options for HTML output

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
html_css_files = [
    'custom.css',  # This should match the name and path of your custom CSS file
]
# -- Options for EPUB output
epub_show_urls = 'footnote'


pygments_style = 'sphinx'
