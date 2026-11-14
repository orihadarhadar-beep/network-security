import os
import time
import requests
from tkinter_class import ScannerWindow

virus_total_api_scan_url = 'https://www.virustotal.com/vtapi/v2/file/scan'
virus_total_api_report_url = 'https://www.virustotal.com/vtapi/v2/file/report'
virus_total_api_key = "b4c5a45455b4313a8416b682941b65fc686bc0e4dc76d7a03bca3734ef26eedb"
GUI = ScannerWindow("Antivirus Scanner")
is_virus_detected = False

def scan_file(file_path):
    print("Scanning: ", file_path)
    time.sleep(5)
    response = send_scan_request(file_path)
    is_virus = get_report(scan_id=response['scan_id'])
    if is_virus:
        print("VIRUS DETECTED!!! Filepath: ", file_path)
        global is_virus_detected
        is_virus_detected = True
        GUI.print_msg(f"VIRUS DETECTED!!! Filepath: {file_path}", is_warning=True)
    else:
        print("{} is not virus".format(file_path))


def send_scan_request(file_path):
    params = {'apikey': virus_total_api_key}

    file_content = open(file_path, 'rb')
    filename = os.path.basename(file_path)
    files = {'file': (filename, file_content)}

    response = requests.post(virus_total_api_scan_url, files=files, params=params)
    return response.json()

def get_report(scan_id):
    params = {'apikey': virus_total_api_key, 'resource': scan_id}
    response = requests.get(virus_total_api_report_url, params=params)
    if not response:
        raise Exception("Unexpected Error in response")

    if response.status_code == 200:
        result = response.json()
        if result["verbose_msg"] == "Your resource is queued for analysis":
            print("Waiting for file to be analyzed...")
            time.sleep(20)
            return get_report(scan_id)
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
                time.sleep(5)
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
    
def create_test_virus(path):
    with open(path, "wb") as f:
        f.write(b"X5O!P%@AP[4\\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*")

if __name__ == "__main__":
    path = GUI.get_input("Enter the directory path to scan:")
    create_test_virus(os.path.join(path, "eicar.txt"))
    scan_dir(path)
    if is_virus_detected:
        GUI.print_msg("Scan finished. Virus detected!", is_warning=True)
    else:
        GUI.print_msg("Scan finished. No viruses detected.")
    GUI.root.mainloop()