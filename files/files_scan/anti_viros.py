import os
import time
import requests

virus_total_api_scan_url = 'https://www.virustotal.com/vtapi/v2/file/scan'
virus_total_api_report_url = 'https://www.virustotal.com/vtapi/v2/file/report'
virus_toatl_api_key = "b4c5a45455b4313a8416b682941b65fc686bc0e4dc76d7a03bca3734ef26eedb"

def scan_file(file_path):
    print("Scanning: ", file_path)
    response = send_scan_request(file_path)
    is_virus = get_report(scan_id=response['scan_id'])
    if is_virus:
        print("VIRUS DETECTED!!! Filepath: ", file_path)
    else:
        print("{} is not virus".format(file_path))


def send_scan_request(file_path):
    params = {'apikey': virus_toatl_api_key}

    file_content = open(file_path, 'rb')
    filename = os.path.basename(file_path)
    files = {'file': (filename, file_content)}

    response = requests.post(virus_total_api_scan_url, files=files, params=params)
    return response.json()

def get_report(scan_id):
    params = {'apikey': virus_toatl_api_key, 'resource': scan_id}
    response = requests.get(virus_total_api_report_url, params=params)
    if not response:
        raise Exception("Unexpected Error in response")

    if response.status_code == 200:
        result = response.json()
        if result["verbose_msg"] == "Your resource is queued for analysis":
            print("Waiting for file to be analyzed...")
            time.sleep(5)
            get_report(scan_id)
            return False
        else:
            return result["positives"] > 0
    else:
        print("Received unexpected response with status code:", response.status_code)
        return False

def scan_dir(path):
    try:
        items = os.listdir(path)
        if not items:
            print(f"The directory '{path}' is empty.")
            return 
        for item in items:
            item_path = os.path.join(path, item)
            if os.path.isfile(item_path):
                scan_file(item_path)
            elif os.path.isdir(item_path):
                print(f"'{item}' is a directory.")
                scan_dir(item_path)

    except FileNotFoundError:
        print(f"Error: The directory '{path}' does not exist.")
        return 
    except OSError:
        print(f"Error: Could not access the directory '{path}'.")
        return 
    return 
    
def print_files(files):
    if not files:
        print("No files found.")
    else:
        print("Files found:")
        for file in files:
            print(file)

if __name__ == "__main__":
    scan_dir(input("Enter the directory path to scan: "))