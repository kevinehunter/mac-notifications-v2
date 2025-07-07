#!/usr/bin/env python3
"""
Generate documentation templates for all modules in the project.
This creates template files that developers can fill in with specific details.
"""

import os
from pathlib import Path
from datetime import datetime

# Documentation templates for different components

DAEMON_TEMPLATE = '''"""
{module_name} - Core daemon functionality for Mac Notifications.

This module implements the background daemon that continuously monitors
macOS notifications using AppleScript. It captures notifications in real-time
and stores them in a SQLite database with priority scoring and metadata.

Architecture:
    The daemon runs as a separate process and uses the following components:
    - AppleScript bridge for accessing macOS Notification Center
    - SQLite database for persistent storage
    - Signal handlers for graceful shutdown
    - Configurable capture intervals
    
    Flow:
    1. Daemon starts and initializes database
    2. Enters capture loop
    3. Every interval, queries notification center via AppleScript
    4. Parses and enriches notifications with priority scores
    5. Stores in database with deduplication
    6. Continues until shutdown signal received

Performance Considerations:
    - AppleScript calls are synchronous and can block
    - Database writes are batched when possible
    - Memory usage is constant regardless of notification count
    - CPU usage is minimal between capture intervals

Configuration:
    Environment Variables:
        MAC_NOTIFICATIONS_DB_PATH: Database file location
        MAC_NOTIFICATIONS_LOG_LEVEL: Logging verbosity
        MAC_NOTIFICATIONS_CAPTURE_INTERVAL: Seconds between captures
        
    Default Values:
        - Database: ./notifications.db
        - Log Level: INFO
        - Capture Interval: 1.0 seconds

Usage:
    Command Line:
        python -m mac_notifications.daemon
        python -m mac_notifications.daemon --db /path/to/db --interval 2.0
        
    Programmatic:
        from mac_notifications.daemon import NotificationDaemon
        
        daemon = NotificationDaemon(db_path="notifications.db")
        daemon.start()  # Runs in current thread
        
    As a Service:
        # Using launchd on macOS
        launchctl load ~/Library/LaunchAgents/com.user.mac-notifications.plist

Thread Safety:
    The daemon is designed to run in a single thread. If you need to
    interact with it from other threads, use the DaemonManager class
    which provides thread-safe control methods.

Security Notes:
    - Requires Full Disk Access permission in System Preferences
    - AppleScript access to Notification Center must be approved
    - Database file should be protected with appropriate permissions

Maintenance:
    - Logs rotate daily by default
    - Database includes automatic vacuum on startup
    - Old notifications can be archived with batch_actions module

See Also:
    - daemon_manager: Thread-safe daemon control
    - database.models: Notification data model
    - features.priority_scoring: Priority calculation logic
"""
'''

MCP_SERVER_TEMPLATE = '''"""
{module_name} - MCP (Model Context Protocol) server implementation.

This module provides the MCP server that enables Claude Desktop to interact
with the Mac Notifications system. It implements a JSON-RPC style protocol
for querying notifications, performing searches, and executing batch operations.

Protocol Overview:
    The MCP server communicates via JSON-RPC 2.0 over stdio. Each request
    contains a method name and parameters, and returns a structured response.
    
    Request Format:
        {{
            "jsonrpc": "2.0",
            "method": "get_recent_notifications",
            "params": {{"limit": 10}},
            "id": 1
        }}
        
    Response Format:
        {{
            "jsonrpc": "2.0",
            "result": {{"notifications": [...]}},
            "id": 1
        }}

Available Methods:
    Query Methods:
        - get_recent_notifications: Fetch recent notifications
        - search_notifications: Natural language search
        - get_notification_by_id: Fetch specific notification
        - get_notification_stats: Summary statistics
        
    Action Methods:
        - mark_as_read: Mark notifications as read
        - archive_notifications: Archive old notifications
        - delete_notifications: Remove notifications
        - update_priority: Change notification priority
        
    Analysis Methods:
        - get_smart_summary: AI-powered summaries
        - get_analytics_dashboard: Generate analytics
        - get_grouped_notifications: Group similar notifications

Error Handling:
    The server implements robust error handling with specific error codes:
    - -32700: Parse error (invalid JSON)
    - -32600: Invalid request
    - -32601: Method not found
    - -32602: Invalid params
    - -32603: Internal error
    - Custom codes for specific errors (see ErrorCodes enum)

Performance:
    - Requests are processed synchronously
    - Database queries are optimized with indexes
    - Large result sets are paginated
    - Caching for frequently accessed data

Integration with Claude:
    The server is configured in Claude Desktop's config file:
    {{
        "mcpServers": {{
            "mac-notifications": {{
                "command": "python",
                "args": ["-m", "mac_notifications.mcp_server"],
                "env": {{"DB_PATH": "/path/to/notifications.db"}}
            }}
        }}
    }}

Security:
    - Input validation on all parameters
    - SQL injection prevention via parameterized queries
    - Rate limiting for expensive operations
    - Audit logging for sensitive actions

Development:
    To add a new method:
    1. Create handler in handlers/ directory
    2. Register in server.py method registry
    3. Add to tools.py for Claude discovery
    4. Update documentation
    5. Add tests

Testing:
    # Test server directly
    echo '{{"method": "get_recent_notifications", "params": {{}}, "id": 1}}' | python -m mac_notifications.mcp_server

See Also:
    - handlers/: Individual method implementations
    - tools.py: Tool definitions for Claude
    - protocol.py: Protocol constants and types
"""
'''

