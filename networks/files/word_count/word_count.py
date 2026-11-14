import sys


def word_count(file_path, N):
    text = read_file(file_path)
    words = {}
    for word in text.split():
        word = word.strip('.,!?;:"()[]{}1234567890').lower()
        if word and word.isalpha():  # Check if the word is not empty and contains only alphabetic characters
            if word in words.keys():
                words[word] += 1
            else:
                words[word] = 1
    return sorted(words.items(), key=lambda x: x[1], reverse=True)[:N]
            

def read_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
        return ""
    except Exception as e:
        print(f"An error occurred while reading the file: {e}")
        return ""


def print_word_count(N_best_word_count_result):
    if N_best_word_count_result is None:
        return
    print("Top words:")
    for word, count in N_best_word_count_result:
        print(f"{word}: {count}")


        
if __name__ == "__main__":
    N_num = 1
    try:
        if len(sys.argv) > 1 and int(sys.argv[1])>0:
            N_num = int(sys.argv[1])
        else:
            N_num = int(input("Enter the number of top words to display (N): "))
    except ValueError:
        print("Invalid value for N. Please provide a valid integer.")
        sys.exit(1)
    path = input("Enter the file path: ")
    result = word_count(path, N_num)
    print_word_count(result[:N_num])