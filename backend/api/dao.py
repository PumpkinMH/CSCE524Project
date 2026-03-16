from django.db.models import F
from .models import Medication, Schedule, DoseLog

class MedicationDAO:

    @staticmethod
    def get_all():
        return list(Medication.objects.all().order_by('name').values())

    @staticmethod
    def get_by_id(medication_id):
        return Medication.objects.filter(pk=medication_id).values().first()

    @staticmethod
    def update(medication_id, amount_left, is_active):
        """Example update focusing on inventory and status."""
        Medication.objects.filter(pk=medication_id).update(
            amount_left=amount_left, 
            is_active=is_active
        )
            
    @staticmethod
    def delete(medication_id):
        Medication.objects.filter(pk=medication_id).delete()
    
    @staticmethod
    def create(name, med_type, strength, condition_treated, instructions, amount_left, refill_threshold, previous_medication_id=None, is_active=True):
        med = Medication.objects.create(
            name=name,
            medication_type=med_type,
            strength=strength,
            condition_treated=condition_treated,
            instructions=instructions,
            amount_left=amount_left,
            refill_threshold=refill_threshold,
            previous_medication_id=previous_medication_id,
            is_active=is_active
        )
        return med.medication_id

    @staticmethod
    def update_details(medication_id, strength, condition_treated, instructions):
        Medication.objects.filter(pk=medication_id).update(
            strength=strength, 
            condition_treated=condition_treated, 
            instructions=instructions
        )


class ScheduleDAO:

    @staticmethod
    def get_all():
        return list(Schedule.objects.all().values())

    @staticmethod
    def create(medication_id, frequency_type, frequency_value, reminder_times):
        sched = Schedule.objects.create(
            medication_id=medication_id,
            frequency_type=frequency_type,
            frequency_value=frequency_value,
            reminder_times=reminder_times
        )
        return sched.schedule_id

    @staticmethod
    def get_for_medication(medication_id):
        return list(Schedule.objects.filter(medication_id=medication_id).values())

    @staticmethod
    def update(schedule_id, frequency_type, reminder_times):
        Schedule.objects.filter(pk=schedule_id).update(
            frequency_type=frequency_type, 
            reminder_times=reminder_times
        )

    @staticmethod
    def delete(schedule_id):
        Schedule.objects.filter(pk=schedule_id).delete()


class DoseLogDAO:

    @staticmethod
    def create(medication_id, scheduled_datetime, scheduled_strength, scheduled_quantity):
        log = DoseLog.objects.create(
            medication_id=medication_id,
            scheduled_datetime=scheduled_datetime,
            scheduled_strength=scheduled_strength,
            scheduled_quantity=scheduled_quantity,
            status='pending'
        )
        return log.log_id

    @staticmethod
    def get_pending_logs():
        """A JOIN query to get pending doses along with the medication name."""
        return list(DoseLog.objects.select_related('medication')
            .filter(status='pending')
            .order_by('scheduled_datetime')
            .annotate(name=F('medication__name'))
            .values('log_id', 'name', 'scheduled_datetime', 'scheduled_strength', 'scheduled_quantity', 'notes'))

    @staticmethod
    def get_logs_for_date(target_date):
        """Fetches all dose logs for a specific date, joining the medication name."""
        return list(DoseLog.objects.select_related('medication')
            .filter(scheduled_datetime__date=target_date)
            .order_by('scheduled_datetime')
            .annotate(name=F('medication__name'))
            .values('log_id', 'name', 'scheduled_datetime', 'status', 'scheduled_strength', 'scheduled_quantity', 'notes'))

    @staticmethod
    def mark_as_taken(log_id, actual_datetime_taken, actual_strength, actual_quantity):
        DoseLog.objects.filter(pk=log_id).update(
            status='taken',
            actual_datetime_taken=actual_datetime_taken,
            actual_strength_taken=actual_strength,
            actual_quantity_taken=actual_quantity
        )

    @staticmethod
    def delete(log_id):
        DoseLog.objects.filter(pk=log_id).delete()

    @staticmethod
    def get_by_id(log_id):
        return DoseLog.objects.filter(pk=log_id).values().first()

    @staticmethod
    def create_ad_hoc(medication_id, actual_datetime_taken, scheduled_strength, actual_quantity):
        """Creates a dose log that is instantly marked as taken."""
        log = DoseLog.objects.create(
            medication_id=medication_id,
            scheduled_datetime=actual_datetime_taken,
            actual_datetime_taken=actual_datetime_taken,
            scheduled_strength=scheduled_strength,
            actual_strength_taken=scheduled_strength,
            scheduled_quantity=actual_quantity,
            actual_quantity_taken=actual_quantity,
            status='taken'
        )
        return log.log_id

    @staticmethod
    def update_log_state(log_id, status, actual_datetime_taken=None, actual_quantity_taken=None):
        """A flexible update method for status changes (skipped, missed, taken, or reverting to pending)."""
        DoseLog.objects.filter(pk=log_id).update(
            status=status,
            actual_datetime_taken=actual_datetime_taken,
            actual_quantity_taken=actual_quantity_taken
        )

    @staticmethod
    def delete_future_pending(medication_id, current_timestamp):
        """Deletes only pending logs that occur after the given timestamp."""
        DoseLog.objects.filter(
            medication_id=medication_id,
            status='pending',
            scheduled_datetime__gt=current_timestamp
        ).delete()

    @staticmethod
    def update_scheduled_datetime(log_id, new_datetime):
        """Updates the scheduled_datetime for a single dose log."""
        DoseLog.objects.filter(pk=log_id).update(scheduled_datetime=new_datetime)

    @staticmethod
    def update_dose_details(log_id, new_strength, new_quantity):
        """Updates the scheduled strength and quantity for a single dose log."""
        DoseLog.objects.filter(pk=log_id).update(
            scheduled_strength=new_strength, 
            scheduled_quantity=new_quantity
        )

    @staticmethod
    def update_log_notes(log_id, notes):
        """Updates the notes for a single dose log."""
        DoseLog.objects.filter(pk=log_id).update(notes=notes)