from PIL import Image, ImageTk
import os
from tkinter import Tk, filedialog, Button, Label, messagebox
import tkinter as tk

# Hide the root tkinter window initially
root = Tk()
root.withdraw()

# Open file explorer to select image
image_path = filedialog.askopenfilename(
    title="Válassz egy képet",
    filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp *.gif"), ("All files", "*.*")]
)

if not image_path:
    print("Nem választottál ki képet!")
    exit()

print(f"Kiválasztott kép: {image_path}")

# Get target resolution from user
resolution = input("Add meg a célfeloldottságot (pl. 120x340): ")
try:
    width, height = map(int, resolution.lower().split('x'))
except:
    print("Hibás formátum! Pl.: 120x340")
    exit()

# Load image
try:
    img = Image.open(image_path)
    print(f"Eredeti méret: {img.size}")
except:
    print("A kép nem nyitható meg!")
    exit()

# Downscale image
img_downscaled = img.resize((width, height), Image.Resampling.LANCZOS)
print(f"Új méret: {img_downscaled.size}")

# Create preview window
preview_window = tk.Toplevel(root)
preview_window.title(f"Előnézet - {width}x{height}")

# Scale up the image for display (so small images are visible)
display_scale = max(1, 400 // max(width, height))
display_img = img_downscaled.resize((width * display_scale, height * display_scale), Image.Resampling.NEAREST)
photo = ImageTk.PhotoImage(display_img)

# Display image
label = Label(preview_window, image=photo)
label.image = photo  # Keep a reference
label.pack(pady=10)

# Save button
def save_image():
    save_path = filedialog.asksaveasfilename(
        title="Mentés helye",
        defaultextension=".png",
        filetypes=[("PNG", "*.png"), ("JPEG", "*.jpg"), ("BMP", "*.bmp"), ("All files", "*.*")]
    )
    if save_path:
        img_downscaled.save(save_path)
        print(f"Sikeresen mentve: {save_path}")
        messagebox.showinfo("Siker", f"Kép sikeresen mentve:\n{save_path}")

save_btn = Button(preview_window, text="Mentés", command=save_image, bg="green", fg="white", padx=20, pady=10)
save_btn.pack(pady=10)

# Cancel button
def close_window():
    preview_window.destroy()
    root.destroy()

cancel_btn = Button(preview_window, text="Mégsem", command=close_window, bg="red", fg="white", padx=20, pady=10)
cancel_btn.pack(pady=5)

root.deiconify()
root.withdraw()
preview_window.mainloop()
