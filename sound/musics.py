from collections import UserDict
import os
import random as rd


class Musics(UserDict):
    SOUND_PATH = os.path.join("sound", "data")
    ALLOWED_EXTENSION = (".mp3", ".mp4", ".ogg")

    def __init__(self):
        super().__init__(self._get_sounds())

    def _get_sounds(self):
        return {
            self.get_name(sound_name): self.create_path(sound_name)
            for sound_name in os.listdir(self.SOUND_PATH)
        }

    def random_choice(self):
        return rd.choice(list(self.values()))
    
    def sound_names(self):
        return self.keys()
    
    def add(self, filename: str):
        self[self.get_name(filename)] = self.create_path(filename)

    def get_name(self, filename: str):
        return filename.split(".")[0]
    
    def create_path(self, filename: str):
        return os.path.join(self.SOUND_PATH, filename) 
    
    def __missing__(self, key):
        return self.random_choice()


if __name__ == "__main__":
    musics = Musics()