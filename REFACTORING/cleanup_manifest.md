# Cleanup Manifest - 2025-01-07

## Debug Scripts to Remove
- analyze_captured_logs.py
- analyze_extraction_output.py
- analyze_log_dump.py
- check_db_status.py
- check_max_recid.py
- check_missing_notifications.py
- check_notification_db_path.py
- check_recent_times.py
- check_schema.py
- cleanup_daemons.py
- debug_enhanced_search.py
- demo_analytics.py
- demo_smart_summaries.py
- dump_and_search_logs.py
- extract_iphone_notifications.py
- find_iphone_notification_data.py
- fix_daemon_path.py
- generate_dashboard.py
- generate_test_report.py
- get_current_summaries.py
- get_recent_by_time.py
- get_true_recent.py
- kill_notification_daemons.py
- live_demo_summaries.py
- migrate_add_archive_fields.py
- monitor_continuity.py
- monitor_continuity_broad.py
- monitor_continuity_filtered.py
- monitor_continuity_smart.py
- monitor_iphone_logs.py
- monitor_notification_appearance.py
- quick_grouping_test.py
- quick_search_test.py
- quick_template_test.py
- quick_test_summaries.py
- reload_context.py
- run_debug.sh
- run_enhanced_search_test.py
- search_notification_mechanisms.py
- show_actual_recent.py
- show_claude_config.py
- show_live_formatted.py
- show_summary_examples.py
- show_template_examples.py

## Test Files to Remove
- test_batch_actions.py
- test_batch_actions_simple.py
- test_daemon_import.py
- test_enhanced_search.py
- test_enhanced_search_comprehensive.py
- test_enhanced_search_simple.py
- test_import_fix.py
- test_mcp_templates.py
- test_notification_analytics.py
- test_notification_grouping.py
- test_notification_templates.py
- test_priority_scoring.py
- test_search_sql.py
- test_smart_summaries.py

## Old Capture Files
- notification_capture_20250704_152018.json
- notification_capture_20250704_152111.json
- notification_capture_20250704_152154.json
- notification_capture_20250704_152155.json
- notification_capture_20250704_152159.json
- notification_capture_20250704_152310.json
- notification_capture_20250704_152312.json
- notification_capture_20250704_152324.json
- notification_capture_20250704_152422.json
- notification_capture_20250704_152423.json
- log_dump_30min_20250705_152315.json
- log_dump_30min_20250705_152315_iphone_events.json
- log_dump_30min_20250705_152315_search_results.json
- log_dump_60min_20250705_152215.json
- log_dump_60min_20250705_152215_search_results.json

## Checkpoint Files
- CONTEXT_CHECKPOINT.md
- ENHANCED_SEARCH_UPDATES.md
- FEATURE3_DEBUG_CHECKPOINT.md
- FEATURE7_GROUPING_DESIGN.md
- FEATURE8_BATCH_ACTIONS_DESIGN.md
- FEATURE_PRIORITY_PLAN.md
- IPHONE_CONTINUITY_CHECKPOINT.md
- PROJECT_CHECKPOINT_FEATURES_123_COMPLETE.md
- PROJECT_CHECKPOINT_FEATURES_1_2_COMPLETE.md
- SESSION_CHECKPOINT_FEATURE1_COMPLETE.md
- SESSION_CHECKPOINT_FEATURE2_COMPLETE.md
- SESSION_CHECKPOINT_SORTING_FIXED.md
- SESSION_SUMMARY_FEATURES_1237.md
- WORKING_STATE_SNAPSHOT.md

## Old Daemon Files
- notification_daemon.py
- notification_daemon_iphone_debug.py
- notification_daemon_v2.py
- notification_mcp_server.py
- notification_mcp_server_v2.py
- notification_mcp_server_v2_backup.py

## Shell Scripts to Remove
- clean_start.sh
- commit_feature_1.sh
- create_git_snapshot.sh
- create_snapshot.sh
- fix_and_restart_daemon.sh
- force_cleanup.sh
- kill_daemons.sh
- migrate_to_v2.sh
- restart_daemon.sh
- setup.sh
- start_daemon.sh
- start_daemon.sh.bak
- start_daemon_debug.sh
- start_v2_debug.sh
- stop_daemon.sh
- test_batch_actions.sh
- test_daemon.sh

## Log and PID Files
- daemon.log
- daemon.pid
- notification_daemon.log
- notification_daemon.pid
- notification_iphone_debug.log

## Database Files
- notifications.db.old
- notifications_iphone_debug.db
- notifications_pre_priority.db

## Other Files
- claude_desktop_config.json
- claude_desktop_config_v2.json
- test_imports.py
- priority_scoring_test_results.json
- test_out.txt
- test_prompts.md
- iphone_notification_analysis_summary.txt
- live_critical_notifications.html
- notification_analytics_dashboard.html
- test_notifications.html
- test_notifications.md
