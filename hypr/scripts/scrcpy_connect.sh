#!/bin/sh

# Your phone's static IP address
PHONE_IP="100.93.190.223"
ADB_PORT="5555"

# Connect to the device wirelessly
adb connect "$PHONE_IP:$ADB_PORT"

# Check if the connection was successful
if adb devices | grep -q "$PHONE_IP:$ADB_PORT"; then
  # If successful, launch scrcpy in a non-interactive way
  scrcpy --tcpip="$PHONE_IP"
fi

