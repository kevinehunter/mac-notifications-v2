#!/bin/bash
timestamp=$(date +%Y%m%d_%H%M%S)
cp data/notifications.db data/backups/notifications_${timestamp}.db
echo "Database backed up to data/backups/notifications_${timestamp}.db"
