import os
import pandas as pd


def concatenate_csv_files(directory, output_file):
    # Get a list of all CSV files in the directory
    csv_files = [file for file in os.listdir(directory) if file.endswith('.csv')]

    # Initialize an empty list to store DataFrames
    dfs = []

    # Read each CSV file and append its DataFrame to the list
    for csv_file in csv_files:
        file_path = os.path.join(directory, csv_file)
        df = pd.read_csv(file_path)
        dfs.append(df)

    # Concatenate all DataFrames into one large DataFrame
    concatenated_df = pd.concat(dfs, ignore_index=True)

    # Export the concatenated DataFrame to a new CSV file
    concatenated_df.to_csv(output_file, index=False)


# Example usage
if __name__ == "__main__":
    directory = "./final_data"
    output_file = "./final_chat_data.csv"

    concatenate_csv_files(directory, output_file)
