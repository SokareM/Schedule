import datetime

class Employee:
    def __init__(self,name,start_date,repo_index=0,leave=None,shifts=None,const=False,group=None):
        self.name = name
        self.group = group
        self.start_date = start_date
        self.repo_index = repo_index
        self.leave = leave or []
        self.shifts = shifts or [
            {"vardia": "Πρωί", "ora": "07:00-15:00"},
            {"vardia": "Απόγευμα", "ora": "13:00-21:00"}
        ]
        if self.shifts[0]['vardia'] == 'Πρωί':
            self.group = 'A'
        else:
            self.group = 'B'    
        self.const = const

    WORK_DAYS = ['Δευτέρα', 'Τρίτη', 'Τετάρτη', 'Πέμπτη', 'Παρασκευή', 'Σάββατο']
    CLOSED_DAY = 'Κυριακή'
    def get_monday_of_week(self, date):
        return date - datetime.timedelta(days=date.weekday())

    def shift(self, date_to_check):
        if not isinstance(date_to_check, datetime.date):
            raise ValueError("date_to_check must be a datetime.date object")
        monday_of_week = self.get_monday_of_week(date_to_check)
        monday_start = self.get_monday_of_week(self.start_date)
        if monday_of_week < monday_start:
            raise ValueError("date_to_check cannot be earlier than start_date")
        weeks_passed = (monday_of_week - monday_start).days // 7
        new_shift_index = weeks_passed % len(self.shifts)
        return self.shifts[new_shift_index]
    
    def repo(self, date_to_check):
        monday_of_week = self.get_monday_of_week(date_to_check)
        monday_start = self.get_monday_of_week(self.start_date)
        if monday_of_week < monday_start:
          raise ValueError("date_to_check cannot be earlier than start_date")
        weeks_passed = (monday_of_week - monday_start).days // 7
        new_repo_index = (self.repo_index + weeks_passed) % len(self.WORK_DAYS)
        return self.WORK_DAYS[new_repo_index]
    
    def day_status(self, date_to_check):
        if not isinstance(date_to_check, datetime.date):
          raise ValueError("date_to_check must be datetime.date")

    # Κυριακή
        if date_to_check.weekday() == 6:
          return {"date": date_to_check, "status": "CLOSED", "shift": None}

    # Άδεια
        if date_to_check in self.leave:
          return {"date": date_to_check, "status": "LEAVE", "shift": None}

    # Ρεπό
        if self.repo(date_to_check) == self.WORK_DAYS[date_to_check.weekday()]:
          return {"date": date_to_check, "status": "REPO", "shift": None}

    # Εργασία
        return {
        "date": date_to_check,
        "status": "WORK",
        "shift": self.shift(date_to_check)
    }

       
                
