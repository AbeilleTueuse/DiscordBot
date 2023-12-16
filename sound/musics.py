import os
import random as rd
import json


class Musics:
    SOUND_PATH = os.path.join("sound", "data")
    INFO_PATH = os.path.join(SOUND_PATH, "info.json")
    ALLOWED_EXTENSION = (".mp3", ".mp4", ".ogg")

    def __init__(self):
        self.sound_files, self.weights = self._get_sounds_data()

    def _open_json(self):
        with open(self.INFO_PATH, "r") as file:
            return json.load(file)
        
    def _save_json(self, data: dict):
        with open(self.INFO_PATH, "w") as file:
            json.dump(data, file, indent=4)
    
    def _get_sounds_data(self):
        data = self._open_json()
        weights = []
        sound_files = {}
        for sound_info in data:
            weights.append(float(sound_info["weight"]))
            sound_file = f"{sound_info["name"]}.{sound_info["extension"]}"
            sound_files[sound_info["name"]] = sound_file

        return sound_files, weights

    def random_choice(self):
        return rd.choices(population=list(self.sound_files.keys()), weights=self.weights)[0]

    def add(self, filename: str):
        self.sound_files[filename.split(".")[0]] = filename
        self.weights.append(1)

    def names(self):
        return self.sound_files.keys()
    
    def prob(self):
        total = sum(self.weights)
        return map(lambda weight: f"{weight} ({weight/total * 100:.2f} %)".replace(".", ","), self.weights)

    def path(self, audio_name: str | None):
        if (audio_name is None) or (audio_name not in self.sound_files):
            audio_name = self.random_choice()

        return os.path.join(self.SOUND_PATH, self.sound_files[audio_name])
    
    def change_weight(self, sound_name: str, new_weight: float):
        data = self._open_json()
        for index, sound_info in enumerate(data):
            if sound_info["name"] == sound_name:
                self.weights[index] = new_weight
                data[index]["weight"] = new_weight
                self._save_json(data)
                break
                
    def create_info_file(self):
        info = [
            {
                "name": sound_name.split(".")[0],
                "extension": sound_name.split(".")[-1],
                "weight": "1",
            }
            for sound_name in os.listdir(self.SOUND_PATH)
        ]

        self._save_json(info)

        print(f"File saved in {self.INFO_PATH}.")


if __name__ == "__main__":
    test = "0,5"
    float(test)
