import requests
from datetime import datetime

# Change this URL to the one that render gives you for the Django server
BASE_URL = "http://localhost:8000/api"

def print_header(title):
    print(f"\n{'='*50}\n {title.center(48)} \n{'='*50}")

def input_prompt(prompt, default=None, required=False, type_func=str):
    """Helper to safely get and cast user input."""
    while True:
        val = input(prompt).strip()
        if not val:
            if default is not None:
                return default
            if required:
                print("  -> This value is required.")
                continue
            return None
        try:
            return type_func(val)
        except ValueError:
            print(f"  -> Invalid input type. Expected {type_func.__name__}")

def make_request(method, endpoint, data=None, params=None):
    """Helper to make HTTP requests to the REST API Service Layer."""
    url = f"{BASE_URL}{endpoint}"
    headers = {'Accept': 'application/json'}
    try:
        response = requests.request(method, url, json=data, params=params, headers=headers)

        if response.status_code >= 400:
            try:
                # Try to extract a clean error message from JSON
                err_data = response.json()
                msg = err_data.get('error') or err_data.get('detail') or str(err_data)
                print(f"  -> API Error ({response.status_code}): {msg}")
            except ValueError:
                # Fallback to the HTTP status reason (e.g., "Not Found") if response is HTML
                print(f"  -> API Error ({response.status_code}): {response.reason}")
            return None
        
        if response.status_code == 204:
            return True
            
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"  -> Connection Error: Make sure the Django server is running! ({e})")
        return None

# ==========================================
#              MEDICATION MENU
# ==========================================
def medication_menu():
    while True:
        print_header("MEDICATION MANAGEMENT (API CLIENT)")
        print("1. View Active Inventory")
        print("2. View Refill Alerts")
        print("3. Add New Medication")
        print("4. Update Medication Details")
        print("5. Upgrade Prescription")
        print("6. Refill Medication")
        print("7. Archive Medication")
        print("8. Purge Medication")
        print("9. Back to Main Menu")
        
        choice = input("\nSelect an option (1-9): ")
        
        if choice == '1':
            meds = make_request('GET', '/medications/')
            if meds is not None:
                if not meds:
                    print("  No active medications found.")
                for m in meds:
                    print(f"  [{m['medication_id']}] {m['name']} ({m.get('strength', 'N/A')}) - {m.get('amount_left', 0)} left")
        
        elif choice == '2':
            alerts = make_request('GET', '/medications/refill-alerts/')
            if alerts is not None:
                if not alerts:
                    print("  No refill alerts. Inventory looks good!")
                for m in alerts:
                    print(f"  ALERT: {m['name']} is low! ({m['amount_left']} left, threshold: {m['refill_threshold']})")
                
        elif choice == '3':
            print("\n-- Add New Medication --")
            data = {
                'name': input_prompt("Name*: ", required=True),
                'medication_type': input_prompt("Type: "),
                'strength': input_prompt("Strength: "),
                'condition_treated': input_prompt("Condition Treated: "),
                'instructions': input_prompt("Instructions: "),
                'amount_left': input_prompt("Amount Left (default 0): ", default=0.0, type_func=float),
                'refill_threshold': input_prompt("Refill Threshold (default 0): ", default=0.0, type_func=float)
            }
            result = make_request('POST', '/medications/', data=data)
            if result:
                print(f"  -> Success! Added medication.")
                
        elif choice == '4':
            print("\n-- Update Details --")
            med_id = input_prompt("Medication ID*: ", required=True)
            data = {
                'strength': input_prompt("New Strength (leave blank to keep current): "),
                'condition_treated': input_prompt("New Condition (leave blank to keep current): "),
                'instructions': input_prompt("New Instructions (leave blank to keep current): ")
            }
            # Remove empty keys so we don't accidentally blank them out if the user hit enter
            data = {k: v for k, v in data.items() if v is not None}
            
            if make_request('PATCH', f'/medications/{med_id}/details/', data=data):
                print("  -> Medication details updated.")
                
        elif choice == '5':
            print("\n-- Upgrade Prescription --")
            med_id = input_prompt("Medication ID*: ", required=True)
            new_strength = input_prompt("New Strength*: ", required=True)
            
            result = make_request('POST', f'/medications/{med_id}/upgrade/', data={'new_strength': new_strength})
            if result:
                print(f"  -> Upgraded! Old archived. New active medication created.")
                
        elif choice == '6':
            print("\n-- Refill Inventory --")
            med_id = input_prompt("Medication ID*: ", required=True)
            amount = input_prompt("Amount to add*: ", required=True, type_func=float)
            
            if make_request('POST', f'/medications/{med_id}/refill/', data={'amount_added': amount}):
                print("  -> Refilled successfully.")
                
        elif choice == '7':
            print("\n-- Archive Medication --")
            med_id = input_prompt("Medication ID*: ", required=True)
            if make_request('POST', f'/medications/{med_id}/archive/'):
                print("  -> Medication archived (soft deleted).")
                
        elif choice == '8':
            print("\n-- Purge Medication --")
            med_id = input_prompt("Medication ID*: ", required=True)
            confirm = input_prompt("Are you sure? This cannot be undone (y/N): ", default="n")
            if confirm.lower() == 'y':
                if make_request('DELETE', f'/medications/{med_id}/'):
                    print("  -> Medication permanently deleted.")
                
        elif choice == '9':
            break

