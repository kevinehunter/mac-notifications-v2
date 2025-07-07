# Documentation Enhancement Task Plan

## Overview
Add comprehensive documentation to all code in the Mac Notifications v2.0 project to improve maintainability, usability, and developer experience.

## Objectives
1. Add detailed docstrings to all modules, classes, and functions
2. Add inline comments for complex logic
3. Ensure complete type hints throughout
4. Generate API documentation
5. Create code examples for each module
6. Add architecture decision records (ADRs)

## Documentation Standards

### Docstring Format (Google Style)
```python
def function_name(param1: str, param2: int) -> dict:
    """Brief description of function purpose.
    
    Longer description explaining the function's behavior,
    any important details, side effects, or considerations.
    
    Args:
        param1: Description of param1, including type info
        param2: Description of param2, what values are valid
        
    Returns:
        Description of return value, including structure
        for complex types like dicts or custom objects
        
    Raises:
        ValueError: When param1 is empty
        ConnectionError: When database is unavailable
        
    Example:
        >>> result = function_name("test", 42)
        >>> print(result['status'])
        'success'
        
    Note:
        Any additional notes about usage, performance,
        or important considerations.
    """
```

## Task Breakdown

### Phase 1: Core Modules Documentation (2 days)

#### Day 1A: Daemon and Database
1. **notification_daemon.py**
   - Module docstring explaining daemon architecture
   - Class docstrings for NotificationDaemon
   - Method docstrings with full parameter documentation
   - Inline comments for AppleScript integration
   - Examples of daemon lifecycle

2. **database/connection.py**
   - Connection pooling explanation
   - Thread safety documentation
   - Error handling patterns
   - Performance considerations

3. **database/models.py**
   - Model field descriptions
   - Validation rules
   - Relationships documentation
   - Migration notes

4. **database/repositories.py**
   - Repository pattern explanation
   - Query optimization notes
   - Transaction handling
   - Caching strategies

#### Day 1B: MCP Server
1. **mcp_server/server.py**
   - MCP protocol explanation
   - Handler registration process
   - Request/response flow
   - Error handling strategies