FEATURE_TEMPLATE = '''"""
{module_name} - {feature_description}

This module implements {detailed_feature_description}. It provides
{key_functionality} that can be used both programmatically and through
the MCP server interface.

Overview:
    {high_level_overview}
    
Algorithm/Approach:
    {algorithm_description}
    
    Steps:
    1. {step_1}
    2. {step_2}
    3. {step_3}
    
Performance Characteristics:
    - Time Complexity: {time_complexity}
    - Space Complexity: {space_complexity}
    - Typical Runtime: {runtime_metrics}
    - Memory Usage: {memory_metrics}

Configuration:
    The module can be configured via:
    
    Environment Variables:
        {ENV_VAR_NAME}: {description}
        
    Config Dictionary:
        config = {{
            "{option_1}": {default_value},  # {description}
            "{option_2}": {default_value},  # {description}
        }}

Usage Examples:
    Basic Usage:
        from mac_notifications.features.{module_name} import {MainClass}
        
        instance = {MainClass}()
        result = instance.{main_method}({example_params})
        
    Advanced Usage:
        # With configuration
        config = {{"option": "value"}}
        instance = {MainClass}(config=config)
        
        # Batch processing
        results = instance.{batch_method}(items)
        
    Integration with MCP:
        # This feature is available via MCP as:
        # Method: {mcp_method_name}
        # Params: {mcp_params}

Customization:
    To extend or customize this feature:
    
    1. Subclass {MainClass}:
        class Custom{MainClass}({MainClass}):
            def {method_to_override}(self, ...):
                # Custom implementation
                
    2. Modify configuration:
        config = {{
            "{custom_option}": value
        }}
        
    3. Register custom handlers:
        instance.register_handler("type", handler_func)

Edge Cases:
    - {edge_case_1}: {how_handled}
    - {edge_case_2}: {how_handled}
    - {edge_case_3}: {how_handled}

Limitations:
    - {limitation_1}
    - {limitation_2}
    
Future Improvements:
    - {improvement_1}
    - {improvement_2}

Dependencies:
    - Internal: {internal_deps}
    - External: {external_deps}
    
Testing:
    Run tests with:
        pytest tests/unit/test_{module_name}.py
        
    Key test cases:
    - {test_case_1}
    - {test_case_2}
    - {test_case_3}

See Also:
    - {related_module_1}: {relationship}
    - {related_module_2}: {relationship}
"""
'''

DATABASE_TEMPLATE = '''"""
{module_name} - Database {component_type} for Mac Notifications.

This module provides {component_description} for the notification storage
system. It implements {key_patterns} to ensure {benefits}.

Database Schema:
    {schema_description}
    
    Key Tables:
        notifications:
            - id: INTEGER PRIMARY KEY
            - app: TEXT (application identifier)
            - title: TEXT
            - body: TEXT
            - delivered_time: TIMESTAMP
            - priority: TEXT
            - priority_score: REAL
            - is_read: INTEGER (0/1)
            - is_archived: INTEGER (0/1)
            
        {other_tables}

Design Patterns:
    {pattern_name}:
        {pattern_description}
        
        Benefits:
        - {benefit_1}
        - {benefit_2}
        
        Example:
            {code_example}

Connection Management:
    {connection_strategy}
    
    - Connection pooling: {pooling_details}
    - Thread safety: {thread_safety_details}
    - Transaction handling: {transaction_details}

Query Optimization:
    Indexes:
        - {index_1}: {purpose}
        - {index_2}: {purpose}
        
    Query Patterns:
        - {pattern_1}: {optimization}
        - {pattern_2}: {optimization}

Error Handling:
    Common Errors:
        - {error_1}: {handling_strategy}
        - {error_2}: {handling_strategy}
        
    Recovery Strategies:
        - {strategy_1}
        - {strategy_2}

Migration Support:
    {migration_approach}
    
    Version Management:
        - Current version: {version}
        - Migration files: {location}
        - Rollback support: {rollback_details}

Performance Tuning:
    - {tuning_tip_1}
    - {tuning_tip_2}
    - {tuning_tip_3}

Usage:
    Basic Connection:
        from mac_notifications.database import get_connection
        
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM notifications")
            
    Repository Pattern:
        from mac_notifications.database.repositories import NotificationRepository
        
        repo = NotificationRepository()
        recent = repo.get_recent(limit=10)
        
    Transactions:
        with get_connection() as conn:
            with conn.transaction():
                # Multiple operations
                repo.update(...)
                repo.insert(...)
                # Automatically committed or rolled back

Testing:
    - Uses in-memory SQLite for tests
    - Fixtures provide test data
    - Migration tests ensure compatibility

See Also:
    - models.py: Data model definitions
    - migrations/: Database migration scripts
    - connection.py: Connection management
"""
'''

