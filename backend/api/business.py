
"""
Business Logic Layer for the MedTracker REST API.

This layer orchestrates the application's business rules and acts as a mediator
between the presentation layer (views) and the data access layer (DAO). It is
designed to be completely independent of the web framework (Django) and the
database implementation.
"""

from datetime import datetime, timedelta, time
from .dao import MedicationDAO, ScheduleDAO, DoseLogDAO
from decimal import Decimal

class MedicationBusiness:
    """Handles business logic related to medications."""

    @staticmethod
    def add_new_medication(medication_data: dict) -> dict:
        """
        Validates and adds a new medication.
        
        Args:
            medication_data: A dictionary containing medication details.
        
        Returns:
            The created medication object.
        """
        if not medication_data.get('name'):
            raise ValueError("Medication name cannot be empty.")
        
        # Convert to Decimal for validation and consistency
        if Decimal(str(medication_data.get('amount_left', 0))) < 0 or \
           Decimal(str(medication_data.get('refill_threshold', 0))) < 0:
            raise ValueError("Amounts and thresholds must be non-negative.")

        med_id = MedicationDAO.create(
            name=medication_data['name'],
            med_type=medication_data.get('medication_type'),
            strength=medication_data.get('strength'),
            condition_treated=medication_data.get('condition_treated'),
            instructions=medication_data.get('instructions'),
            amount_left=medication_data.get('amount_left', 0),
            refill_threshold=medication_data.get('refill_threshold', 0)
        )
        return MedicationDAO.get_by_id(med_id)

    @staticmethod
    def update_medication_details(medication_id: str, details_data: dict):
        """Updates non-critical details of a medication."""
        MedicationDAO.update_details(
            medication_id=medication_id,
            strength=details_data.get('strength'),
            condition_treated=details_data.get('condition_treated'),
            instructions=details_data.get('instructions')
        )

    @staticmethod
    def upgrade_prescription(medication_id: str, new_strength: str) -> dict:
        """
        Upgrades a prescription, creating a new active record and archiving the old one.
        
        Returns:
            The new medication object.
        """
        old_med = MedicationDAO.get_by_id(medication_id)
        if not old_med:
            raise ValueError("Medication not found.")

        # 1. Soft-delete the current medication
        MedicationDAO.update(medication_id, old_med['amount_left'], is_active=False)

        # 2. Create a new medication row linked to the old one
        new_med_id = MedicationDAO.create(
            name=old_med['name'],
            med_type=old_med['medication_type'],
            strength=new_strength,
            condition_treated=old_med['condition_treated'],
            instructions=old_med['instructions'],
            amount_left=old_med['amount_left'],
            refill_threshold=old_med['refill_threshold'],
            previous_medication_id=medication_id,
            is_active=True
        )

        # 3. Delete future pending logs for the old medication
        DoseLogDAO.delete_future_pending(medication_id, datetime.now())

        # 4. Trigger log generation for the new medication
        DoseLogBusiness.generate_upcoming_schedule(new_med_id)
        
        return MedicationDAO.get_by_id(new_med_id)

    @staticmethod
    def archive_medication(medication_id: str):
        """Soft-deletes a medication and removes its future scheduled doses."""
        med = MedicationDAO.get_by_id(medication_id)
        if med:
            MedicationDAO.update(medication_id, med['amount_left'], is_active=False)
            DoseLogDAO.delete_future_pending(medication_id, datetime.now())

    @staticmethod
    def purge_medication(medication_id: str):
        """Permanently deletes a medication and all associated data."""
        MedicationDAO.delete(medication_id)

    @staticmethod
    def get_active_inventory() -> list:
        """Fetches all active medications."""
        all_meds = MedicationDAO.get_all()
        return [med for med in all_meds if med['is_active']]

    @staticmethod
    def get_refill_alerts() -> list:
        """Finds active medications that are low on stock."""
        active_meds = MedicationBusiness.get_active_inventory()
        return [
            med for med in active_meds 
            if med['amount_left'] is not None and med['refill_threshold'] is not None and med['amount_left'] <= med['refill_threshold']
        ]

    @staticmethod
    def refill_medication(medication_id: str, amount_added: float):
        """Adds a specified amount to a medication's inventory."""
        if amount_added <= 0:
            raise ValueError("Amount to add must be positive.")
        med = MedicationDAO.get_by_id(medication_id)
        if med:
            # Ensure all arithmetic is done with Decimal
            current_amount = med['amount_left'] if med['amount_left'] is not None else Decimal('0')
            new_amount = current_amount + Decimal(str(amount_added))
            MedicationDAO.update(medication_id, new_amount, med['is_active'])


