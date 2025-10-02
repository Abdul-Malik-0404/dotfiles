#!/usr/bin/env python3

import json
import subprocess
import sys
import os

# Define the maximum length for the displayed text, consistent with Waybar config.
MAX_LENGTH = 40

# Define Font Awesome 6 icons for media controls and player types
# Ensure your system has a font that supports these glyphs (e.g., Nerd Fonts)
PLAYER_ICONS = {
    "spotify": "",  # Font Awesome Spotify icon
    "default": "🎜"   # Default music note icon
}

CONTROL_ICONS = {
    "play": "󰐊",      # Font Awesome 6 play
    "pause": "󰏤",     # Font Awesome 6 pause
    "next": "󰒭",      # Font Awesome 6 forward-step
    "previous": "󰒰"   # Font Awesome 6 backward-step
}

def get_player_info_continuous(player_name=None):
    """
    Sets up a continuous stream of player information using playerctl --follow.
    It yields player data as dictionaries whenever an update occurs.
    """
    # Check if playerctl is installed and accessible
    if not os.path.exists("/usr/bin/playerctl"):
        raise FileNotFoundError("playerctl command not found. Please install it (e.g., pacman -S playerctl).")

    # The format string for playerctl metadata.
    # We include 'status' directly to know playback state (Playing, Paused, Stopped).
    playerctl_format_string = '{"title": "{{title}}", "artist": "{{artist}}", "player": "{{playerName}}", "status": "{{status}}"}'

    # Construct the playerctl command to follow metadata changes
    cmd = ["playerctl", "--follow", "metadata", "--format", playerctl_format_string]

    # Add player filtering if specified by command line arguments
    if player_name:
        cmd.insert(1, "--player")
        cmd.insert(2, player_name)

    try:
        # Start the playerctl process.
        # stdout=subprocess.PIPE: Captures the output.
        # text=True: Decodes output as text.
        # bufsize=1: Line-buffered, so we get updates immediately.
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, text=True, bufsize=1)

        # Continuously read lines from playerctl's stdout
        for line in process.stdout:
            try:
                # Attempt to parse each line as a JSON object
                player_data = json.loads(line.strip())
                yield player_data # Yield the parsed data to the main loop
            except json.JSONDecodeError:
                # If a line is not valid JSON, skip it (e.g., empty lines or errors)
                continue
            except BrokenPipeError:
                # This occurs if Waybar terminates the script's stdout pipe,
                # indicating Waybar itself has exited or reloaded.
                break # Exit the loop gracefully

    except FileNotFoundError:
        # Re-raise if playerctl wasn't found during Popen (should be caught by initial check)
        raise
    except Exception as e:
        # Catch any other unexpected errors during subprocess execution
        # print(f"DEBUG: An unexpected error during playerctl Popen: {e}", file=sys.stderr)
        pass # Allow main loop to handle default output or error state

    finally:
        # Ensure the playerctl subprocess is terminated when this script exits
        if 'process' in locals() and process.poll() is None:
            process.terminate()
            process.wait(timeout=1) # Give it a moment to terminate

