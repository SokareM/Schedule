from flask import Flask, request
import datetime
import pandas as pd
from Employee import Employees

app = Flask(__name__)

GREEK_DAYS = ['Δευτέρα','Τρίτη','Τετάρτη','Πέμπτη','Παρασκευή','Σάββατο','Κυριακή']

def generate_schedule(employees, start, end):
    dates = pd.date_range(start=start, end=end)
    data = {}

    for e in employees:
        data[e.name] = [
            e.day_status(d.date()) for d in dates
        ]

    df = pd.DataFrame(data, index=dates).T
    df.columns = [f"{GREEK_DAYS[d.weekday()]}<br>{d.date()}" for d in dates]
    return df.to_html(classes="table", border=1)

@app.route("/", methods=["GET", "POST"])
def index():
    table = ""
    if request.method == "POST":
        start = datetime.datetime.strptime(request.form["start"], "%Y-%m-%d").date()
        end = datetime.datetime.strptime(request.form["end"], "%Y-%m-%d").date()
        table = generate_schedule(Employees, start, end)

    return f"""
    <html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body {{ font-family: Arial; padding: 10px; }}
            table {{ width: 100%; border-collapse: collapse; }}
            th, td {{ padding: 6px; text-align: center; }}
        </style>
    </head>
    <body>
        <h2>Πρόγραμμα Εργασίας</h2>
        <form method="post">
            Έναρξη: <input type="date" name="start" required><br><br>
            Λήξη: <input type="date" name="end" required><br><br>
            <button type="submit">Δημιουργία</button>
        </form>
        <br>
        {table}
    </body>
    </html>
    """
