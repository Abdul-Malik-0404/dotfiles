#!/bin/bash

# Characters to use for load visualization
BARS=(" " "▂" "▃" "▄" "▅" "▆" "▇" "█")

# This function gets CPU stats from /proc/stat
get_cpu_stats() {
    # The first line of /proc/stat contains a summary of all cores.
    # We read the first line and then process the rest for per-core data.
    read -r cpu_stats < /proc/stat

    # Store the relevant values (user, nice, system, idle, iowait, etc.)
    # The first word is "cpu", so we ignore it.
    idle_time_total=$(echo "$cpu_stats" | awk '{print $5 + $6}')
    total_time_total=$(echo "$cpu_stats" | awk '{print $2 + $3 + $4 + $5 + $6 + $7 + $8 + $9 + $10}')

    echo "$idle_time_total" "$total_time_total"
}

# Get the initial stats
read -r idle_time1 total_time1 < <(get_cpu_stats)
# Sleep for a short period to get a second reading
sleep 0.1
read -r idle_time2 total_time2 < <(get_cpu_stats)

# Calculate the difference between the two readings
total_diff=$((total_time2 - total_time1))
idle_diff=$((idle_time2 - idle_time1))

# Prevent division by zero
if [ "$total_diff" -eq 0 ]; then
    usage_percent=0
else
    # Calculate usage percentage (100 - idle_percentage)
    usage_percent=$(( (total_diff - idle_diff) * 100 / total_diff ))
fi

# The script will now output the total CPU usage,
# as per-core data is much more complex and less reliable in a simple script.
if ~/.config/hypr/scripts/toolbar_state; then
    # Map the usage percentage to the bar character
    index=$((usage_percent / 13))
    [[ $index -gt 7 ]] && index=7

    echo "${BARS[$index]} ${usage_percent}%"
else
    echo ""
fi
