#!/bin/bash

# Get memory usage %
USED=$(free | awk '/Mem:/ {printf("%.0f"), $3/$2 * 100}')

# Print it in Waybar-friendly format
if .config/hypr/scripts/toolbar_state; then
    echo "$USED% "
else
    echo ""
fi
sleep 0.01
