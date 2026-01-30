def text_to_binary(text):
    return ' '.join(format(ord(c), '08b') for c in text)

def binary_to_text(binary):
    try:
        chars = binary.split()
        return ''.join(chr(int(c, 2)) for c in chars)
    except ValueError:
        return "Hibás bináris kód!"

def number_to_binary(number):
    try:
        n = int(number)
        return bin(n)[2:]  # '0b'-t levágjuk
    except ValueError:
        return "Hibás szám!"

def binary_to_number(binary):
    try:
        return str(int(binary, 2))
    except ValueError:
        return "Hibás bináris szám!"

# Interaktív menü
while True:
    print("\n--- Bináris Konverter ---")
    print("1. Szöveg -> Bináris")
    print("2. Bináris -> Szöveg")
    print("3. Szám -> Bináris")
    print("4. Bináris -> Szám")
    print("5. Kilépés")
    
    choice = input("Válassz egy lehetőséget (1-5): ")

    if choice == "1":
        szoveg = input("Írd be a szöveget: ")
        print("Bináris:", text_to_binary(szoveg))
    elif choice == "2":
        binary = input("Írd be a bináris kódot (8 bites csoportok szóközzel): ")
        print("Szöveg:", binary_to_text(binary))
    elif choice == "3":
        szam = input("Írd be a számot: ")
        print("Bináris:", number_to_binary(szam))
    elif choice == "4":
        binary = input("Írd be a bináris számot: ")
        print("Szám:", binary_to_number(binary))
    elif choice == "5":
        print("Kilépés...")
        break
    else:
        print("Érvénytelen választás, próbáld újra.")
