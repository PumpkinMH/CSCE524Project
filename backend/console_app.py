import os
import django
from datetime import timedelta

# Setup Django environment to talk to your Data Access Layer
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medtracker.settings')
django.setup()

from django.utils import timezone
from api.dao import MedicationDAO, DoseLogDAO

def main():
    print("\n========================================")
    print("      MEDISAFE TERMINAL DASHBOARD      ")
    print("========================================\n")
    print("Welcome back! (Single-User Mode Active)\n")

    offset_days = 0 

    while True:
        target_date = timezone.now().date() + timedelta(days=offset_days)
        
        # Label the date window
        if offset_days == 0:
            day_label = "TODAY"
        elif offset_days == -1:
            day_label = "YESTERDAY"
        elif offset_days == 1:
            day_label = "TOMORROW"
        else:
            day_label = target_date.strftime("%b %d, %Y")

        print(f"\n=== DASHBOARD MENU ({day_label}) ===")
        print("1. View Schedule for this day")
        print("2. Go back one day (<)")
        print("3. Go forward one day (>)")
        print("4. Return to Today")
        print("5. View all medications (General)")
        print("6. Exit")
        
        choice = input("\nSelect an option (1-6): ")
        
        if choice == '1':
            # Fetching from the Database via our Manual DAO
            logs = DoseLogDAO.get_logs_for_date(target_date)
            
            print(f"\n*** Schedule for {target_date.strftime('%A, %b %d')} ***")
            
            if not logs:
                print("  No medications scheduled for this day.")
            else:
                # Grouping the dictionary results using Python list comprehensions
                taken = [log for log in logs if log['status'] == 'taken']
                pending = [log for log in logs if log['status'] == 'pending']
                missed = [log for log in logs if log['status'] in ['missed', 'skipped']]
                
                if taken:
                    print("\n[ ALREADY TAKEN ]")
                    for log in taken:
                        time_str = log['scheduled_datetime'].strftime('%I:%M %p')
                        print(f"  v {time_str}: {log['name']}")
                
                if pending:
                    print("\n[ UPCOMING / PENDING ]")
                    for log in pending:
                        time_str = log['scheduled_datetime'].strftime('%I:%M %p')
                        print(f"  - {time_str}: {log['name']}")
                        
                if missed:
                    print("\n[ MISSED / SKIPPED ]")
                    for log in missed:
                        time_str = log['scheduled_datetime'].strftime('%I:%M %p')
                        print(f"  x {time_str}: {log['name']}")

        elif choice == '2': offset_days -= 1
        elif choice == '3': offset_days += 1
        elif choice == '4': offset_days = 0
        elif choice == '5':
            print("\n*** YOUR MEDICATIONS ***")
            # Fetch all meds, then filter active ones in Python
            meds = MedicationDAO.get_all()
            active_meds = [m for m in meds if m['is_active']]
            
            if not active_meds:
                print("  No active medications found.")
            for med in active_meds:
                print(f"  * {med['name']} ({med['strength']}), {med['condition_treated']}")
                
        elif choice == '6':
            print("Exiting application.")
            break
        else:
            print("Invalid selection, please try again.")
            
if __name__ == "__main__":
    main()