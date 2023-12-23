from unidecode import unidecode


def string_normalisation(string: str, strict = True):
    string = unidecode(string.lower())

    if strict:
        return "".join(char for char in string if char.isalnum())

    return "".join(
        char
        for char in string.replace(" ", "_")
        if char.isalnum() or char in ["_", "-"]
    )