TEST_TEMPLATE = '''"""
{test_module_name} - Tests for {module_under_test}.

This test module provides comprehensive testing for {module_description}.
It includes unit tests, integration tests, and performance benchmarks to
ensure {quality_goals}.

Test Strategy:
    {overall_test_strategy}
    
    Coverage Goals:
        - Line Coverage: >90%
        - Branch Coverage: >85%
        - Edge Cases: All identified cases
        - Error Paths: All error conditions

Test Categories:
    1. Unit Tests:
        - Test individual functions/methods
        - Mock external dependencies
        - Fast execution (<100ms per test)
        
    2. Integration Tests:
        - Test component interactions
        - Use real database (in-memory)
        - Moderate execution (<1s per test)
        
    3. Performance Tests:
        - Benchmark critical operations
        - Track performance regressions
        - Set performance budgets

Fixtures:
    {fixture_name}:
        {fixture_description}
        
        Usage:
            def test_something({fixture_name}):
                # Fixture automatically provided
                
    Common Fixtures:
        - {fixture_1}: {purpose}
        - {fixture_2}: {purpose}
        - {fixture_3}: {purpose}

Test Patterns:
    Parametrized Tests:
        @pytest.mark.parametrize("input,expected", [
            (input_1, expected_1),
            (input_2, expected_2),
        ])
        def test_multiple_cases(input, expected):
            assert function(input) == expected
            
    Async Tests:
        @pytest.mark.asyncio
        async def test_async_operation():
            result = await async_function()
            assert result == expected
            
    Property-Based Tests:
        @hypothesis.given(st.text())
        def test_property(text):
            # Test invariants hold for all inputs
            result = function(text)
            assert invariant(result)

Mock Strategies:
    External Services:
        @patch('module.external_service')
        def test_with_mock(mock_service):
            mock_service.return_value = Mock(status=200)
            
    Time-Dependent Tests:
        @freeze_time("2024-01-01 12:00:00")
        def test_time_sensitive():
            # Time is frozen for consistent tests

Edge Cases:
    - {edge_case_1}: {test_approach}
    - {edge_case_2}: {test_approach}
    - {edge_case_3}: {test_approach}

Performance Benchmarks:
    def test_performance_benchmark(benchmark):
        result = benchmark(function_to_benchmark, arg1, arg2)
        assert benchmark.stats['mean'] < 0.1  # 100ms budget

Running Tests:
    # Run all tests
    pytest tests/unit/test_{module_name}.py
    
    # Run specific test
    pytest tests/unit/test_{module_name}.py::TestClass::test_method
    
    # Run with coverage
    pytest --cov={module_name} tests/unit/test_{module_name}.py
    
    # Run with markers
    pytest -m "not slow" tests/

Test Data:
    Location: tests/fixtures/{module_name}/
    Format: {data_format}
    Generation: {how_to_generate}

Debugging Tests:
    # Run with debugging
    pytest -vv --pdb tests/unit/test_{module_name}.py
    
    # Show print statements
    pytest -s tests/unit/test_{module_name}.py
    
    # Profile test execution
    pytest --profile tests/unit/test_{module_name}.py

CI/CD Integration:
    - Tests run on every commit
    - Coverage reports uploaded to codecov
    - Performance tracked over time
    - Failures block deployment

See Also:
    - conftest.py: Shared fixtures
    - test_integration.py: Integration tests
    - benchmarks/: Performance benchmarks
"""
'''

def generate_doc_enhancement_script():
    """Generate the main documentation enhancement script."""
    
    script_content = '''#!/bin/bash
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
'''
    
    return script_content

def main():
    """Generate all documentation templates and scripts."""
    
    base_path = Path("/Users/khunter/claude/mac_notifications_clean/refactored")
    
    # Create documentation task plan
    print("Documentation Enhancement Task Plan created at:")
    print("  REFACTORING/DOCUMENTATION_ENHANCEMENT_TASK.md")
    
    # Create enhancement script
    enhance_script = base_path / "enhance_documentation.py"
    print(f"\nDocumentation enhancement script created at:")
    print(f"  {enhance_script}")
    
    # Create implementation script
    impl_script = base_path / "implement_documentation.sh"
    with open(impl_script, 'w') as f:
        f.write(generate_doc_enhancement_script())
    
    print(f"\nImplementation script created at:")
    print(f"  {impl_script}")
    
    print("\nTo start documentation enhancement:")
    print(f"  chmod +x {impl_script}")
    print(f"  ./{impl_script.name}")
    
    print("\nThis will:")
    print("  1. Install documentation tools")
    print("  2. Set up Sphinx documentation")
    print("  3. Create documentation structure")
    print("  4. Generate API documentation")
    print("  5. Create example templates")
    print("  6. Build initial documentation")

if __name__ == "__main__":
    main()
