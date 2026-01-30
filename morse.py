# Morse táblázat (magyar karakterekkel)
morse_dict = {
    "A": ".-", "Á": ".-.-", "B": "-...", "C": "-.-.", "D": "-..",
    "E": ".", "É": "..-..", "F": "..-.", "G": "--.", "H": "....",
    "I": "..", "Í": "..---.", "J": ".---", "K": "-.-", "L": ".-..",
    "M": "--", "N": "-.", "O": "---", "Ó": "---.", "Ö": "---.-",
    "Ő": "---..", "P": ".--.", "Q": "--.-", "R": ".-.", "S": "...",
    "T": "-", "U": "..-", "Ú": "..--", "Ü": "..--.", "Ű": "..---",
    "V": "...-", "W": ".--", "X": "-..-", "Y": "-.--", "Z": "--..",
    "0": "-----", "1": ".----", "2": "..---", "3": "...--",
    "4": "....-", "5": ".....", "6": "-....", "7": "--...",
    "8": "---..", "9": "----."
}

# Morse -> karakter szótár
reverse_morse_dict = {v: k for k, v in morse_dict.items()}

def text_to_morse(text):
    text = text.upper()
    morse_code = []
    for char in text:
        if char == " ":
            morse_code.append("/")  # szóköz Morse-ben
        elif char in morse_dict:
            morse_code.append(morse_dict[char])
        else:
            morse_code.append("?")  # ismeretlen karakter
    return " ".join(morse_code)

def morse_to_text(morse):
    words = morse.split(" / ")
    decoded_words = []
    for word in words:
        letters = word.split()
        decoded_letters = [reverse_morse_dict.get(l, "?") for l in letters]
        decoded_words.append("".join(decoded_letters))
    return " ".join(decoded_words)

# Interaktív menü
while True:
    print("\nMorse konverter")
    print("1. Szöveg -> Morse")
    print("2. Morse -> Szöveg")
    print("3. Kilépés")
    choice = input("Válassz egy lehetőséget (1/2/3): ")

    if choice == "1":
        szoveg = input("Írd be a szöveget: ")
        print("Morse kód:", text_to_morse(szoveg))
    elif choice == "2":
        morse = input("Írd be a Morse kódot (szavak '/'-al elválasztva): ")
        print("Szöveg:", morse_to_text(morse))
    elif choice == "3":
        print("Kilépés...")
        break
    else:
        print("Érvénytelen választás, próbáld újra.")