class ScheduleBusiness:
    """Handles business logic for medication schedules."""

    ALLOWED_FREQ_TYPES = {'daily', 'weekly', 'interval', 'specific_days', 'as_needed'}

    @staticmethod
    def create_schedule(schedule_data: dict) -> dict:
        """
        Creates a new schedule and generates its initial dose logs.
        """
        freq_type = schedule_data.get('frequency_type')
        if freq_type not in ScheduleBusiness.ALLOWED_FREQ_TYPES:
            raise ValueError(f"Invalid frequency_type: {freq_type}")

        med_id = schedule_data['medication_id']
        schedule_id = ScheduleDAO.create(
            medication_id=med_id,
            frequency_type=freq_type,
            frequency_value=schedule_data.get('frequency_value'),
            reminder_times=schedule_data.get('reminder_times', [])
        )
        
        # Immediately generate upcoming logs
        DoseLogBusiness.generate_upcoming_schedule(med_id)

        # DAO should be updated to return the created object or have a get_by_id
        return {'schedule_id': schedule_id, **schedule_data}


    @staticmethod
    def update_schedule(schedule_id: str, schedule_data: dict):
        """Updates an existing schedule."""
        # This assumes we might also want to regenerate logs after an update.
        # For now, it just updates the schedule itself.
        ScheduleDAO.update(
            schedule_id,
            schedule_data['frequency_type'],
            schedule_data['reminder_times']
        )
    
    @staticmethod
    def remove_schedule(schedule_id: str, medication_id: str):
        """Deletes a schedule and its future pending logs."""
        ScheduleDAO.delete(schedule_id)
        DoseLogDAO.delete_future_pending(medication_id, datetime.now())


