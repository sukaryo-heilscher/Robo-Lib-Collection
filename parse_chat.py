import pandas as pd
from datetime import datetime
import os

def parse_line(line):
    parts = line.strip().split('] ')
    timestamp_str = parts[0][1:]
    hour, minute, second = map(int, timestamp_str.split(':'))
    timestamp = (hour * 3600 + minute * 60 + second) * 1000  # converting to milliseconds
    timestamp -= timestamp % 10000  # round down to nearest 10s
    commenter_comment = parts[1].split(': ')
    commenter = commenter_comment[0].lower()  # Convert to lowercase
    comment = commenter_comment[1].lower()    # Convert to lowercase
    return timestamp, commenter, comment


def import_chat(file_path):
    date_str = '_'.join(os.path.basename(file_path).split('_')[:3])
    date = datetime.strptime(date_str, '%m_%d_%Y')
    data = {'Timestamp': [], 'Commenters': [], 'Comments': [], 'Date': []}
    line_number = 0
    with open(file_path, 'r', encoding='utf-8') as file:
        try:
            for line in file:
                line_number += 1
                timestamp, commenter, comment = parse_line(line)
                data['Timestamp'].append(timestamp)
                data['Commenters'].append(commenter)
                data['Comments'].append(comment)
                data['Date'].append(date)
        except UnicodeDecodeError as e:
            print(f"UnicodeDecodeError occurred at line {line_number}: {e}")
            raise e

    try:
        df = pd.DataFrame(data)

        # Group and aggregate comments by 10-second intervals
        df = df.groupby(['Date', pd.Grouper(key='Timestamp')]).agg({'Commenters': ' '.join, 'Comments': ' '.join}).reset_index()

    except ValueError as e:
        print(f"ValueError occurred when converting 'Timestamp' column: {e}")
        print("Problematic 'Timestamp' values:")
        print(df[df['Timestamp'].apply(lambda x: not isinstance(x, datetime))]['Timestamp'])

    return df


def mark_clipped(df, clipped_file):
    with open(clipped_file, 'r') as file:
        for line in file:
            start, end = map(int, line.strip().split(' - '))
            start = start - (start % 10000)  # Round down to the nearest 10-second interval
            end = end - (end % 10000)  # Round down to the nearest 10-second interval
            df.loc[(df['Timestamp'] >= start) & (df['Timestamp'] <= end), 'Clipped'] = 1
    df['Clipped'] = df['Clipped'].fillna(0).astype(int)
    return df

def export_to_csv(df, output_file):
    df.to_csv(output_file, index=False)

# Example usage
if __name__ == "__main__":
    file_path = "./chat/04_02_2024_chat.txt"
    clipped_file = "./timestamps/04_02_2024_timestamps.txt"
    output_file = "./final_data/04_02_2024_data.csv"

    df = import_chat(file_path)
    df = mark_clipped(df, clipped_file)
    # export_to_csv(df, output_file)
