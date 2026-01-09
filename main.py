from flask import Flask, request, url_for
import datetime
import pandas as pd
from Employee import Employees

app = Flask(__name__)

GREEK_DAYS = ['Δευτέρα','Τρίτη','Τετάρτη','Πέμπτη','Παρασκευή','Σάββατο','Κυριακή']

def generate_schedule(employees, start, end):
    dates = pd.date_range(start=start, end=end)
    data = {}

    # 1. Συλλογή Δεδομένων
    for e in employees:
        row = []
        for d in dates:
            ora = e.day_status(d.date())
            match ora:
                case {'status': "CLOSED"}: row.append("Κλειστά")
                case {'status': "LEAVE"}: row.append("Άδεια")
                case {'status': "REPO"}: row.append("Ρεπό")
                case __: row.append(ora["shift"]["ora"])
        data[e.name] = row

    df = pd.DataFrame(data, index=dates).T
    df.columns = [f"{GREEK_DAYS[d.weekday()]}<br>{d.date()}" for d in dates]

    weekly_schedule = [df.iloc[:, i:i+7] for i in range(0, df.shape[1], 7)]

    html = '<form method="POST" action="/save">'
    
    for week_index, week_df in enumerate(weekly_schedule, start=1):
        html += f'<div style="margin-bottom:40px;"><h3>Εβδομάδα {week_index} (Επεξεργασία)</h3>'
        html += '<div class="table-wrapper"><table class="table"><thead><tr>'
        html += '<th class="sticky-col">Υπάλληλος</th>'
        
        for col in week_df.columns:
            html += f'<th>{col}</th>'
        html += '</tr></thead><tbody>'

        for name, row in week_df.iterrows():
            html += f'<tr><td class="sticky-col"><strong>{name}</strong></td>'
            for date_col, value in row.items():
                clean_date = date_col.split('<br>')[-1]
                html += '<td>'
                html += f'<select name="edit_{name}_{clean_date}" style="width:100%; min-width:100px;">'
                
                all_options = ["06:00-14:00", "07:00-15:00", "08:00-16:00", "13:15-21:15", "Ρεπό", "Άδεια", "Κλειστά"]
                if value not in all_options:
                    all_options.insert(0, value)

                for opt in all_options:
                    selected = "selected" if opt == value else ""
                    html += f'<option value="{opt}" {selected}>{opt}</option>'
                
                html += '</select></td>'
            html += '</tr>'
        html += '</tbody></table></div></div>'

    html += """
        <div style="position:fixed; bottom:20px; right:20px; z-index:1000;">
            <button type="submit" style="padding:15px 25px; background-color:#28a745; color:white; border:none; border-radius:50px; cursor:pointer; font-size:16px; box-shadow: 2px 2px 10px rgba(0,0,0,0.3);">
                💾 Αποθήκευση & Προβολή Εκτύπωσης
            </button>
        </div>
    </form>
    """
    return html

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
            body {{ font-family: Arial, sans-serif; padding: 10px; background-color: #f4f4f4; }}
            .container {{ background: white; padding: 20px; border-radius: 8px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }}
            
            .table-wrapper {{ 
                width: 100%; 
                overflow-x: auto; 
                -webkit-overflow-scrolling: touch;
                border: 1px solid #ddd;
                margin-top: 10px;
            }}

            table {{ 
                width: 100%; 
                border-collapse: separate; 
                border-spacing: 0;
                background: white; 
            }}
            
            th, td {{ 
                padding: 10px; 
                text-align: center; 
                font-size: 11px; 
                border-bottom: 1px solid #ddd; 
                border-right: 1px solid #ddd;
                white-space: nowrap;
            }}

            th {{ background-color: #eee; position: sticky; top: 0; z-index: 2; }}

            .sticky-col {{
                position: sticky;
                left: 0;
                background-color: #f9f9f9 !important;
                z-index: 3;
                border-right: 2px solid #bbb !important;
                font-weight: bold;
                min-width: 100px;
            }}

            thead th.sticky-col {{ z-index: 4; background-color: #ddd !important; }}
            h2, h3 {{ color: #333; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h2>🗓️ Διαχείριση Προγράμματος</h2>
            <form method="post">
                Από: <input type="date" name="start" required> 
                Έως: <input type="date" name="end" required>
                <button type="submit" style="padding:5px 15px; cursor:pointer;">Δημιουργία</button>
            </form>
            <hr>
            {table}
        </div>
    </body>
    </html>
    """

@app.route("/save", methods=["POST"])
def save_changes():
    data = request.form
    all_dates = sorted(list(set([k.split('_')[-1] for k in data.keys() if k.startswith('edit_')])))
    employees = sorted(list(set([k.split('_')[1] for k in data.keys() if k.startswith('edit_')])))
    weeks = [all_dates[i:i + 7] for i in range(0, len(all_dates), 7)]

    print_html = """
    <html>
    <head>
        <style>
            body { font-family: Arial; padding: 20px; }
            table { width: 100%; border-collapse: collapse; margin-bottom: 30px; }
            th, td { border: 1px solid black; padding: 6px; text-align: center; font-size: 10px; }
            th { background-color: #f2f2f2; }
            .stats-row { background-color: #f9f9f9; font-weight: bold; font-size: 9px !important; }
            .no-print { margin-bottom: 20px; padding: 10px 20px; cursor: pointer; background: #007bff; color: white; border: none; border-radius: 5px; text-decoration: none; display: inline-block; }
            @media print { 
                .no-print { display: none; }
                .week-block { page-break-after: always; }
                @page { size: landscape; }
            }
        </style>
    </head>
    <body>
        <button class="no-print" onclick="window.print()">🖨️ Εκτύπωση / PDF</button>
        <a href="/" class="no-print">⬅️ Επιστροφή</a>
        <h2 style="text-align:center;">Τελικό Πρόγραμμα Εργασίας</h2>
    """

    for i, week_dates in enumerate(weeks, start=1):
        # --- ΛΟΓΙΚΗ SORTING ΑΝΑ ΕΒΔΟΜΑΔΑ (Με βάση την 1η μέρα) ---
        first_day = week_dates[0]
        def sort_priority(emp_name):
            val = data.get(f"edit_{emp_name}_{first_day}", "")
            if "06:00" in val: return 1
            if "07:00" in val: return 2
            if "08:00" in val: return 3
            if "13:15" in val: return 4
            return 5
        sorted_employees = sorted(employees, key=sort_priority)

        print_html += f'<div class="week-block"><h3>Εβδομάδα {i} ({week_dates[0]} έως {week_dates[-1]})</h3>'
        print_html += "<table><thead><tr><th>Υπάλληλος</th>"
        for d in week_dates:
            dt_obj = datetime.datetime.strptime(d, "%Y-%m-%d")
            print_html += f"<th>{GREEK_DAYS[dt_obj.weekday()]}<br>{d}</th>"
        print_html += "</tr></thead><tbody>"

        morning_counts = {d: 0 for d in week_dates}
        evening_counts = {d: 0 for d in week_dates}

        for emp in sorted_employees:
            print_html += f"<tr><td><strong>{emp}</strong></td>"
            for d in week_dates:
                val = data.get(f"edit_{emp}_{d}", "-")
                if val in ["06:00-14:00", "07:00-15:00", "08:00-16:00"]:
                    morning_counts[d] += 1
                elif val == "13:15-21:15":
                    evening_counts[d] += 1
                
                style = 'style="color: red; font-weight: bold;"' if val == "Ρεπό" else ""
                print_html += f"<td {style}>{val}</td>"
            print_html += "</tr>"
        
        # Προσθήκη Συνόλων
        print_html += '<tr class="stats-row"><td>Πρωινοί (Σύνολο)</td>'
        for d in week_dates: print_html += f'<td>{morning_counts[d]}</td>'
        print_html += '</tr>'
        print_html += '<tr class="stats-row"><td>Απογευματινοί (Σύνολο)</td>'
        for d in week_dates: print_html += f'<td>{evening_counts[d]}</td>'
        print_html += '</tr>'

        print_html += "</tbody></table></div>"

    print_html += "</body></html>"
    return print_html

if __name__ == "__main__":
    app.run(debug=True)