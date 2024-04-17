import dict_bible_books
from scripture_classes import Scripture, DownloadManager
from art import logo, instructions

# ------------------------ CONSTANTS ---------------------------------
ENDPOINT = "https://b.jw-cdn.org/apis/pub-media/GETPUBMEDIALINKS"
BIBLE_BOOKS_NUMBER = dict_bible_books.BIBLE_BOOKS_NUMBER_T

# ------------------------ MAIN ---------------------------------

print(logo)
print(instructions)

lines = []
print("Enter a list of scriptures in want to download (or press Enter twice to finish): ")
# Prompt the user to enter lines of input
while True:
    line = input()

    # If the user presses Enter without typing anything, exit the loop
    if not line:
        break

    # Append the entered line to the list
    lines.append(line)

scriptures = [line.strip().capitalize() for line in lines]

print("All scriptures entered. Please wait while we process the downloads.")

# Process each input line
for address in scriptures:

    texto = Scripture(address=address)

    if texto.chapter is False or texto.verses_string is False:
        print(f"{texto.address} is not a valid scripture.")
        continue

    # Getting the json from the API
    params = {
        "output": "json",
        "pub": "nwt",
        "fileformat": "MP3",
        "alllangs": 0,
        "track": texto.chapter,
        "langwritten": "T",
        "txtCMSLang": "T",
    }

    try:
        params["booknum"] = BIBLE_BOOKS_NUMBER[f"{texto.bible_book}"]
    except KeyError:
        print(f"{texto.address} is not a valid scripture.")
        continue

    downloader = DownloadManager(endpoint=ENDPOINT, parameters=params, scripture_object=texto)

    if downloader.json == 1:
        print("Couldn't connect to server. Please check to see if your computer is connected to the internet.")
        input("Program concluded! (Press 'Enter' to close)")
        exit()
    elif downloader.json == 2:
        print(f"Error [{texto.address}]: Invalid scripture.")
        continue

    result = downloader.download_audio()

    if result == 0:
        print(f"{texto.address} (status): in")

    elif result == 1:
        print("Could open the buffer file on folder 'input'. Make sure the folder and the file within it exist.")
        exit()

    elif result == 2:
        print(f"{texto.address} (status): error; the audio for that scripture doesn't exist.")
        continue


input("Program concluded! (Press 'Enter' to close)")