class DoseLogBusiness:
    """Handles business logic for tracking and managing medication doses."""

    @staticmethod
    def get_daily_planned_doses(target_date: str) -> list:
        """Fetches all dose logs for a specific date, sorted chronologically."""
        return DoseLogDAO.get_logs_for_date(target_date)

    @staticmethod
    def log_dose_as_taken(log_id: str):
        """
        Marks a dose as taken and deducts the quantity from the medication inventory.
        """
        log = DoseLogDAO.get_by_id(log_id)
        if not log:
            raise ValueError("Log not found.")
        if log['status'] == 'taken':
            return # Prevent double-dipping

        med = MedicationDAO.get_by_id(log['medication_id'])
        if not med:
            raise ValueError("Associated medication not found.")

        # Ensure quantity_taken is Decimal for calculations
        quantity_taken_decimal = Decimal(str(log['scheduled_quantity']))

        # Update log status
        DoseLogDAO.update_log_state(
            log_id, 
            'taken',
            actual_datetime_taken=datetime.now(),
            actual_quantity_taken=quantity_taken
        )

        # Update inventory, flooring at 0
        current_amount = med['amount_left'] if med['amount_left'] is not None else Decimal('0')
        new_amount = max(Decimal('0'), current_amount - quantity_taken_decimal)
        MedicationDAO.update(med['medication_id'], new_amount, med['is_active'])

    @staticmethod
    def log_dose_as_skipped(log_id: str, notes: str = None):
        """Marks a dose as skipped without changing inventory."""
        DoseLogDAO.update_log_state(log_id, 'skipped')
        if notes:
            DoseLogDAO.update_log_notes(log_id, notes)

    @staticmethod
    def reschedule_single_dose(log_id: str, new_datetime: str):
        """Changes the scheduled_datetime for a single pending dose."""
        DoseLogDAO.update_scheduled_datetime(log_id, new_datetime)

    @staticmethod
    def modify_single_dose(log_id: str, new_strength: str, new_quantity: float):
        """Changes the strength and quantity for a single pending dose."""
        DoseLogDAO.update_dose_details(log_id, new_strength, new_quantity)

    @staticmethod
    def add_ad_hoc_dose(medication_id: str, quantity: float, strength: str = None) -> dict:
        """Instantly logs a dose as taken and deducts from inventory.
        Quantity is expected as float from serializer, converted to Decimal for calculations."""
        med = MedicationDAO.get_by_id(medication_id)
        if not med:
            raise ValueError("Medication not found.")

        # Use medication's default strength if not provided
        actual_strength = strength if strength else med['strength']

        # Convert float quantity to Decimal for precise storage and calculation
        quantity_decimal = Decimal(str(quantity))

        log_id = DoseLogDAO.create_ad_hoc(
            medication_id,
            datetime.now(),
            actual_strength,
            quantity_decimal
        )

        # Deduct from inventory, flooring at 0
        current_amount = med['amount_left'] if med['amount_left'] is not None else Decimal('0')
        new_amount = max(Decimal('0'), current_amount - quantity_decimal)
        MedicationDAO.update(medication_id, new_amount, med['is_active'])

        # Return the newly created object, which is RESTful best practice.
        return DoseLogDAO.get_by_id(log_id)

    @staticmethod
    def generate_upcoming_schedule(medication_id: str, days_ahead: int = 30):
        """
        Creates pending dose logs for a medication based on its active schedules.
        """
        schedules = ScheduleDAO.get_for_medication(medication_id)
        med = MedicationDAO.get_by_id(medication_id)
        if not med or not med['is_active']:
            return

        today = datetime.now().date()
        
        for schedule in schedules:
            # Check treatment duration if it exists
            if med.get('treatment_duration_days'):
                # This assumes a start date, which is not in the schema.
                # A more robust implementation would need a `treatment_start_date`.
                # For now, we'll just use a placeholder for the logic.
                pass
            
            for i in range(days_ahead):
                target_date = today + timedelta(days=i)
                
                # Logic for different frequency types
                if schedule['frequency_type'] == 'daily':
                    for t in schedule['reminder_times']:
                        dt = datetime.combine(target_date, t)
                        DoseLogDAO.create(medication_id, dt, med['strength'], 1) # Assuming quantity 1
    
    @staticmethod
    def sweep_expired_doses():
        """Finds pending doses older than 24 hours and marks them as 'missed'."""
        pending_logs = DoseLogDAO.get_pending_logs()
        yesterday = datetime.now() - timedelta(hours=24)
        for log in pending_logs:
            if log['scheduled_datetime'].replace(tzinfo=None) < yesterday:
                DoseLogDAO.update_log_state(log['log_id'], 'missed')

    @staticmethod
    def revert_or_update_dose_status(log_id: str, new_status: str, new_quantity: float = None):
        """
        Handles state transitions for a dose, adjusting inventory accordingly.
        """
        log = DoseLogDAO.get_by_id(log_id)
        if not log:
            raise ValueError("Log not found.")
        
        # Ensure all quantities are Decimals for consistent arithmetic
        old_status = log['status']
        old_quantity_decimal = Decimal(str(log.get('actual_quantity_taken', 0)))
        new_quantity_decimal = Decimal(str(new_quantity)) if new_quantity is not None else None
        scheduled_quantity_decimal = Decimal(str(log['scheduled_quantity']))
        
        # No change, no action
        if old_status == new_status and (new_quantity_decimal is None or old_quantity_decimal == new_quantity_decimal):
            return

        med = MedicationDAO.get_by_id(log['medication_id'])
        if not med:
            raise ValueError("Medication not found.")

        inventory_change = Decimal('0')
        current_med_amount = med['amount_left'] if med['amount_left'] is not None else Decimal('0')

        # Case 1: Reverting a 'taken' dose
        if old_status == 'taken' and new_status in ('pending', 'skipped'):
            inventory_change = old_quantity_decimal # Add back to inventory
            DoseLogDAO.update_log_state(log_id, new_status, actual_quantity_taken=None, actual_datetime_taken=None)

        # Case 2: Changing a non-taken dose to 'taken'
        elif old_status in ('pending', 'skipped', 'missed') and new_status == 'taken':
            quantity_to_log = new_quantity_decimal if new_quantity_decimal is not None else scheduled_quantity_decimal
            inventory_change = -quantity_to_log # Deduct from inventory (negative value)
            DoseLogDAO.update_log_state(log_id, new_status, actual_quantity_taken=quantity_to_log, actual_datetime_taken=datetime.now()) # Pass Decimal

        # Case 3: Modifying an already 'taken' dose's quantity
        elif old_status == 'taken' and new_status == 'taken' and new_quantity_decimal is not None:
            inventory_change = old_quantity_decimal - new_quantity_decimal # Adjust by the difference
            DoseLogDAO.update_log_state(log_id, new_status, actual_quantity_taken=new_quantity_decimal, actual_datetime_taken=log['actual_datetime_taken']) # Pass Decimal

        # Apply inventory change
        if inventory_change != Decimal('0'):
            new_amount = current_med_amount + inventory_change
            # Ensure inventory doesn't go negative on a deduction
            if inventory_change < Decimal('0'):
                new_amount = max(Decimal('0'), new_amount)
            MedicationDAO.update(med['medication_id'], new_amount, med['is_active'])
