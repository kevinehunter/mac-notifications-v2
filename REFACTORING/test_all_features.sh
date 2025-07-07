#!/bin/bash
# Complete feature test script for Mac Notifications v2.0

echo "======================================"
echo "Mac Notifications v2.0 Feature Test"
echo "======================================"
echo "Test Date: $(date)"
echo ""

# Color codes for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test result tracking
PASSED=0
FAILED=0
SKIPPED=0

# Function to run a test
run_test() {
    local test_name="$1"
    local test_command="$2"
    local expected_result="${3:-0}"
    
    echo -n "Testing: $test_name... "
    
    if eval "$test_command" > /tmp/test_output.log 2>&1; then
        if [ $? -eq $expected_result ]; then
            echo -e "${GREEN}PASSED${NC}"
            ((PASSED++))
            return 0
        fi
    fi
    
    echo -e "${RED}FAILED${NC}"
    echo "  Error output:"
    tail -5 /tmp/test_output.log | sed 's/^/    /'
    ((FAILED++))
    return 1
}

# Function to check prerequisites
check_prerequisites() {
    echo "Checking prerequisites..."
    
    # Check Python version
    if python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)"; then
        echo "  ✓ Python 3.8+ found"
    else
        echo "  ✗ Python 3.8+ required"
        exit 1
    fi
    
    # Check if virtual environment exists
    if [ -d "venv" ]; then
        echo "  ✓ Virtual environment found"
    else
        echo "  ✗ Virtual environment not found - run ./scripts/install.sh first"
        exit 1
    fi
    
    echo ""
}

# Activate virtual environment
activate_venv() {
    if [ -f "venv/bin/activate" ]; then
        source venv/bin/activate
        echo "Virtual environment activated"
    else
        echo "Failed to activate virtual environment"
        exit 1
    fi
}

# Test daemon operations
test_daemon() {
    echo ""
    echo "=== DAEMON TESTS ==="
    
    # Stop any existing daemon
    ./scripts/stop_daemon.sh > /dev/null 2>&1
    
    run_test "Daemon startup" "./scripts/start_daemon.sh"
    sleep 3
    
    run_test "Daemon status check" "pgrep -f notification_daemon"
    
    run_test "Daemon restart" "./scripts/restart_daemon.sh"
    sleep 3
    
    run_test "Daemon shutdown" "./scripts/stop_daemon.sh"
}

# Test notification capture
test_notification_capture() {
    echo ""
    echo "=== NOTIFICATION CAPTURE TESTS ==="
    
    # Start daemon for tests
    ./scripts/start_daemon.sh > /dev/null 2>&1
    sleep 3
    
    # Create test notification
    osascript -e 'display notification "Test notification" with title "Feature Test"' > /dev/null 2>&1
    sleep 2
    
    # Check if captured
    run_test "Notification capture" "python3 -c \"
import sqlite3
conn = sqlite3.connect('data/notifications.db')
cursor = conn.cursor()
cursor.execute('SELECT COUNT(*) FROM notifications WHERE title = \\'Feature Test\\' AND created_at > datetime(\\'now\\', \\'-1 minute\\')')
count = cursor.fetchone()[0]
exit(0 if count > 0 else 1)
\""
    
    ./scripts/stop_daemon.sh > /dev/null 2>&1
}

# Test priority scoring
test_priority_scoring() {
    echo ""
    echo "=== PRIORITY SCORING TESTS ==="
    
    run_test "Priority scorer import" "python3 -c 'from src.features.priority_scoring import PriorityScorer'"
    
    run_test "Priority calculation" "python3 -c \"
from src.features.priority_scoring import PriorityScorer
scorer = PriorityScorer()
result = scorer.calculate_priority('Mail', 'Urgent: Server down', 'Critical issue', '')
exit(0 if result['priority'] == 'CRITICAL' else 1)
\""
}

# Test enhanced search
test_search() {
    echo ""
    echo "=== SEARCH TESTS ==="
    
    run_test "Search module import" "python3 -c 'from src.features.enhanced_search import EnhancedSearch'"
    
    run_test "Natural language search" "python3 -c \"
from src.features.enhanced_search import EnhancedSearch
search = EnhancedSearch()
# Just test that it doesn't crash
query = 'urgent emails from yesterday'
parsed = search._parse_natural_language(query)
exit(0)
\""
}

