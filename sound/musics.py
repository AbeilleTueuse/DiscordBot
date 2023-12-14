from collections import UserDict
import os
import random as rd


class Musics(UserDict):
    SOUND_PATH = "sound"

    def __init__(self):
        super().__init__(self._get_sounds())

    def _get_sounds(self):
        return {
            sound_name.split(".")[0]: os.path.join(self.SOUND_PATH, sound_name)
            for sound_name in os.listdir(self.SOUND_PATH)
        }

    def random_choice(self):
        return rd.choice(list(self.values()))
    
    def sound_names(self):
        return self.keys()
    
    def __missing__(self, key):
        return self.random_choice()


if __name__ == "__main__":
    musics = Musics()