import os
import random as rd
import json
import pandas as pd


class Musics:
    SOUND_PATH = os.path.join("sound", "data")
    INFO_PATH = os.path.join(SOUND_PATH, "_sound_info.csv")
    ALLOWED_EXTENSION = (".mp3", ".mp4", ".ogg")

    EXTENSION_COLUMN = "extension"
    WEIGHT_COLUMN = "weight"

    def __init__(self):
        self.sound_info = self._read_csv()

    def _read_csv(self):
        return pd.read_csv(self.INFO_PATH, index_col=[0])
        
    def _save_csv(self):
        self.sound_info.to_csv(self.INFO_PATH)

    def random_choice(self):
        return self.sound_info.sample(n=1, weights=self.WEIGHT_COLUMN).index[0]

    def add(self, filename: str):
        name, columns = self.from_filename(filename)
        self.sound_info.loc[name] = columns
        self._save_csv()

    def remove(self, sound_name: str):
        sound_path = self.get_path(sound_name, strict=True)
        self.sound_info.drop([sound_name], inplace=True)

        if os.path.exists(sound_path):
            os.remove(sound_path)

        self._save_csv()

    def get_names(self):
        return self.sound_info.index.to_list()
    
    def get_probabilities(self):
        weights = self.sound_info[self.WEIGHT_COLUMN]
        total = weights.sum()
        return map(lambda weight: f"{weight} ({weight/total * 100:.2f} %)".replace(".", ","), weights)

    def get_path(self, sound_name: str | None, strict=False):
        if strict:
            return os.path.join(self.SOUND_PATH, f"{sound_name}.{self.sound_info.loc[sound_name, self.EXTENSION_COLUMN]}")
        
        if (sound_name is None) or (sound_name not in self.sound_info.index):
            sound_name = self.random_choice()

        return os.path.join(self.SOUND_PATH, f"{sound_name}.{self.sound_info.loc[sound_name, self.EXTENSION_COLUMN]}")
    
    def change_weight(self, sound_name: str, new_weight: float):
        self.sound_info.loc[sound_name, self.WEIGHT_COLUMN] = new_weight
        self._save_csv()

    def from_filename(self, filename: str, weight = 1):
        name, extension = filename.split(".")
        return name, {self.EXTENSION_COLUMN: extension, self.WEIGHT_COLUMN: weight}
    
    def has_sound(self, filename: str):
        return filename.split(".")[0] in self.sound_info.index


if __name__ == "__main__":
    musics = Musics()
    musics.add("caca.mp4")
    musics.remove("caca")
    print(musics.sound_info)