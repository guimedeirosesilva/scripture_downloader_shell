import requests
from pydub import AudioSegment

# --------------------- CLASSES ----------------------------------


class Scripture:
    def __init__(self, address):
        self.address = address
        self.bible_book = self.get_bible_book()
        self.chapter = self.get_chapter()
        self.verses_string = self.get_verses_string()
        self.verses_list = self.get_verses_list()

    def get_bible_book(self):
        # find out for each scripture the bible book, chapter and verse
        bible_book = self.address.split(" ")[0]

        # Se for um livro bíblico SEM número na frente
        if len(bible_book) <= 1:
            scripture_sliced = self.address.split(" ")
            bible_book = " ".join((scripture_sliced[0], scripture_sliced[1].capitalize()))

        return bible_book

    def get_chapter(self):
        first_part_address = self.address.split(":")[0]
        try:
            chapter = int(first_part_address.split(" ")[-1])
        except ValueError:
            return False

        return chapter

    def get_verses_string(self):
        try:
            second_part_address = self.address.split(":")[1].replace(" ", "")
        except IndexError:
            return False
        return second_part_address

    def get_verses_list(self):
        if self.verses_string is False:
            return False

        if "," in self.verses_string:
            verses = self.verses_string.split(",")
        else:
            verses = [self.verses_string]
        return verses


class DownloadManager:
    def __init__(self, endpoint, parameters, scripture_object):
        self.endpoint = endpoint
        self.params = parameters
        self.scripture_object = scripture_object
        self.json = self.get_json()

    def get_json(self):
        # Getting the json from the API
        try:
            response = requests.get(self.endpoint, params=self.params)
        except requests.exceptions.RequestException:
            return 1

        try:
            json = response.json()["files"]["T"]["MP3"][0]
        except TypeError:
            return 2

        return json

    def get_milliseconds(self, time):
        dividido = time.split(":")
        hour = int(dividido[0])
        minute = int(dividido[1])
        sec = float(dividido[2])

        sec_total = (hour * 3600) + (minute * 60) + sec
        milliseconds = sec_total * 1000

        return milliseconds

    def download_audio(self):
        response_audio = requests.get(self.json["file"]["url"])

        with open("input/in_audio.mp3", "wb") as f_in_audio:
            f_in_audio.write(response_audio.content)

        # cut audio based on the json file
        try:
            audio_complete = AudioSegment.from_file("input/in_audio.mp3", format="mp3")
        except FileNotFoundError:
            return 1

        output_audio_list = []

        for verse in self.scripture_object.verses_list:
            if "-" in verse:
                verses_list = [int(verse.split("-")[0]), int(verse.split("-")[1])]
            else:
                verses_list = [int(verse), int(verse)]

            try:
                start_milliseconds = self.get_milliseconds(self.json["markers"]["markers"][verses_list[0] - 1]["startTime"])
                end_milliseconds = (self.get_milliseconds(self.json["markers"]["markers"][verses_list[1] - 1]["startTime"]) +
                                    self.get_milliseconds(self.json["markers"]["markers"][verses_list[1] - 1]["duration"]))
            except IndexError:
                return 2

            extract = audio_complete[start_milliseconds:end_milliseconds]
            output_audio_list.append(extract)

        output_audio = output_audio_list[0]
        for audio in output_audio_list[1:]:
            output_audio = output_audio + audio

        output_audio.export(f"output/{self.scripture_object.bible_book}_{self.scripture_object.chapter}.{self.scripture_object.verses_string}.wav", format="wav")

        return 0
