# Mac Notifications Maintenance Guide

## Overview

This guide provides instructions for maintaining the Mac Notifications system to ensure optimal performance, reliability, and security.

## Regular Maintenance Tasks

### Daily Checks (Automated)
These checks run automatically but should be monitored:

1. **Daemon Health Check**
   - Daemon auto-restarts if crashed
   - Log rotation prevents disk filling
   - Database connections cleaned up

2. **Performance Monitoring**
   - Memory usage stays under threshold
   - CPU usage remains low
   - Database response times normal

### Weekly Tasks

#### 1. Log Review (Mondays)
```bash
# Check daemon logs for errors
tail -n 1000 data/logs/daemon.log | grep -E "ERROR|WARNING"

# Check log sizes
du -h data/logs/*.log

# Archive old logs if needed
./scripts/archive_logs.sh
```

#### 2. Database Optimization (Wednesdays)
```bash
# Run database optimization
sqlite3 data/notifications.db "VACUUM;"
sqlite3 data/notifications.db "ANALYZE;"

# Check database size
du -h data/notifications.db
```

#### 3. Performance Check (Fridays)
```bash
# Run quick performance test
python REFACTORING/performance_benchmark.py --quick

# Check system resource usage
ps aux | grep notification_daemon
```

### Monthly Tasks

#### 1. Database Maintenance (First Monday)
```bash
# Backup database
./scripts/db_backup.sh

# Archive old notifications (> 90 days)
python -c "
from src.features.batch_actions import BatchActions
batch = BatchActions()
batch.archive_notifications('older_than', '90d')
"

# Rebuild indexes
sqlite3 data/notifications.db < scripts/rebuild_indexes.sql
```

#### 2. Security Review (Second Monday)
- Review access logs
- Check for unusual notification patterns
- Verify permissions are correct
- Update dependencies if needed

#### 3. Performance Analysis (Third Monday)
```bash
# Generate monthly analytics
python -c "
from src.features.analytics import NotificationAnalytics
analytics = NotificationAnalytics()
analytics.generate_monthly_report()
"
```

#### 4. Cleanup (Last Monday)
- Remove old backups (keep last 3 months)
- Clean temporary files
- Archive old logs
- Update documentation if needed

### Quarterly Tasks

#### 1. Dependency Updates
```bash
# Check for updates
pip list --outdated

# Update in test environment first
pip install --upgrade -r requirements.txt

# Run full test suite
./scripts/run_tests.sh
```

#### 2. Performance Review
- Analyze long-term trends
- Identify optimization opportunities
- Plan capacity needs
- Review user feedback

#### 3. Security Audit
- Review all dependencies for vulnerabilities
- Check system permissions
- Audit database access patterns
- Update security documentation

## Monitoring

### Key Metrics to Track

1. **System Health**
   - Daemon uptime
   - Memory usage trend
   - CPU usage pattern
   - Disk space usage

2. **Performance Metrics**
   - Average search response time
   - Notifications processed per minute
   - Database query performance
   - Feature usage statistics

3. **Error Rates**
   - Failed notification captures
   - Database errors
   - MCP server errors
   - Search failures

### Monitoring Commands

```bash
# Check daemon status
./scripts/status.sh

# View recent errors
grep ERROR data/logs/daemon.log | tail -20

# Database statistics
sqlite3 data/notifications.db "
SELECT 
    COUNT(*) as total_notifications,
    COUNT(CASE WHEN created_at > datetime('now', '-1 day') THEN 1 END) as last_24h,
    COUNT(CASE WHEN is_read = 0 THEN 1 END) as unread,
    COUNT(CASE WHEN is_archived = 1 THEN 1 END) as archived
FROM notifications;
"
```

## Troubleshooting

### Common Issues

#### 1. High Memory Usage
**Symptoms:** Memory usage > 200MB

**Solutions:**
- Restart daemon: `./scripts/restart_daemon.sh`
- Check for memory leaks in logs
- Archive old notifications
- Optimize database

#### 2. Slow Performance
**Symptoms:** Searches take > 2 seconds

**Solutions:**
- Run database optimization
- Check index health
- Review recent changes
- Profile slow queries

#### 3. Notification Capture Failures
**Symptoms:** Missing notifications

**Solutions:**
- Verify Full Disk Access permission
- Check daemon is running
- Review error logs
- Test with simple notification

### Debug Procedures

