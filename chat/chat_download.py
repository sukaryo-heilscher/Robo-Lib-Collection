import subprocess

# Read IDs and dates from a CSV file
with open('list.csv', 'r') as file:
    for line in file:
        id, month, day = line.strip().split(',')  # Assuming CSV format with ID,Date
        command = f"C:\\Users\\mrcud\\Desktop\\RoboLibrarian\\TwitchDownloaderCLI.exe chatdownload --id {id} -o {month}_{day}_2024_chat.txt"
        subprocess.run(command, shell=True)
        # print(command)