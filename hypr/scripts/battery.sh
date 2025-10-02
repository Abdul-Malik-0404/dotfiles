#!/bin/bash
#["", "", "", "", ""]
capacity=$(cat /sys/class/power_supply/BAT*/capacity)
status=$(cat /sys/class/power_supply/BAT*/status)
icon=""
if (($capacity>=80)); then
    icon=""
elif (($capacity<80)); then
    icon=""
elif (($capacity<60)); then
    icon=""
elif (($capacity<40));then
    icon=""
elif (($capacity<20));then
    icon=""
else
    icon="N/A"
fi

if .config/hypr/scripts/toolbar_state; then
    if [[ "$status" == "Charging" ]]; then
        echo "$icon"
    else
        echo "$icon"
    fi
else
    echo ""
fi
