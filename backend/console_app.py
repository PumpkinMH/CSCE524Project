import os
import django
from datetime import timedelta

# 1. Setup Django environment to talk to your Data Access Layer
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medtracker.settings')
django.setup()

from django.utils import timezone
from api.models import User, Medication, DoseLog

def get_day_bounds(target_date):
    """Calculates the exact start and end of a specific date."""
    start_of_day = timezone.make_aware(timezone.datetime.combine(target_date, timezone.datetime.min.time()))
    end_of_day = start_of_day + timedelta(days=1)
    return start_of_day, end_of_day

def main():
    print("\n========================================")
    print("       MEDISAFE TERMINAL DASHBOARD      ")
    print("========================================\n")
    
    email = input("Please enter your email to log in: ")
    
    try:
        current_user = User.objects.get(email=email)
        print(f"\nWelcome back, {current_user.first_name}!")
    except User.DoesNotExist:
        print("\nError: User not found. Please check the email and try again.")
        return

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
            start, end = get_day_bounds(target_date)
            
            # Fetching from the DoseLog table via the ORM (Our DAO)
            logs = DoseLog.objects.filter(
                medication__user=current_user,
                scheduled_datetime__gte=start,
                scheduled_datetime__lt=end
            ).order_by('scheduled_datetime')
            
            print(f"\n--- Schedule for {target_date.strftime('%A, %b %d')} ---")
            
            if not logs.exists():
                print("  No medications scheduled for this day.")
            else:
                taken = logs.filter(status='taken')
                pending = logs.filter(status='pending')
                missed = logs.filter(status__in=['missed', 'skipped'])
                
                if taken.exists():
                    print("\n[ ALREADY TAKEN ]")
                    for log in taken:
                        print(f"  v {log.scheduled_datetime.strftime('%I:%M %p')}: {log.medication.name}")
                
                if pending.exists():
                    print("\n[ UPCOMING / PENDING ]")
                    for log in pending:
                        print(f"  - {log.scheduled_datetime.strftime('%I:%M %p')}: {log.medication.name}")
                        
                if missed.exists():
                    print("\n[ MISSED / SKIPPED ]")
                    for log in missed:
                        print(f"  x {log.scheduled_datetime.strftime('%I:%M %p')}: {log.medication.name}")

        elif choice == '2': offset_days -= 1
        elif choice == '3': offset_days += 1
        elif choice == '4': offset_days = 0
        elif choice == '5':
            print("\n--- YOUR MEDICATIONS ---")
            meds = Medication.objects.filter(user=current_user, is_active=True)
            for med in meds:
                print(f"  * {med.name} ({med.strength}) - {med.condition_treated}")
        elif choice == '6':
            print("Logging out.")
            break
            
if __name__ == "__main__":
    main()
