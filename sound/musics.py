import os
import random as rd
import json


class Musics:
    SOUND_PATH = os.path.join("sound", "data")
    INFO_PATH = os.path.join(SOUND_PATH, "info.json")
    ALLOWED_EXTENSION = (".mp3", ".mp4", ".ogg")

    def __init__(self):
        self.sound_files, self.weights = self._get_sounds_data()

    def _open_json(self) -> list:
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
        data = self._open_json()
        data.append(self.info_file(filename))
        self._save_json(data)
        self.__init__()

    def remove(self, sound_name: str):
        data = self._open_json()
        for sound_info in data:
            if sound_info["name"] == sound_name:
                data.remove(sound_info)
                sound_path = self.path(sound_name, strict=True)
                if os.path.exists(sound_path):
                    os.remove(sound_path)
                break
        self._save_json(data)
        self.__init__()

    def names(self):
        return self.sound_files.keys()
    
    def prob(self):
        total = sum(self.weights)
        return map(lambda weight: f"{weight} ({weight/total * 100:.2f} %)".replace(".", ","), self.weights)

    def path(self, sound_name: str | None, strict=False):
        if strict:
            return os.path.join(self.SOUND_PATH, self.sound_files[sound_name])
        
        if (sound_name is None) or (sound_name not in self.sound_files):
            sound_name = self.random_choice()

        return os.path.join(self.SOUND_PATH, self.sound_files[sound_name])
    
    def change_weight(self, sound_name: str, new_weight: float):
        data = self._open_json()
        for index, sound_info in enumerate(data):
            if sound_info["name"] == sound_name:
                self.weights[index] = new_weight
                data[index]["weight"] = new_weight
                self._save_json(data)
                break

    def info_file(self, filename: str, weight = 1):
        name, extension = filename.split(".")
        return {"name": name, "extension": extension, "weight": weight}
                
    def create_info_file(self):
        info = [self.info_file(filename) for filename in os.listdir(self.SOUND_PATH)]
        self._save_json(info)

        print(f"File saved in {self.INFO_PATH}.")


if __name__ == "__main__":
    test = "0,5"
    float(test)
