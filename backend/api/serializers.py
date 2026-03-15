from rest_framework import serializers

class MedicationSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    medication_type = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    strength = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    condition_treated = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    instructions = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    amount_left = serializers.FloatField(min_value=0, default=0)
    refill_threshold = serializers.FloatField(min_value=0, default=0)

class MedicationUpdateDetailsSerializer(serializers.Serializer):
    strength = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    condition_treated = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    instructions = serializers.CharField(required=False, allow_blank=True, allow_null=True)

class MedicationUpgradeSerializer(serializers.Serializer):
    new_strength = serializers.CharField(max_length=50)

class RefillSerializer(serializers.Serializer):
    amount_added = serializers.FloatField(min_value=0.01)

class MedicationGenerateScheduleSerializer(serializers.Serializer):
    days_ahead = serializers.IntegerField(min_value=1, default=30)

class ScheduleSerializer(serializers.Serializer):
    medication_id = serializers.UUIDField()
    frequency_type = serializers.ChoiceField(choices=['daily', 'weekly', 'interval', 'specific_days', 'as_needed'])
    frequency_value = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    reminder_times = serializers.ListField(child=serializers.TimeField(), required=False, default=list)

class ScheduleDeleteSerializer(serializers.Serializer):
    medication_id = serializers.UUIDField()

class DailyDoseQuerySerializer(serializers.Serializer):
    date = serializers.DateField(input_formats=['%Y-%m-%d'])

class DoseLogSkipSerializer(serializers.Serializer):
    notes = serializers.CharField(required=False, allow_blank=True, allow_null=True)

class DoseLogRescheduleSerializer(serializers.Serializer):
    new_datetime = serializers.DateTimeField()

class DoseLogModifySerializer(serializers.Serializer):
    new_strength = serializers.CharField(max_length=50)
    new_quantity = serializers.FloatField(min_value=0)

class AdHocDoseSerializer(serializers.Serializer):
    medication_id = serializers.UUIDField()
    quantity = serializers.FloatField(min_value=0.01)
    strength = serializers.CharField(required=False, allow_blank=True, allow_null=True)

class DoseStatusUpdateSerializer(serializers.Serializer):
    new_status = serializers.ChoiceField(choices=['pending', 'taken', 'skipped', 'missed'])
    new_quantity = serializers.FloatField(min_value=0, required=False, allow_null=True)