# ==========================================
#              SCHEDULE MENU
# ==========================================
def schedule_menu():
    while True:
        print_header("SCHEDULE MANAGEMENT (API CLIENT)")
        print("1. View All Schedules")
        print("2. Create Schedule")
        print("3. Update Schedule")
        print("4. Remove Schedule")
        print("5. Back to Main Menu")
        
        choice = input("\nSelect an option (1-5): ")
        
        if choice == '1':
            schedules = make_request('GET', '/schedules/')
            if schedules is not None:
                if not schedules:
                    print("  No schedules found.")
                for s in schedules:
                    freq_val = s.get('frequency_value')
                    freq_str = f" (Value: {freq_val})" if freq_val else ""
                    times = ", ".join(s.get('reminder_times', []))
                    print(f"  [{s.get('schedule_id', s.get('id', 'N/A'))}] Med ID: {s.get('medication_id', 'N/A')} | Freq: {s.get('frequency_type', 'N/A')}{freq_str} | Times: [{times}]")
                    
        elif choice == '2':
            print("\n-- Create Schedule --")
            med_id = input_prompt("Medication ID*: ", required=True)
            freq_type = input_prompt("Frequency Type (daily/weekly/interval/specific_days/as_needed)*: ", required=True)
            freq_value = input_prompt("Frequency Value (e.g., '2' for every 2 days, or blank): ")
            
            times_str = input_prompt("Reminder Times (HH:MM format, comma separated)*: ", required=True)
            try:
                # The API expects a list of time strings like ["08:00", "20:00"]
                times = [t.strip() for t in times_str.split(',')]
                
                data = {
                    'medication_id': med_id,
                    'frequency_type': freq_type,
                    'frequency_value': freq_value,
                    'reminder_times': times
                }
                result = make_request('POST', '/schedules/', data=data)
                if result:
                    print(f"  -> Schedule created!")
            except Exception as e:
                print(f"  -> Error parsing times: {e}")
                
        elif choice == '3':
            print("\n-- Update Schedule --")
            sched_id = input_prompt("Schedule ID*: ", required=True)
            med_id = input_prompt("Medication ID*: ", required=True)
            freq_type = input_prompt("New Frequency Type*: ", required=True)
            times_str = input_prompt("New Reminder Times (HH:MM format, comma separated)*: ", required=True)
            try:
                times = [t.strip() for t in times_str.split(',')]
                data = {
                    'medication_id': med_id,
                    'frequency_type': freq_type,
                    'reminder_times': times
                }
                if make_request('PUT', f'/schedules/{sched_id}/', data=data):
                    print("  -> Schedule updated.")
            except Exception as e:
                print(f"  -> Error parsing times: {e}")
                
        elif choice == '4':
            print("\n-- Remove Schedule --")
            sched_id = input_prompt("Schedule ID*: ", required=True)
            med_id = input_prompt("Medication ID (needed to purge future logs)*: ", required=True)
            
            if make_request('DELETE', f'/schedules/{sched_id}/', data={'medication_id': med_id}):
                print("  -> Schedule and future pending logs removed.")
                
        elif choice == '5':
            break

