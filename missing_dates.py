import os

# Directory containing original audio files
og_audio_dir = "./chat"
# Directory containing timestamp files
timestamp_dir = "./final_data"

# Get the list of original audio files
og_audio_files = os.listdir(og_audio_dir)

# Extract dates from original audio filenames
og_dates = set(filename.split("_chat")[0] for filename in og_audio_files)

# Get the list of timestamp files
timestamp_files = os.listdir(timestamp_dir)

# Extract dates from timestamp filenames
timestamp_dates = set(filename.split("_data")[0] for filename in timestamp_files)

# Find dates in original audio filenames that don't have a corresponding library audio file
missing_dates = sorted(og_dates - timestamp_dates)

# Print the missing dates
print(" ".join(missing_dates))