def format_waybar_output(player_data):
    """
    Formats the player data into a Waybar-compatible JSON dictionary.
    This function generates the raw text and 'alt' field, and also
    includes control icons to be used directly in Waybar's format string.
    """
    # Initialize all potential output fields to empty strings/defaults
    raw_text = ""
    player_name_alt = "" # For Waybar's format-icons (based on player name)
    tooltip_text = ""

    icon_prev_val = ""
    icon_play_pause_val = ""
    icon_next_val = ""

    # Only process player data if it's valid and status is not "stopped"
    # An empty title also indicates no media playing
    if player_data and player_data.get("title") and player_data.get("status", "").lower() != "stopped":
        title = player_data.get("title", "Unknown Title")
        artist = player_data.get("artist", "Unknown Artist")
        player_name = player_data.get("player", "default")
        status = player_data.get("status", "Playing").lower()

        # Construct the raw text part
        if title and artist and artist != "Unknown Artist":
            raw_text = f"{artist} - {title}"
        elif title:
            raw_text = title
        else:
            raw_text = "No track playing" # Fallback, should ideally not be reached with checks above

        # Apply the maximum length
        if len(raw_text) > MAX_LENGTH:
            raw_text = raw_text[:MAX_LENGTH - 3] + "..."

        # Set tooltip text
        tooltip_text = f"{player_name.capitalize()} ({status.capitalize()}): {artist} - {title}"

        # Set alt text for Waybar's format-icons
        player_name_alt = player_name

        # Determine control icons based on playback status
        icon_prev_val = CONTROL_ICONS["previous"]
        icon_play_pause_val = CONTROL_ICONS["pause"] if status == "playing" else CONTROL_ICONS["play"]
        icon_next_val = CONTROL_ICONS["next"]

    # Construct the final JSON object that Waybar expects
    # 'text': The main content to display (media info)
    # 'alt': Used by Waybar's 'format-icons' to pick the player icon (e.g., Spotify icon)
    # 'tooltip': Detailed information shown on hover
    # 'icon_prev', 'icon_play_pause', 'icon_next': Control icons to be directly inserted by Waybar's 'format'
    output_json = {
        "text": raw_text,
        "alt": player_name_alt, # Waybar uses this to pick the player icon from 'format-icons'
        "tooltip": tooltip_text,
        "icon_prev": icon_prev_val,
        "icon_play_pause": icon_play_pause_val,
        "icon_next": icon_next_val
    }

    return output_json

def get_initial_player_status():
    """
    Gets the current status of the active player once, for immediate display
    when the script starts.
    """
    try:
        if not os.path.exists("/usr/bin/playerctl"):
            return None

        # List all active player names
        players_output = subprocess.run(
            ["playerctl", "--list-all"], capture_output=True, text=True, check=True
        )
        player_names = [p.strip() for p in players_output.stdout.splitlines() if p.strip()]

        if not player_names:
            return None

        # Prioritize 'spotify' if active, otherwise choose the first detected player
        chosen_player = "spotify" if "spotify" in player_names else player_names[0]

        # Get metadata for the chosen player
        metadata_cmd = [
            "playerctl",
            "--player", chosen_player,
            "metadata",
            "--format",
            '{"title": "{{title}}", "artist": "{{artist}}", "player": "{{playerName}}", "status": "{{status}}"}'
        ]
        metadata_output = subprocess.run(metadata_cmd, capture_output=True, text=True, check=True)
        return json.loads(metadata_output.stdout.strip())
    except Exception:
        # Handle errors if playerctl commands fail (e.g., no player running)
        return None

if __name__ == "__main__":
    # Handle optional player filter from command line arguments
    filter_player = None
    if len(sys.argv) > 2 and sys.argv[1] == "--player":
        filter_player = sys.argv[2]

    # --- Initial Status Output ---
    # Output the current media status immediately when the script starts.
    initial_status = get_initial_player_status()
    if initial_status:
        print(json.dumps(format_waybar_output(initial_status)), flush=True)
    else:
        # If no player is active initially, output an empty state to hide the module
        print(json.dumps({"text": "", "alt": "", "tooltip": ""}), flush=True)

    # --- Start Continuous Monitoring ---
    try:
        # Loop indefinitely to process new player data as it comes in
        for player_data in get_player_info_continuous(filter_player):
            # Print the formatted JSON output. `flush=True` is crucial for Waybar.
            print(json.dumps(format_waybar_output(player_data)), flush=True)
    except FileNotFoundError:
        # If playerctl was not found, print an error message to Waybar
        print(json.dumps({"text": "playerctl missing", "alt": "Error", "tooltip": "playerctl command not found. Please install it."}), flush=True)
        sys.exit(1) # Exit with an error code
    except Exception as e:
        # Catch any other unexpected errors during the continuous monitoring
        print(json.dumps({"text": "Script Error", "alt": "Error", "tooltip": f"An unexpected error occurred: {e}"}), flush=True)
        sys.exit(1) # Exit with an error code
