# --- memory_ui.py (updated to support rarity filter) ---
import tkinter as tk
from PIL import Image, ImageTk
import requests
from io import BytesIO

CARD_WIDTH = 120
CARD_HEIGHT = 180
CARDS_PER_ROW = 6

class MemoryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Hearthstone Memory")
        self.frame = tk.Frame(self.root, bg="black")
        self.frame.pack()

        self.rarity_vars = {
            "common": tk.BooleanVar(value=True),
            "rare": tk.BooleanVar(value=True),
            "epic": tk.BooleanVar(value=True),
            "legendary": tk.BooleanVar(value=True)
        }

        self.create_rarity_checkboxes()
        self.fetch_and_render_cards()

    def create_rarity_checkboxes(self):
        rarity_frame = tk.Frame(self.root, bg="gray")
        rarity_frame.pack(pady=10)

        for rarity, var in self.rarity_vars.items():
            cb = tk.Checkbutton(rarity_frame, text=rarity.title(), variable=var, bg="gray", fg="white")
            cb.pack(side=tk.LEFT, padx=5)

        reload_btn = tk.Button(rarity_frame, text="Reload", command=self.fetch_and_render_cards)
        reload_btn.pack(side=tk.LEFT, padx=10)

    def get_selected_rarities(self):
        return [k for k, v in self.rarity_vars.items() if v.get()]

    def fetch_and_render_cards(self):
        for widget in self.frame.winfo_children():
            widget.destroy()
        self.images = []

        rarities = self.get_selected_rarities()
        params = "&".join(f"rarity={r}" for r in rarities)
        api_url = f"http://localhost:5000/cards?{params}"

        try:
            response = requests.get(api_url, timeout=10)
            data = response.json()
            self.cards = data["cards"]
            self.render_cards()
        except Exception as e:
            print(f"❌ Failed to fetch cards: {e}")
            self.cards = []

    def render_cards(self):
        for index, card in enumerate(self.cards):
            row = index // CARDS_PER_ROW
            col = index % CARDS_PER_ROW

            try:
                response = requests.get(card["img"], timeout=10)
                img_data = Image.open(BytesIO(response.content)).resize((CARD_WIDTH, CARD_HEIGHT))
                tk_img = ImageTk.PhotoImage(img_data)
            except:
                continue

            label = tk.Label(self.frame, image=tk_img, borderwidth=2, relief="ridge")
            label.image = tk_img
            label.grid(row=row, column=col, padx=5, pady=5)
            self.images.append(tk_img)

        if not self.cards:
            tk.Label(self.frame, text="No cards found.", fg="white", bg="black").pack()


if __name__ == "__main__":
    root = tk.Tk()
    app = MemoryApp(root)
    root.mainloop()
