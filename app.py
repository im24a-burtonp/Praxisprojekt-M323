from pathlib import Path
import json

from flask import Flask, render_template

app = Flask(__name__)
DATA_FILE = Path(__file__).parent / "data" / "ligue1-2024-25.json"


@app.route("/")
def index():
    with DATA_FILE.open(encoding="utf-8") as file:
        season = json.load(file)
    return render_template("index.html", season=season)


if __name__ == "__main__":
    app.run(debug=True)
