import datetime
import pandas as pd
from Employee import Employees

GREEK_DAYS = ['Δευτέρα', 'Τρίτη', 'Τετάρτη', 'Πέμπτη', 'Παρασκευή', 'Σάββατο', 'Κυριακή']

def generate_schedule(employees, start_date, end_date):
    headers = pd.date_range(start=start_date, end=end_date)
    df = pd.DataFrame(index=[e.name for e in employees] + ['Σύνολο'], columns=headers)

    for date in headers:
        for employee in employees:
            info = employee.day_status(date.date())
            df.loc[employee.name, date] = info["shift"]["ora"] if info["shift"] else info["status"]

        morning = ['06:00-14:00', '07:00-15:00', '08:00-16:00']
        afternoon = ['01:15-09:15']

        df.loc['Σύνολο', date] = f"Π: {df[date].isin(morning).sum()}, Α: {df[date].isin(afternoon).sum()}"

    return df

def print_schedule_weekly(df):
    week_starts = df.columns[::7]

    for start in week_starts:
        week_cols = df.columns[df.columns.get_loc(start):df.columns.get_loc(start)+7]
        week_df = df[week_cols].copy()
        week_df.columns = [GREEK_DAYS[d.weekday()] for d in week_df.columns]

        print(f"\nΕβδομάδα που ξεκινάει {start.date()}")
        print(week_df)
        print("-" * 60)

def parse_date(s):
    return datetime.datetime.strptime(s, "%Y-%m-%d").date()

if __name__ == "__main__":
    print("Δώσε ημερομηνίες (YYYY-MM-DD)")
    start = parse_date(input("Έναρξη: "))
    end = parse_date(input("Λήξη: "))

    if end < start:
        raise ValueError("Η λήξη δεν μπορεί να είναι πριν την έναρξη")

    schedule = generate_schedule(Employees, start, end)
    print_schedule_weekly(schedule)
