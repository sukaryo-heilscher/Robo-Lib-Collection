import argparse
from datetime import datetime
from parse_chat import import_chat, mark_clipped, export_to_csv

# Create argument parser
parser = argparse.ArgumentParser(description='Process chat data and convert into csv.')
parser.add_argument('date', nargs='+', help='Date(s) in MM_DD_YYYY format')

# Parse arguments
args = parser.parse_args()

# Process each date
for date_str in args.date:
    try:
        # Convert date string to datetime object
        date = datetime.strptime(date_str, '%m_%d_%Y')
        print(f"Processing date: {date_str}")

        file_path = f"./chat/{date_str}_chat.txt"
        clipped_file = f"./timestamps/{date_str}_timestamps.txt"
        output_file = f"./final_data/{date_str}_data.csv"

        df = import_chat(file_path)
        df = mark_clipped(df, clipped_file)
        export_to_csv(df, output_file)

    except ValueError:
        print(f"Error: Invalid date format for {date_str}. Please use MM_DD_YYYY format.")