2. **mcp_server/handlers/*.py**
   - Each handler's purpose
   - Input validation rules
   - Response format specs
   - Integration examples

3. **mcp_server/tools.py**
   - Tool registration process
   - Parameter validation
   - Claude integration notes

### Phase 2: Features Documentation (2 days)

#### Day 2A: Search and Analytics
1. **enhanced_search.py**
   - Natural language parsing algorithm
   - Query syntax documentation
   - Performance optimization notes
   - Search examples for each pattern

2. **analytics.py**
   - Metric calculation methods
   - Visualization generation
   - Performance considerations
   - Dashboard customization

3. **priority_scoring.py**
   - Scoring algorithm explanation
   - Weight factors documentation
   - Customization guide
   - Pattern examples

#### Day 2B: Advanced Features
1. **smart_summaries.py**
   - AI summarization approach
   - Template system
   - Context management
   - Performance tuning

2. **batch_actions.py**
   - Batch processing strategies
   - Transaction management
   - Error recovery
   - Performance limits

3. **grouping.py**
   - Clustering algorithm
   - Similarity metrics
   - Performance optimization
   - Customization options

4. **templates.py**
   - Template syntax
   - Variable interpolation
   - Custom filters
   - Usage examples

### Phase 3: Tests Documentation (1 day)

1. **Test Strategy Documentation**
   - Testing philosophy
   - Coverage goals
   - Mock strategies
   - Fixture documentation

2. **Individual Test Files**
   - Test case purposes
   - Setup/teardown explanation
   - Assertion strategies
   - Performance test notes

### Phase 4: Configuration and Scripts (1 day)

1. **Configuration Files**
   - Each setting explained
   - Environment variables
   - Default values
   - Security considerations

2. **Shell Scripts**
   - Script purpose
   - Parameters/options
   - Error handling
   - Examples

### Phase 5: API Documentation Generation (1 day)

1. **Sphinx Setup**
   - Configure Sphinx for API docs
   - Create custom theme
   - Add examples gallery
   - Generate diagrams

2. **API Reference**
   - Auto-generate from docstrings
   - Add usage examples
   - Create tutorials
   - Build search index

## Specific Documentation Tasks

### 1. Module-Level Documentation Template
```python
"""Module name and primary purpose.

This module handles [specific functionality] for the Mac Notifications system.
It provides [key features/capabilities] and integrates with [other modules].

Architecture Notes:
    - Design decisions made
    - Performance considerations
    - Threading/async behavior
    - External dependencies

Usage:
    Basic usage example showing common patterns
    
    >>> from module import MainClass
    >>> instance = MainClass()
    >>> result = instance.method()

Configuration:
    Environment variables used
    Configuration file options
    Default behaviors

See Also:
    - related_module: Description of relationship
    - another_module: How they work together
"""
```

### 2. Class Documentation Template
```python
class NotificationHandler:
    """Handles processing of macOS notifications.
    
    This class is responsible for capturing, parsing, and storing
    notifications from the macOS notification center. It runs as
    a daemon process and uses AppleScript for notification access.
    
    Attributes:
        db_path (str): Path to SQLite database
        running (bool): Daemon run state
        capture_interval (float): Seconds between capture attempts
        
    Properties:
        notification_count: Total notifications processed
        uptime: Daemon uptime in seconds
        
    Thread Safety:
        This class is thread-safe for read operations.
        Write operations are synchronized using internal locks.
        
    Example:
        >>> handler = NotificationHandler("/path/to/db")
        >>> handler.start()
        >>> # ... daemon runs ...
        >>> handler.stop()
        
    Note:
        Requires Full Disk Access permission in macOS
        System Preferences for AppleScript access.
    """
```

### 3. Function Documentation Template
```python
def parse_natural_language_query(
    query: str,
    context: Optional[Dict[str, Any]] = None,
    strict: bool = False
) -> QueryAST:
    """Parse natural language search query into structured AST.
    
    Converts human-friendly search queries into a structured
    abstract syntax tree (AST) that can be converted to SQL.
    Supports boolean operators, field-specific searches, and
    time-based queries.
    
    Args:
        query: Natural language search query
            Examples: "urgent emails from yesterday"
                     "meeting OR appointment tomorrow"
        context: Optional context for relative time resolution
            Default: {"timezone": "UTC", "now": datetime.now()}
        strict: Whether to raise exceptions on parse errors
            Default: False (returns best-effort parse)
            
    Returns:
        QueryAST object containing:
            - root: Root node of the AST
            - tokens: List of parsed tokens
            - metadata: Parse statistics and warnings
            
    Raises:
        ParseError: When strict=True and query is invalid
        ValueError: When query is empty or None
        
    Example:
        Simple query:
        >>> ast = parse_natural_language_query("emails from John")
        >>> print(ast.to_sql())
        "SELECT * FROM notifications WHERE app LIKE '%mail%' AND body LIKE '%John%'"
        
        Complex query with boolean operators:
        >>> ast = parse_natural_language_query("urgent AND (email OR slack)")
        >>> print(ast.root.node_type)
        'AND'
        
    Performance:
        - Simple queries: < 1ms
        - Complex queries: < 5ms
        - Memory: O(n) where n is query length
        
    See Also:
        - QueryAST: Structure of the returned AST
        - SQLGenerator: Converts AST to SQL
        - SearchOptimizer: Optimizes generated queries
    """
```

### 4. Inline Documentation Standards

```python
def calculate_priority_score(notification: Dict[str, Any]) -> Tuple[float, str, List[str]]:
    """Calculate priority score for a notification."""
    
    # Initialize base score from app-specific weights
    # Financial apps start at 60, social apps at 20
    base_score = APP_WEIGHTS.get(notification['app'], 30)
    
    # Extract text content for analysis
    # Combine all text fields with proper null handling
    text_content = ' '.join([
        notification.get('title', ''),
        notification.get('subtitle', ''),
        notification.get('body', '')
    ]).lower()
    
    # Critical pattern matching with early exit
    # These patterns immediately set CRITICAL priority
    for pattern, score_boost in CRITICAL_PATTERNS:
        if pattern.search(text_content):
            # Found critical pattern - immediate high score
            return (95.0, 'CRITICAL', [f'critical_pattern:{pattern.pattern}'])
    
    # Time-based decay calculation
    # Recent notifications get full score, older ones decay
    # Uses exponential decay with 24-hour half-life
    time_decay = calculate_time_decay(
        notification['delivered_time'],
        half_life_hours=24
    )
    
    # Apply all scoring factors
    # Each factor can add 0-20 points
    factors = []
    
    # ... more complex logic with detailed comments ...
```

### 5. Type Hints Enhancement

```python
from typing import (
    Dict, List, Optional, Union, Tuple, Any,
    Callable, TypeVar, Generic, Protocol, Literal,
    TypedDict, NotRequired, cast
)
from datetime import datetime
from pathlib import Path

# Custom type definitions
NotificationID = int
Priority = Literal['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']
JSONDict = Dict[str, Any]

class NotificationDict(TypedDict):
    """Type definition for notification dictionary."""
    id: NotificationID
    app: str
    title: str
    subtitle: NotRequired[str]
    body: NotRequired[str]
    delivered_time: datetime
    priority: Priority
    priority_score: float

# Generic types
T = TypeVar('T')
HandlerFunc = Callable[[JSONDict], JSONDict]
```

### 6. Code Examples for Each Module

Create `examples/` directory with:
- `daemon_examples.py` - Daemon usage patterns
- `search_examples.py` - Search query examples  
- `analytics_examples.py` - Dashboard generation
- `batch_examples.py` - Bulk operations
- `integration_examples.py` - Full workflows

### 7. Architecture Decision Records (ADRs)

Create `docs/adr/` directory with:
- `001-daemon-architecture.md`
- `002-mcp-protocol-choice.md`
- `003-database-design.md`
- `004-search-algorithm.md`
- `005-priority-scoring.md`

## Implementation Script

```bash
#!/bin/bash
# Start documentation enhancement

# Create documentation structure
mkdir -p mac_notifications/docs/{api,adr,tutorials,examples}
mkdir -p mac_notifications/examples

# Install documentation tools
pip install sphinx sphinx-rtd-theme sphinx-autodoc-typehints

# Initialize Sphinx
cd mac_notifications/docs
sphinx-quickstart --quiet --project="Mac Notifications" \
    --author="Your Name" --release="2.0" --language=en

# Create documentation config
cat > conf.py << 'EOF'
# Sphinx configuration for Mac Notifications

import os
import sys
sys.path.insert(0, os.path.abspath('../src'))

project = 'Mac Notifications'
copyright = '2024'
author = 'Your Name'
release = '2.0.0'

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
    'sphinx.ext.intersphinx',
    'sphinx_autodoc_typehints',
]

templates_path = ['_templates']
exclude_patterns = []

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

# Napoleon settings
napoleon_google_docstring = True
napoleon_numpy_docstring = False
napoleon_include_init_with_doc = True
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = True
napoleon_use_admonition_for_notes = True
napoleon_use_admonition_for_references = False
napoleon_use_ivar = False
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_type_aliases = None
napoleon_attr_annotations = True

# Autodoc settings
autodoc_default_options = {
    'members': True,
    'member-order': 'bysource',
    'special-members': '__init__',
    'undoc-members': True,
    'exclude-members': '__weakref__'
}
EOF
```

## Validation Checklist

### For Each Module:
- [ ] Module docstring with overview
- [ ] All classes have docstrings
- [ ] All methods/functions have docstrings
- [ ] Complex logic has inline comments
- [ ] Type hints are complete
- [ ] Examples provided
- [ ] Performance notes included
- [ ] Cross-references added

### For Each Docstring:
- [ ] Brief one-line summary
- [ ] Detailed description if needed
- [ ] All parameters documented
- [ ] Return value described
- [ ] Exceptions listed
- [ ] At least one example
- [ ] See Also section if applicable

### Quality Metrics:
- [ ] Docstring coverage > 95%
- [ ] Type hint coverage > 90%
- [ ] All public APIs documented
- [ ] Examples run without errors
- [ ] Sphinx builds without warnings

## Timeline

- **Week 1**: Core modules + MCP server
- **Week 2**: Features + Tests  
- **Week 3**: Scripts + Configuration + API docs
- **Week 4**: Review, polish, and generate final documentation

Total: 4 weeks for comprehensive documentation
