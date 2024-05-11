import argparse
import time
from datetime import datetime
from pydub import AudioSegment
from identifier import find_chunks, find_matching_indices, create_matching_timestamps, save_timestamps_to_file

# Create argument parser
parser = argparse.ArgumentParser(description='Identify audio chunks and create timestamps.')
parser.add_argument('date', nargs='+', help='Date(s) in MM_DD_YYYY format')

# Parse arguments
args = parser.parse_args()

# Process each date
for date_str in args.date:
    try:
        # Convert date string to datetime object
        date = datetime.strptime(date_str, '%m_%d_%Y')
        print(f"Processing date: {date_str}")

        # Construct file paths
        lib_audio_path = f'./lib_audio/{date_str}_library.mp3'
        og_audio_path = f'./og_audio/{date_str}_stream.mp3'
        timestamps_file_path = f'./timestamps/{date_str}_timestamps.txt'

        # Process the library audio
        start_time = time.time()
        lib_audio = AudioSegment.from_mp3(lib_audio_path)
        lib_indices, lib_chunks = find_chunks(lib_audio)
        end_time = time.time()
        print(f"Total execution time for chunking lib: {end_time - start_time:.2f} seconds.")

        # Process the original audio
        start_time = time.time()
        og_audio = AudioSegment.from_mp3(og_audio_path)
        og_indices, og_chunks = find_chunks(og_audio)
        end_time = time.time()
        print(f"Total execution time for chunking og: {end_time - start_time:.2f} seconds.")

        # Find matching indices between original and library chunks
        start_time = time.time()
        matches = find_matching_indices(og_chunks, lib_chunks)
        end_time = time.time()
        print(f"Total execution time for finding matches: {end_time - start_time:.2f} seconds.")

        # Create timestamps for matching segments and save to file
        start_time = time.time()
        timestamps = create_matching_timestamps(og_indices, matches)
        save_timestamps_to_file(timestamps, timestamps_file_path)
        end_time = time.time()
        print(f"Total execution time for creating timestamps: {end_time - start_time:.2f} seconds.")

    except ValueError:
        print(f"Error: Invalid date format for {date_str}. Please use MM_DD_YYYY format.")
