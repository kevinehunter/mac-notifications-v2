# Test File Inventory

## Test Files Found

### Real Test Files (to migrate to tests/)
- test_priority_scoring.py - Unit tests for priority scoring feature
- test_notification_templates.py - Unit tests for notification templates
- test_enhanced_search.py - Tests for enhanced search functionality
- test_enhanced_search_comprehensive.py - Comprehensive search tests
- test_enhanced_search_simple.py - Simple search tests
- test_batch_actions.py - Tests for batch operations
- test_batch_actions_simple.py - Simple batch operation tests
- test_smart_summaries.py - Tests for smart summary feature
- test_notification_analytics.py - Tests for analytics feature
- test_notification_grouping.py - Tests for grouping feature
- test_mcp_templates.py - Tests for MCP template functionality

### Debug/Check Scripts (to convert to tests or archive)
- check_db_status.py
- check_recent_times.py
- debug_enhanced_search.py
- test_search_sql.py
- test_daemon_import.py
- test_import_fix.py

### Demo Scripts (to move to examples/)
- demo_analytics.py
- demo_smart_summaries.py
- show_template_examples.py
- quick_test_summaries.py

### Shell Test Scripts (to convert to pytest)
- test_batch_actions.sh
- test_daemon.sh

### Output Files (to delete)
- test_out.txt
- test_notifications.html
- test_notifications.md
- test_prompts.md
- test_results/
- priority_scoring_test_results.json

### Already Migrated
- mac_notifications/tests/unit/test_daemon.py
- mac_notifications/tests/unit/test_features.py
- mac_notifications/test_imports.py (utility script)

## Migration Plan
1. Create pytest configuration
2. Set up test fixtures
3. Migrate real test files to appropriate test directories
4. Convert debug scripts to proper tests
5. Move demo scripts to examples
6. Delete obsolete output files
