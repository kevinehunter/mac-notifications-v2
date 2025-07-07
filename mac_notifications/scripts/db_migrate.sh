#!/bin/bash
source venv/bin/activate
python -m mac_notifications.database.migrations upgrade
