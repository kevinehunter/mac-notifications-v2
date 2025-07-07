#!/bin/bash
source venv/bin/activate
python -m mac_notifications.daemon.notification_daemon \
    --db data/notifications.db \
    --log data/logs/daemon.log \
    --pid data/daemon.pid
