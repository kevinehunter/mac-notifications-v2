#!/bin/bash
# Documentation Enhancement Implementation Script

echo "Starting Documentation Enhancement for Mac Notifications v2.0"
echo "============================================================"

PROJECT_ROOT="/Users/khunter/claude/mac_notifications_clean/refactored/mac_notifications"
cd "$PROJECT_ROOT"

# Step 1: Install documentation tools
echo "Installing documentation tools..."
pip install -U sphinx sphinx-rtd-theme sphinx-autodoc-typehints myst-parser

# Step 2: Create documentation structure
echo "Creating documentation structure..."
mkdir -p docs/{_static,_templates,api,guides,tutorials,adr,examples}

# Step 3: Initialize Sphinx
echo "Initializing Sphinx documentation..."
cd docs
sphinx-quickstart -q -p "Mac Notifications" -a "Kevin Hunter" -v "2.0" --ext-autodoc --ext-viewcode --ext-napoleon

# Step 4: Create Sphinx configuration
cat > conf.py << 'EOF'
# Configuration file for the Sphinx documentation builder.

import os
import sys
sys.path.insert(0, os.path.abspath('../src'))

# Project information
project = 'Mac Notifications'
copyright = '2025, Kevin Hunter'
author = 'Kevin Hunter'
release = '2.0.0'

# General configuration
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
    'sphinx.ext.intersphinx',
    'sphinx.ext.todo',
    'sphinx_autodoc_typehints',
    'myst_parser',
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# HTML output
html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
html_theme_options = {
    'navigation_depth': 4,
    'collapse_navigation': False,
    'sticky_navigation': True,
    'includehidden': True,
    'titles_only': False
}

# Napoleon settings for Google-style docstrings
napoleon_google_docstring = True
napoleon_numpy_docstring = False
napoleon_include_init_with_doc = True
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = True
napoleon_use_admonition_for_notes = True
napoleon_use_param = True
napoleon_use_rtype = True

# Autodoc settings
autodoc_default_options = {
    'members': True,
    'member-order': 'bysource',
    'special-members': '__init__',
    'undoc-members': True,
    'exclude-members': '__weakref__',
    'show-inheritance': True,
}

# Type hints
typehints_fully_qualified = False
always_document_param_types = True
typehints_document_rtype = True

# MyST settings for Markdown support
myst_enable_extensions = [
    "deflist",
    "tasklist",
    "html_image",
]

# Intersphinx mapping
intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
    'sqlite3': ('https://docs.python.org/3/library/sqlite3.html', None),
}
EOF

# Step 5: Create main documentation index
cat > index.rst << 'EOF'
Mac Notifications Documentation
===============================

Welcome to the Mac Notifications v2.0 documentation!

.. toctree::
   :maxdepth: 2
   :caption: Getting Started

   guides/quick_start
   guides/installation
   guides/configuration

.. toctree::
   :maxdepth: 2
   :caption: User Guide

   guides/basic_usage
   guides/advanced_features
   guides/claude_integration

.. toctree::
   :maxdepth: 2
   :caption: API Reference

   api/modules
   api/daemon
   api/mcp_server
   api/features
   api/database

.. toctree::
   :maxdepth: 2
   :caption: Developer Guide

   guides/contributing
   guides/architecture
   guides/testing
   guides/deployment

.. toctree::
   :maxdepth: 1
   :caption: Additional Resources

   adr/index
   examples/index
   guides/troubleshooting
   guides/faq

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
EOF

# Step 6: Create API documentation files
echo "Creating API documentation structure..."

# Create module documentation
cat > api/modules.rst << 'EOF'
API Modules Overview
====================

.. toctree::
   :maxdepth: 2

   daemon
   mcp_server
   features
   database
   utils
EOF

# Create daemon documentation
cat > api/daemon.rst << 'EOF'
Daemon Module
=============

.. automodule:: mac_notifications.daemon
   :members:
   :undoc-members:
   :show-inheritance:

notification_daemon
-------------------

.. automodule:: mac_notifications.daemon.notification_daemon
   :members:
   :undoc-members:
   :show-inheritance:

daemon_manager
--------------

.. automodule:: mac_notifications.daemon.daemon_manager
   :members:
   :undoc-members:
   :show-inheritance:
EOF

# Create features documentation
cat > api/features.rst << 'EOF'
Features Module
===============

.. automodule:: mac_notifications.features
   :members:
   :undoc-members:
   :show-inheritance:

priority_scoring
----------------

.. automodule:: mac_notifications.features.priority_scoring
   :members:
   :undoc-members:
   :show-inheritance:

enhanced_search
---------------

.. automodule:: mac_notifications.features.enhanced_search
   :members:
   :undoc-members:
   :show-inheritance:

smart_summaries
---------------

.. automodule:: mac_notifications.features.smart_summaries
   :members:
   :undoc-members:
   :show-inheritance:

analytics
---------

.. automodule:: mac_notifications.features.analytics
   :members:
   :undoc-members:
   :show-inheritance:

batch_actions
-------------

.. automodule:: mac_notifications.features.batch_actions
   :members:
   :undoc-members:
   :show-inheritance:

grouping
--------

.. automodule:: mac_notifications.features.grouping
   :members:
   :undoc-members:
   :show-inheritance:

templates
---------

.. automodule:: mac_notifications.features.templates
   :members:
   :undoc-members:
   :show-inheritance:
EOF

# Step 7: Create example documentation
cat > examples/index.md << 'EOF'
# Code Examples

This section contains practical examples of using the Mac Notifications system.

## Basic Examples

- [Getting Started](basic_usage.md)
- [Daemon Control](daemon_examples.md)
- [Simple Searches](search_examples.md)

## Advanced Examples

- [Complex Queries](advanced_search.md)
- [Batch Operations](batch_examples.md)
- [Custom Analytics](analytics_examples.md)
- [Integration Patterns](integration_examples.md)

## Claude Desktop Examples

- [Basic Claude Usage](claude_basic.md)
- [Advanced Claude Features](claude_advanced.md)
- [Custom Claude Tools](claude_custom.md)
EOF

# Step 8: Create ADR index
cat > adr/index.md << 'EOF'
# Architecture Decision Records

This directory contains Architecture Decision Records (ADRs) for the Mac Notifications project.

## What is an ADR?

An Architecture Decision Record captures an important architectural decision made along with its context and consequences.

## ADR List

1. [ADR-001: Daemon Architecture](001-daemon-architecture.md)
2. [ADR-002: MCP Protocol Choice](002-mcp-protocol.md)
3. [ADR-003: Database Design](003-database-design.md)
4. [ADR-004: Search Algorithm](004-search-algorithm.md)
5. [ADR-005: Priority Scoring System](005-priority-scoring.md)
6. [ADR-006: Testing Strategy](006-testing-strategy.md)
7. [ADR-007: Documentation Standards](007-documentation-standards.md)
EOF

# Step 9: Build documentation
echo "Building HTML documentation..."
cd "$PROJECT_ROOT/docs"
make clean
make html

echo ""
echo "Documentation Enhancement Setup Complete!"
echo "========================================"
echo ""
echo "Next Steps:"
echo "1. Run: python enhance_documentation.py $PROJECT_ROOT"
echo "2. Fill in template placeholders in generated docs"
echo "3. Review and enhance existing docstrings"
echo "4. Generate final documentation: cd docs && make html"
echo "5. View docs at: docs/_build/html/index.html"
echo ""
echo "Documentation Standards Example:"
echo "  $PROJECT_ROOT/examples/documentation_standards.py"