# ==========================================
#              DOSE LOG MENU
# ==========================================
def doselog_menu():
    while True:
        print_header("DOSE LOG MANAGEMENT (API CLIENT)")
        print("1. View Daily Planned Doses")
        print("2. Log Dose as Taken")
        print("3. Log Dose as Skipped")
        print("4. Add Ad-Hoc Dose")
        print("5. Reschedule Single Dose")
        print("6. Modify Single Dose Details")
        print("7. Revert/Update Dose Status")
        print("8. Delete Dose Log") # New option
        print("9. Generate Upcoming Schedule (Manual Trigger)") # Shifted
        print("10. Sweep Expired Doses") # Shifted
        print("11. Back to Main Menu") # Shifted
        
        choice = input("\nSelect an option (1-11): ") # Updated range
        
        if choice == '1':
            date_str = input_prompt("Date (YYYY-MM-DD)*: ", required=True)
            logs = make_request('GET', '/doses/daily/', params={'date': date_str})
            if logs is not None:
                if not logs:
                    print("  No logs found for this date.")
                for log in logs:
                    print(f"  [{log['log_id']}] {log['scheduled_datetime']} - {log['name']} - Strength: {log.get('scheduled_strength', 'N/A')}, Quantity: {log.get('scheduled_quantity', 'N/A')} - Status: {log['status']} - Notes: {log.get('notes', 'N/A')}")
                
        elif choice == '2':
            log_id = input_prompt("Log ID*: ", required=True)
            if make_request('POST', f'/doses/{log_id}/take/'):
                print("  -> Dose marked as taken. Inventory updated.")
                
        elif choice == '3':
            log_id = input_prompt("Log ID*: ", required=True)
            notes = input_prompt("Notes (optional): ")
            
            if make_request('POST', f'/doses/{log_id}/skip/', data={'notes': notes}):
                print("  -> Dose marked as skipped.")
                
        elif choice == '4':
            print("\n-- Log Ad-Hoc Dose --")
            med_id = input_prompt("Medication ID*: ", required=True)
            qty = input_prompt("Quantity Taken*: ", required=True, type_func=float)
            strength = input_prompt("Strength (leave blank for default): ")
            
            data = {'medication_id': med_id, 'quantity': qty}
            if strength:
                data['strength'] = strength
                
            if make_request('POST', '/doses/ad-hoc/', data=data):
                print("  -> Ad-Hoc dose logged. Inventory deducted.")
                
        elif choice == '5':
            log_id = input_prompt("Log ID*: ", required=True)
            dt_str = input_prompt("New Datetime (YYYY-MM-DD HH:MM:SS)*: ", required=True)
            # Need to format dt_str appropriately for the serializer, ISO 8601 is best
            try:
                dt_iso = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S").isoformat()
                if make_request('POST', f'/doses/{log_id}/reschedule/', data={'new_datetime': dt_iso}):
                    print("  -> Dose rescheduled successfully.")
            except ValueError:
                print("  -> Error: Invalid date format.")
                
        elif choice == '6':
            log_id = input_prompt("Log ID*: ", required=True)
            strength = input_prompt("New Strength*: ", required=True)
            qty = input_prompt("New Quantity*: ", required=True, type_func=float)
            
            if make_request('PATCH', f'/doses/{log_id}/', data={'new_strength': strength, 'new_quantity': qty}):
                print("  -> Dose details modified.")
                
        elif choice == '7':
            log_id = input_prompt("Log ID*: ", required=True)
            status = input_prompt("New Status (pending/taken/skipped/missed)*: ", required=True)
            qty = input_prompt("New Quantity (optional, hit enter to skip): ", type_func=float)
            
            data = {'new_status': status}
            if qty is not None:
                data['new_quantity'] = qty
                
            if make_request('PATCH', f'/doses/{log_id}/status/', data=data):
                print("  -> Dose status updated.")
                
        elif choice == '8': # New logic for deleting a dose log
            print("\n-- Delete Dose Log --")
            log_id = input_prompt("Log ID to delete*: ", required=True)
            confirm = input_prompt("Are you sure you want to permanently delete this dose log? (y/N): ", default="n")
            if confirm.lower() == 'y':
                if make_request('DELETE', f'/doses/{log_id}/'):
                    print("  -> Dose log permanently deleted.")
            else:
                print("  -> Dose log deletion cancelled.")
        elif choice == '9': # Shifted from 8 to 9
            med_id = input_prompt("Medication ID*: ", required=True)
            days = input_prompt("Days Ahead (default 30): ", default=30, type_func=int)
            
            if make_request('POST', f'/medications/{med_id}/generate-schedule/', data={'days_ahead': days}):
                print(f"  -> Successfully triggered generation for {days} days of logs.")
                
        elif choice == '10': # Shifted from 9 to 10
            if make_request('POST', '/doses/sweep-expired/'):
                print("  -> Expired pending doses swept and marked as 'missed'.")

        elif choice == '11': # Shifted from 10 to 11
            break

def main():
    while True:
        print_header("API SERVICE CLIENT CONSOLE")
        print("Make sure your Django server is running locally on port 8000")
        print("1. Medication Management")
        print("2. Schedule Management")
        print("3. Dose Log Management")
        print("4. Exit")
        
        choice = input("\nSelect a module to test (1-4): ")
        
        if choice == '1': medication_menu()
        elif choice == '2': schedule_menu()
        elif choice == '3': doselog_menu()
        elif choice == '4':
            print("\nExiting. Goodbye!\n")
            break
        else: print("  -> Invalid choice.")

if __name__ == "__main__":
    main()