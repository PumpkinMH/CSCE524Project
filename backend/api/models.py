from django.db import models
from django.contrib.postgres.fields import ArrayField

# class User(models.Model):
#     user_id = models.UUIDField(primary_key=True)
#     email = models.CharField(unique=True, max_length=255)
#     password_hash = models.CharField(max_length=255)
#     first_name = models.CharField(max_length=100, blank=True, null=True)
#     timezone = models.CharField(max_length=100, blank=True, null=True)
#     created_at = models.DateTimeField(blank=True, null=True)

#     class Meta:
#         managed = False # Tells Django the table already exists
#         db_table = 'users'

# class Medication(models.Model):
#     medication_id = models.UUIDField(primary_key=True)
#     user = models.ForeignKey(User, models.DO_NOTHING)
#     previous_medication = models.ForeignKey('self', models.DO_NOTHING, blank=True, null=True)
#     name = models.CharField(max_length=255)
#     medication_type = models.CharField(max_length=50, blank=True, null=True)
#     strength = models.CharField(max_length=50, blank=True, null=True)
#     condition_treated = models.CharField(max_length=255, blank=True, null=True)
#     instructions = models.TextField(blank=True, null=True)
#     amount_left = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
#     refill_threshold = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
#     is_active = models.BooleanField(blank=True, null=True)
#     treatment_duration_days = models.IntegerField(blank=True, null=True)

#     class Meta:
#         managed = False
#         db_table = 'medications'

# class Schedule(models.Model):
#     schedule_id = models.UUIDField(primary_key=True)
#     medication = models.ForeignKey(Medication, models.DO_NOTHING)
#     frequency_type = models.CharField(max_length=50, blank=True, null=True)
#     frequency_value = models.CharField(max_length=255, blank=True, null=True)
#     reminder_times = ArrayField(models.TimeField(), blank=True, null=True)

#     class Meta:
#         managed = False
#         db_table = 'schedules'

# class DoseLog(models.Model):
#     log_id = models.UUIDField(primary_key=True)
#     medication = models.ForeignKey(Medication, models.DO_NOTHING)
#     scheduled_datetime = models.DateTimeField()
#     actual_datetime_taken = models.DateTimeField(blank=True, null=True)
#     scheduled_strength = models.CharField(max_length=50, blank=True, null=True)
#     actual_strength_taken = models.CharField(max_length=50, blank=True, null=True)
#     scheduled_quantity = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
#     actual_quantity_taken = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
#     status = models.CharField(max_length=50, blank=True, null=True)
#     notes = models.TextField(blank=True, null=True)

#     class Meta:
#         managed = False
#         db_table = 'dose_logs'
