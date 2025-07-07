import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import requests
import io
import time
from trie import Trie

# === הגדרות ===
CARD_WIDTH = 100
CARD_HEIGHT = 150
NUM_COLS = 6
MAX_CARDS = 36
RARITIES = ["Common", "Rare", "Epic", "Legendary"]

CARD_BACK_URL = "https://d15f34w2p8l1cc.cloudfront.net/hearthstone/3980e7201eb27f5d58d28c466e5b636dfbd55e75401228be7baac704d9d7bdb0.png"
API_ENDPOINT = "http://localhost:5000/cards"

# מילון: name.lower() -> image URL
card_images = {}
card_buttons = {}

def load_image_from_url(url, size=(CARD_WIDTH, CARD_HEIGHT)):
    try:
        response = requests.get(url, timeout=10)
        img_data = response.content
        img = Image.open(io.BytesIO(img_data))
        img = img.resize(size, Image.ANTIALIAS)
        return ImageTk.PhotoImage(img)
    except Exception as e:
        print(f"❌ Failed to load image: {url}\n{e}")
        return None

card_back_image = load_image_from_url(CARD_BACK_URL)

class HearthstoneFullApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🃏 Hearthstone Card Finder")
        self.revealed = set()
        self.running = True
        self.card_buttons = {}
        self.image_refs = {}
        self.guess_var = tk.StringVar()

        self.rarity_vars = {r: tk.BooleanVar(value=True) for r in RARITIES}
        self.rarity_frame = tk.LabelFrame(root, text="Rarity Filter")
        self.rarity_frame.grid(row=0, column=0, columnspan=NUM_COLS)

        for idx, r in enumerate(RARITIES):
            cb = tk.Checkbutton(self.rarity_frame, text=r, variable=self.rarity_vars[r], command=self.refresh_cards)
            cb.grid(row=0, column=idx)

        self.input_frame = tk.Frame(root)
        self.input_frame.grid(row=1, column=0, columnspan=NUM_COLS, pady=10)

        self.entry = tk.Entry(self.input_frame, textvariable=self.guess_var, font=("Arial", 14))
        self.entry.grid(row=0, column=0)
        self.entry.bind("<Return>", self.check_guess)

        self.btn = tk.Button(self.input_frame, text="Guess", command=self.check_guess)
        self.btn.grid(row=0, column=1)

        self.grid_frame = tk.Frame(root)
        self.grid_frame.grid(row=2, column=0, columnspan=NUM_COLS)

        self.refresh_cards()

    def get_filtered_cards(self):
        selected = [r for r, var in self.rarity_vars.items() if var.get()]
        try:
            params = "&".join(f"rarity={r}" for r in selected)
            response = requests.get(f"{API_ENDPOINT}?{params}", timeout=10)
            data = response.json()
            return data.get("cards", [])[:MAX_CARDS]
        except Exception as e:
            messagebox.showerror("Error", f"❌ Failed to fetch cards: {e}")
            return []

    def refresh_cards(self):
        for widget in self.grid_frame.winfo_children():
            widget.destroy()

        self.card_buttons.clear()
        self.image_refs.clear()

        self.cards_data = self.get_filtered_cards()
        self.trie = Trie()
        for c in self.cards_data:
            self.trie.insert(c["name"].lower())

        for idx, card in enumerate(self.cards_data):
            row, col = divmod(idx, NUM_COLS)
            frame = tk.Frame(self.grid_frame, width=CARD_WIDTH, height=CARD_HEIGHT)
            frame.grid(row=row, column=col)

            lbl = tk.Label(frame, image=card_back_image)
            lbl.image = card_back_image
            lbl.pack()

            name = card["name"].lower()
            self.card_buttons[name] = lbl
            card_images[name] = card["img"]

    def check_guess(self, event=None):
        guess = self.guess_var.get().strip().lower()
        if not guess:
            return

        matches = [name for name in self.card_buttons if name == guess]
        if not matches:
            messagebox.showerror("❌", "Card not found or not in selected rarity.")
            return

        name = matches[0]
        if name in self.revealed:
            return

        url = card_images[name]
        img = load_image_from_url(url)
        if img:
            self.card_buttons[name].configure(image=img)
            self.card_buttons[name].image = img
            self.revealed.add(name)

        self.guess_var.set("")
        self.entry.focus()

if __name__ == "__main__":
    root = tk.Tk()
    app = HearthstoneFullApp(root)
    root.mainloop()
