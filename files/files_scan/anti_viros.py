import os

def check_dir(path):
    files = []
    try:
        items = os.listdir(path)
        if not items:
            print(f"The directory '{path}' is empty.")
            return files
        for item in items:
            item_path = os.path.join(path, item)
            if os.path.isfile(item_path):
                files.append(item)
            elif os.path.isdir(item_path):
                print(f"'{item}' is a directory.")
                files += check_dir(item_path) 

    except FileNotFoundError:
        print(f"Error: The directory '{path}' does not exist.")
        return files
    except OSError:
        print(f"Error: Could not access the directory '{path}'.")
        return files
    return files
    
def print_files(files):
    if not files:
        print("No files found.")
    else:
        print("Files found:")
        for file in files:
            print(file)

if __name__ == "__main__":
    files = check_dir(input("Enter the directory path to check: "))
    print_files(files)