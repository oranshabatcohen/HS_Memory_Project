from flask import Flask, jsonify, request, render_template_string
import requests

app = Flask(__name__)

RAPID_API_KEY = "7bc2b4fa68msh3e28c3a61602b96p188797jsnc86e5df015f9"
HEADERS = {
    "x-rapidapi-host": "omgvamp-hearthstone-v1.p.rapidapi.com",
    "x-rapidapi-key": RAPID_API_KEY
}

STANDARD_SETS = [
    "Core",
    "Event",
    "Whizbang's Workshop",
    "Perils in Paradise",
    "The Great Dark Beyond",
    "Into the Emerald Dream"
]

RARITY_ORDER = ["Common", "Rare", "Epic", "Legendary"]

def fetch_cards_by_set(set_name):
    url = f"https://omgvamp-hearthstone-v1.p.rapidapi.com/cards/sets/{set_name}"
    try:
        response = requests.get(url, headers=HEADERS, timeout=20)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Failed to fetch set {set_name}: {e}")
        return []

@app.route("/cards")
def show_cards():
    selected_rarities = request.args.getlist("rarity")
    selected_rarities = [r.capitalize() for r in selected_rarities]
    if not selected_rarities or "All" in selected_rarities:
        selected_rarities = RARITY_ORDER

    all_cards_by_set = {}
    for set_name in STANDARD_SETS:
        cards = fetch_cards_by_set(set_name)
        filtered_cards = [
            {"name": c["name"], "img": c["img"]}
            for c in cards
            if "name" in c and "img" in c and c.get("rarity") in selected_rarities
        ]
        if filtered_cards:
            all_cards_by_set[set_name] = filtered_cards

    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Hearthstone Guess Game</title>
        <style>
            body {
                background: #1e1e1e;
                color: #fff;
                font-family: sans-serif;
                text-align: center;
            }
            .rarity-filter {
                margin: 10px;
            }
            .rarity-filter label {
                margin-right: 10px;
            }
            .grid {
                display: flex;
                flex-wrap: wrap;
                justify-content: center;
                gap: 10px;
                margin: 20px;
            }
            .card {
                width: 120px;
                height: 180px;
                perspective: 1000px;
                display: inline-block;
                position: relative;
            }
            .card-inner {
                width: 100%;
                height: 100%;
                position: relative;
                transform-style: preserve-3d;
                transition: transform 0.6s;
            }
            .card.flip .card-inner {
                transform: rotateY(180deg);
            }
            .card-front, .card-back {
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                backface-visibility: hidden;
                border-radius: 8px;
                object-fit: cover;
            }
            .card-front {
                transform: rotateY(180deg);
            }
            .guess-box {
                margin-top: 20px;
            }
            .guess-box input {
                padding: 10px;
                font-size: 16px;
                width: 250px;
            }
            .guess-box button {
                padding: 10px 20px;
                font-size: 16px;
                margin-left: 10px;
            }
            .set-title {
                margin-top: 40px;
                font-size: 20px;
                font-weight: bold;
            }
            .set-separator {
                height: 3px;
                background-color: #aaa;
                margin: 10px auto 30px auto;
                width: 90%;
            }
        </style>
    </head>
    <body>
        <h1>🃏 Guess the Hearthstone Cards</h1>

        <div class="guess-box">
            <input type="text" id="guess" placeholder="Type card name..." />
            <button onclick="checkGuess()">Guess</button>
        </div>

        <form method="get">
            <div class="rarity-filter">
                {% for rarity in ['Common', 'Rare', 'Epic', 'Legendary', 'All'] %}
                    <label>
                        <input type="checkbox" name="rarity" value="{{ rarity }}"
                        {% if rarity in selected_rarities or ('All' in selected_rarities and rarity != 'All') %}
                            checked
                        {% endif %}>
                        {{ rarity }}
                    </label>
                {% endfor %}
                <button type="submit">Apply</button>
            </div>
        </form>

        {% for set_name, cards in all_cards_by_set.items() %}
            <div class="set-separator"></div>
            <h2 class="set-title">{{ set_name }}</h2>
            <div class="grid">
                {% for card in cards %}
                    <div class="card" data-name="{{ card.name|lower }}" data-revealed="false">
                        <div class="card-inner">
                            <img class="card-front" src="{{ card.img }}">
                            <img class="card-back" src="/static/card_back.png">
                        </div>
                    </div>
                {% endfor %}
            </div>
        {% endfor %}

        <script>
            function clean(str) {
                return str.toLowerCase().replace(/\s+/g, " ").trim();
            }

            async function checkGuess() {
                const input = document.getElementById("guess");
                const guess = clean(input.value);
                if (!guess) return;

                const cards = document.querySelectorAll(".card");
                let found = false;

                for (const div of cards) {
                    if (clean(div.dataset.name) === guess && div.dataset.revealed === "false") {
                        input.blur();
                        div.scrollIntoView({ behavior: "smooth", block: "center", inline: "center" });
                        await new Promise(r => setTimeout(r, 800));
                        div.classList.add("flip");
                        div.dataset.revealed = "true";
                        found = true;
                        break;
                    }
                }

                if (!found) {
                    alert("❌ Not found! Try again.");
                } else {
                    await new Promise(r => setTimeout(r, 3500));
                    input.value = "";
                    input.focus();
                    checkWinCondition();
                }
            }

            function checkWinCondition() {
                const allCards = document.querySelectorAll(".card");
                const allRevealed = Array.from(allCards).every(div => div.dataset.revealed === "true");
                if (allRevealed) {
                    setTimeout(() => {
                        alert("🎉 Congratulations! You've guessed all the cards! 🎉");
                    }, 500);
                }
            }

            document.getElementById("guess").addEventListener("keydown", function (e) {
                if (e.key === "Enter") {
                    e.preventDefault();
                    checkGuess();
                }
            });
        </script>
    </body>
    </html>
    """

    return render_template_string(
        html_template,
        all_cards_by_set=all_cards_by_set,
        selected_rarities=selected_rarities
    )

if __name__ == "__main__":
    app.run(debug=True)
