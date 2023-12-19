from unidecode import unidecode

def string_normalisation(string: str):
    string = unidecode(string.lower())
    return "".join(char for char in string if char.isalnum())