# Test batch operations
test_batch_operations() {
    echo ""
    echo "=== BATCH OPERATIONS TESTS ==="
    
    run_test "Batch actions import" "python3 -c 'from src.features.batch_actions import BatchActions'"
    
    run_test "Batch selection validation" "python3 -c \"
from src.features.batch_actions import BatchActions
batch = BatchActions()
# Test dry run doesn't crash
import sqlite3
conn = sqlite3.connect(':memory:')
cursor = conn.cursor()
cursor.execute('CREATE TABLE notifications (id INTEGER PRIMARY KEY)')
result = batch._get_selection_query('app', 'TestApp')
exit(0 if 'WHERE' in result else 1)
\""
}

# Test smart summaries
test_summaries() {
    echo ""
    echo "=== SMART SUMMARIES TESTS ==="
    
    run_test "Smart summaries import" "python3 -c 'from src.features.smart_summaries import SmartSummaries'"
    
    run_test "Summary generation" "python3 -c \"
from src.features.smart_summaries import SmartSummaries
summaries = SmartSummaries()
# Test with empty data
import sqlite3
conn = sqlite3.connect(':memory:')
result = summaries._generate_summary([], 'brief')
exit(0 if 'summary' in result else 1)
\""
}

# Test analytics
test_analytics() {
    echo ""
    echo "=== ANALYTICS TESTS ==="
    
    run_test "Analytics import" "python3 -c 'from src.features.analytics import NotificationAnalytics'"
    
    run_test "Metrics calculation" "python3 -c \"
from src.features.analytics import NotificationAnalytics
analytics = NotificationAnalytics()
# Test with empty database
import sqlite3
conn = sqlite3.connect(':memory:')
cursor = conn.cursor()
cursor.execute('CREATE TABLE notifications (id INTEGER PRIMARY KEY)')
conn.commit()
metrics = analytics.get_notification_metrics(conn, days=7)
exit(0 if 'total_notifications' in metrics else 1)
\""
}

# Test MCP server
test_mcp_server() {
    echo ""
    echo "=== MCP SERVER TESTS ==="
    
    run_test "MCP server import" "python3 -c 'from src.mcp_server.server import NotificationMCPServer'"
    
    run_test "MCP tools registration" "python3 -c \"
from src.mcp_server.tools import get_mcp_tools
tools = get_mcp_tools()
exit(0 if len(tools) > 10 else 1)
\""
}

# Test database operations
test_database() {
    echo ""
    echo "=== DATABASE TESTS ==="
    
    run_test "Database connection" "python3 -c \"
from src.database.connection import DatabaseConnection
db = DatabaseConnection()
conn = db.get_connection()
exit(0 if conn else 1)
\""
    
    run_test "Database migrations" "python3 -c \"
from src.database.migrations import run_migrations
# Just test it doesn't crash
import sqlite3
conn = sqlite3.connect(':memory:')
run_migrations(conn)
exit(0)
\""
}

# Test imports
test_imports() {
    echo ""
    echo "=== IMPORT TESTS ==="
    
    local modules=(
        "src.daemon.notification_daemon"
        "src.mcp_server.server"
        "src.features.priority_scoring"
        "src.features.enhanced_search"
        "src.features.templates"
        "src.features.grouping"
        "src.features.batch_actions"
        "src.features.smart_summaries"
        "src.features.analytics"
        "src.database.connection"
        "src.database.models"
        "src.config.settings"
    )
    
    for module in "${modules[@]}"; do
        run_test "Import $module" "python3 -c 'import $module'"
    done
}

# Main test execution
main() {
    cd "$(dirname "$0")/.."
    
    check_prerequisites
    activate_venv
    
    echo "Starting comprehensive feature tests..."
    echo ""
    
    # Run all test suites
    test_imports
    test_database
    test_daemon
    test_notification_capture
    test_priority_scoring
    test_search
    test_batch_operations
    test_summaries
    test_analytics
    test_mcp_server
    
    # Summary
    echo ""
    echo "======================================"
    echo "TEST SUMMARY"
    echo "======================================"
    echo -e "Passed:  ${GREEN}$PASSED${NC}"
    echo -e "Failed:  ${RED}$FAILED${NC}"
    echo -e "Skipped: ${YELLOW}$SKIPPED${NC}"
    echo ""
    
    if [ $FAILED -eq 0 ]; then
        echo -e "${GREEN}All tests passed!${NC}"
        exit 0
    else
        echo -e "${RED}Some tests failed. Please review the output above.${NC}"
        exit 1
    fi
}

# Run main function
main
