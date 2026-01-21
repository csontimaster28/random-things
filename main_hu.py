import tkinter as tk
from tkinter import messagebox
import tkinter.font as tkfont
import random


WORDS = [
	'kígyó', 'akvárium', 'programozás', 'ország', 'ablak', 'játék', 'asztal', 'számítógép',
	'erdő', 'kulcsszó', 'titok', 'ablakok', 'grafika', 'egyszerű', 'könyv', 'toll', 'ceruza',
    'iskola', 'tanulás', 'barát', 'család', 'nyár', 'tél', 'tavasz', 'ősz', 'hegy', 'folyó', 'tó', 'erdő', 'virág', 'fa', 'madár', 'hal', 'kutya', 'macska', 'autó', 'bicikli', 'busz', 'vonat', 'repülő', 'hajó'
]


class HangmanApp(tk.Tk):
	def __init__(self):
		super().__init__()
		self.title('Hangman - Magyar')
		self.resizable(True, True)
		self.configure(bg='#163b16')
		self._build_ui()
		self.new_game()

	def _build_ui(self):
		# Canvas a rajzoláshoz (krétatáblás háttér)
		self.canvas = tk.Canvas(self, width=420, height=400, bg='#173b17', highlightthickness=0)
		self.canvas.grid(row=0, column=0, rowspan=4, padx=10, pady=10)
		self._decorate_chalkboard()

		# Jobb oldali panel
		right = tk.Frame(self, bg='#163b16')
		right.grid(row=0, column=1, sticky='n', padx=10, pady=10)

		# Kréta-stílusú font (fallback konzolos/monospace italic)
		self.chalk_font = tkfont.Font(family='Consolas', size=28, slant='italic')
		small_chalk = tkfont.Font(family='Consolas', size=10, slant='italic')

		self.word_var = tk.StringVar(value='')
		word_label = tk.Label(right, textvariable=self.word_var, font=self.chalk_font, width=16, bg='#163b16', fg='white')
		word_label.pack(pady=(0, 10))

		self.message_var = tk.StringVar(value='Üdv! Találd ki a szót.')
		msg_label = tk.Label(right, textvariable=self.message_var, fg='#e6f2e6', bg='#163b16', font=small_chalk)
		msg_label.pack(pady=(0, 10))

		# Betűgombok (magyar ékezetes ábécé egyszerűsítve)
		letters_frame = tk.Frame(right, bg='#163b16')
		letters_frame.pack()
		self.letter_buttons = {}
		letters = 'AÁBCDEÉFGHIÍJKLMNOÓÖŐPQRSTUÚÜŰVWXYZ'
		for idx, ch in enumerate(letters):
			btn = tk.Button(letters_frame, text=ch, width=3, command=lambda c=ch: self.guess(c),
							bg='#2f5b2f', fg='white', activebackground='#5b8b5b', relief='flat', bd=1)
			btn.grid(row=idx // 10, column=idx % 10, padx=2, pady=2)
			self.letter_buttons[ch] = btn

		# Új játék gomb
		new_btn = tk.Button(right, text='Új játék', command=self.new_game, width=20, bg='#1f4b1f', fg='white', relief='raised')
		new_btn.pack(pady=(10, 5))

		# Nyelv váltás gomb
		switch_btn = tk.Button(right, text='Switch to English', command=self.switch_language, width=20, bg='#1f4b1f', fg='white', relief='raised')
		switch_btn.pack(pady=(0, 5))

		# Kilépés
		quit_btn = tk.Button(right, text='Kilépés', command=self.quit, width=20, bg='#1f4b1f', fg='white', relief='raised')
		quit_btn.pack()

		# billentyűzet kezelése
		self.bind('<Key>', self._on_key)

	def _decorate_chalkboard(self):
		# Finom kréta textúra: apró halvány pontok és vonalak
		import random as _r
		for _ in range(220):
			x = _r.randint(0, 420)
			y = _r.randint(0, 400)
			alpha = _r.randint(20, 80)
			# halvány fehér pötty
			col = f'#{alpha:02x}{alpha:02x}{alpha:02x}'
			self.canvas.create_oval(x, y, x+1, y+1, fill=col, outline=col)
		# horizontális enyhe csíkok
		for y in range(30, 400, 80):
			self.canvas.create_line(0, y, 420, y, fill='#0d2a0d', width=1)

	def _on_key(self, event):
		ch = event.char.upper()
		if ch.isalpha() and ch in self.letter_buttons:
			if self.letter_buttons[ch]['state'] == 'normal':
				self.guess(ch)
				print(f'[DEBUG] Key pressed: {ch}')

	def new_game(self):
		self.secret = random.choice(WORDS).upper()
		self.guessed = set()
		self.mistakes = 0
		for b in self.letter_buttons.values():
			b.config(state='normal')
		self.canvas.delete('hangman')
		self._draw_gallows()
		self._update_display()
		self.message_var.set('Jó szórakozást!')
		print('[DEBUG] New game started')
		print(f'[DEBUG] Solution: {self.secret}')

	def _update_display(self):
		# megjelenítés krétás stílusban
		display = ' '.join([c if c in self.guessed else '_' for c in self.secret])
		self.word_var.set(display)

	def switch_language(self):
		print("[DEBUG] Switched to English")
		self.destroy()
		import main_en
		app = main_en.HangmanApp()
		app.mainloop()

	def guess(self, ch):
		ch = ch.upper()
		if ch in self.guessed:
			return
		self.guessed.add(ch)
		if ch in self.secret:
			self._update_display()
			if all(c in self.guessed for c in set(self.secret)):
				self._win()
		else:
			self.mistakes += 1
			self._draw_hangman_part(self.mistakes)
			if self.mistakes >= 6:
				self._lose()
		# letiltjuk a gombot
		if ch in self.letter_buttons:
			self.letter_buttons[ch].config(state='disabled')

	def _win(self):
		self.message_var.set('Nyertél!')
		messagebox.showinfo('Nyertél!', f'Gratulálok! A szó: {self.secret}')
		print(f'[DEBUG] WIN')
		for b in self.letter_buttons.values():
			b.config(state='disabled')

	def _lose(self):
		self.message_var.set('Vesztettél!')
		self._update_display()
		messagebox.showinfo('Vesztettél!', f'Vesztettél A szó: {self.secret}')
		print(f'[DEBUG] LOSE')
		for b in self.letter_buttons.values():
			b.config(state='disabled')

	def _draw_gallows(self):
		c = self.canvas
		# talapzat (a 'hangman' taggal törölhető a későbbiekben)
		c.create_line(20, 370, 400, 370, width=4, fill='white', tags='hangman')
		c.create_line(80, 370, 80, 40, width=4, fill='white', tags='hangman')
		c.create_line(80, 40, 260, 40, width=4, fill='white', tags='hangman')
		c.create_line(260, 40, 260, 80, width=4, fill='white', tags='hangman')

	def _draw_hangman_part(self, step):
		c = self.canvas
		if step == 1:
			# fej
			c.create_oval(230, 80, 290, 140, width=3, outline='white', tags='hangman')
		elif step == 2:
			# test
			c.create_line(260, 140, 260, 240, width=3, fill='white', tags='hangman')
		elif step == 3:
			# bal kar
			c.create_line(260, 160, 210, 190, width=3, fill='white', tags='hangman')
		elif step == 4:
			# jobb kar
			c.create_line(260, 160, 310, 190, width=3, fill='white', tags='hangman')
		elif step == 5:
			# bal láb
			c.create_line(260, 240, 230, 300, width=3, fill='white', tags='hangman')
		elif step == 6:
			# jobb láb
			c.create_line(260, 240, 290, 300, width=3, fill='white', tags='hangman')


def main():
	app = HangmanApp()
	app.mainloop()


if __name__ == '__main__':
	main()

