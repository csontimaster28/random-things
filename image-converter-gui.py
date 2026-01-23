import os
from tkinter import Tk, filedialog, simpledialog, messagebox, Button, Label
from PIL import Image

SUPPORTED_FORMATS = ["PNG", "JPG", "JPEG", "WEBP", "BMP", "TIFF", "GIF"]

def convert_images():
    # Fájlok kiválasztása
    file_paths = filedialog.askopenfilenames(title="Válassz képeket", 
                                             filetypes=[("Képek", "*.png *.jpg *.jpeg *.webp *.bmp *.tiff *.gif")])
    if not file_paths:
        return

    # Célformátum kiválasztása
    format_choice = simpledialog.askstring("Formátum", f"Milyen formátumba konvertáljuk? {SUPPORTED_FORMATS}")
    if not format_choice:
        return
    format_choice = format_choice.upper()
    if format_choice not in SUPPORTED_FORMATS:
        messagebox.showerror("Hiba", f"A formátum nem támogatott: {format_choice}")
        return

    for path in file_paths:
        # Mentési útvonal és név megadása
        save_path = filedialog.asksaveasfilename(title=f"Mentés {os.path.basename(path)}",
                                                 defaultextension=f".{format_choice.lower()}",
                                                 filetypes=[(format_choice, f"*.{format_choice.lower()}")])
        if not save_path:
            continue

        # Kép betöltése
        image = Image.open(path)

        # JPG esetén RGB konvertálás
        if format_choice in ["JPG", "JPEG"]:
            image = image.convert("RGB")

        image.save(save_path, format_choice)
        print(f"Sikeresen konvertált: {save_path}")

    messagebox.showinfo("Kész", "Minden kiválasztott kép konvertálva lett!")

# GUI
root = Tk()
root.title("Kép konverter")
root.geometry("300x150")

Label(root, text="Képek konvertálása különböző formátumokba").pack(pady=10)
Button(root, text="Képek kiválasztása és konvertálás", command=convert_images).pack(pady=20)

root.mainloop()
