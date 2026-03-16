import uuid
from django.db import models
from django.contrib.postgres.fields import ArrayField


class Medication(models.Model):
    MEDICATION_TYPES = [
        ('tablet', 'Tablet'),
        ('capsule', 'Capsule'),
        ('liquid', 'Liquid'),
        ('injection', 'Injection'),
        ('oil', 'Oil'),
        ('topical', 'Topical'),
        ('other', 'Other'),
    ]

    medication_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    previous_medication = models.ForeignKey('self', on_delete=models.SET_NULL, db_column='previous_medication_id', blank=True, null=True)
    name = models.CharField(max_length=255)
    medication_type = models.CharField(max_length=50, choices=MEDICATION_TYPES, blank=True, null=True)
    strength = models.CharField(max_length=50, blank=True, null=True)
    condition_treated = models.CharField(max_length=255, blank=True, null=True)
    instructions = models.TextField(blank=True, null=True)
    amount_left = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    refill_threshold = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    treatment_duration_days = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'medications'


class Schedule(models.Model):
    FREQUENCY_TYPES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('interval', 'Interval'),
        ('specific_days', 'Specific Days'),
        ('as_needed', 'As Needed'),
    ]

    schedule_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    medication = models.ForeignKey(Medication, on_delete=models.CASCADE, db_column='medication_id')
    frequency_type = models.CharField(max_length=50, choices=FREQUENCY_TYPES, blank=True, null=True)
    frequency_value = models.CharField(max_length=255, blank=True, null=True)
    reminder_times = ArrayField(models.TimeField(), blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'schedules'


class DoseLog(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('taken', 'Taken'),
        ('skipped', 'Skipped'),
        ('missed', 'Missed'),
    ]

    log_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    medication = models.ForeignKey(Medication, on_delete=models.CASCADE, db_column='medication_id')
    scheduled_datetime = models.DateTimeField()
    actual_datetime_taken = models.DateTimeField(blank=True, null=True)
    scheduled_strength = models.CharField(max_length=50, blank=True, null=True)
    actual_strength_taken = models.CharField(max_length=50, blank=True, null=True)
    scheduled_quantity = models.DecimalField(max_digits=10, decimal_places=2, default=1)
    actual_quantity_taken = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'dose_logs'