#### Enable Debug Logging
```bash
# Set environment variable
export MAC_NOTIFICATIONS_LOG_LEVEL=DEBUG

# Restart daemon
./scripts/restart_daemon.sh

# Watch logs
tail -f data/logs/daemon.log
```

#### Database Integrity Check
```bash
sqlite3 data/notifications.db "PRAGMA integrity_check;"
sqlite3 data/notifications.db "PRAGMA foreign_key_check;"
```

#### Performance Profiling
```python
# Run with profiling
python -m cProfile -o profile.stats src/daemon/notification_daemon.py

# Analyze results
python -m pstats profile.stats
```

## Backup and Recovery

### Backup Strategy

1. **Automated Daily Backups**
   - Database backed up nightly
   - Keep 7 daily backups
   - Keep 4 weekly backups
   - Keep 3 monthly backups

2. **Backup Verification**
   ```bash
   # Verify backup integrity
   ./scripts/verify_backup.sh [backup_file]
   ```

3. **Off-site Backup**
   - Consider cloud storage for critical data
   - Encrypt sensitive backups
   - Test restoration quarterly

### Recovery Procedures

#### Database Recovery
```bash
# Stop daemon
./scripts/stop_daemon.sh

# Restore from backup
./scripts/restore_backup.sh [backup_file]

# Verify data integrity
sqlite3 data/notifications.db "PRAGMA integrity_check;"

# Restart daemon
./scripts/start_daemon.sh
```

#### Full System Recovery
1. Restore from git repository
2. Run installation script
3. Restore database from backup
4. Restore configuration files
5. Verify all features working

## Capacity Planning

### Storage Requirements
- Database: ~1MB per 1,000 notifications
- Logs: ~10MB per week (with rotation)
- Backups: ~3x database size

### Performance Scaling
| Notifications | RAM | CPU | Response Time |
|---------------|-----|-----|---------------|
| < 10,000 | 100MB | < 1% | < 50ms |
| < 50,000 | 150MB | < 2% | < 100ms |
| < 100,000 | 200MB | < 3% | < 200ms |
| > 100,000 | Consider archiving old data |

## Update Procedures

### Minor Updates (2.0.x)
```bash
# Backup first
./scripts/backup_production.sh

# Pull updates
git pull origin main

# Install updates
./scripts/install.sh --update

# Restart daemon
./scripts/restart_daemon.sh

# Verify functionality
./scripts/run_tests.sh --quick
```

### Major Updates (2.x)
1. Read migration guide
2. Backup entire system
3. Test in development environment
4. Schedule maintenance window
5. Execute migration scripts
6. Verify all features
7. Monitor for issues

## Support Resources

### Documentation
- User Guide: `docs/user_guide.md`
- API Reference: `docs/api_reference.md`
- Troubleshooting: `docs/troubleshooting.md`

### Getting Help
1. Check documentation first
2. Review recent logs
3. Search issue tracker
4. Contact support channels

### Reporting Issues
Include:
- System version (`python -m mac_notifications --version`)
- macOS version
- Error messages
- Steps to reproduce
- Recent changes

## Maintenance Log Template

```markdown
## Maintenance Log Entry

**Date:** [Date]
**Type:** [Weekly/Monthly/Emergency]
**Performed by:** [Name]

### Tasks Completed
- [ ] Task 1
- [ ] Task 2

### Issues Found
- None / Description

### Actions Taken
- Description of actions

### Next Steps
- Any follow-up needed

**Time Spent:** [Duration]
```

## Emergency Procedures

### Daemon Crash Loop
```bash
# Force stop
pkill -9 -f notification_daemon

# Clear PID file
rm -f data/daemon.pid

# Clear any locks
rm -f data/*.lock

# Start fresh
./scripts/start_daemon.sh
```

### Database Corruption
```bash
# Attempt repair
sqlite3 data/notifications.db ".recover" > recovered.sql
sqlite3 data/notifications_new.db < recovered.sql

# If repair fails, restore from backup
./scripts/restore_backup.sh --latest
```

### Complete System Failure
1. Check system logs: `Console.app`
2. Verify Python installation
3. Check disk space
4. Restore from backup
5. Reinstall if necessary

## Best Practices

1. **Always backup before changes**
2. **Test updates in development first**
3. **Monitor after any changes**
4. **Document all maintenance activities**
5. **Keep dependencies updated**
6. **Review logs regularly**
7. **Maintain good communication**

---

**Remember:** Preventive maintenance is better than emergency fixes. Regular small tasks prevent major issues.
