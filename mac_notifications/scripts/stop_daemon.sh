#!/bin/bash
if [ -f data/daemon.pid ]; then
    pid=$(cat data/daemon.pid)
    kill $pid
    rm data/daemon.pid
    echo "Daemon stopped (PID: $pid)"
else
    echo "No daemon PID file found"
fi
