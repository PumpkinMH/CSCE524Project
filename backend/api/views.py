from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .business import MedicationBusiness, ScheduleBusiness, DoseLogBusiness
from . import serializers
import uuid
from datetime import datetime
from django.utils.decorators import method_decorator

def _api_error_handler(func):
    """Decorator for APIView dispatch method to handle common exceptions."""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            # In a real app, you'd want to log this exception.
            # import logging
            # logging.exception("An unexpected error occurred")
            return Response({'error': 'An unexpected server error occurred.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return wrapper

# === Medication Views ===

@method_decorator(_api_error_handler, name='dispatch')
class MedicationListCreateView(APIView):
    """
    List active medications or create a new one.
    GET: /api/medications/
    POST: /api/medications/
    """
    def get(self, request):
        meds = MedicationBusiness.get_active_inventory()
        return Response(meds, status=status.HTTP_200_OK)

    def post(self, request):
        medication_data = request.data
        new_med = MedicationBusiness.add_new_medication(medication_data)
        serializer = serializers.MedicationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        new_med = MedicationBusiness.add_new_medication(serializer.validated_data)
        return Response(new_med, status=status.HTTP_201_CREATED)

@method_decorator(_api_error_handler, name='dispatch')
class MedicationDetailView(APIView):
    """
    Purge a medication.
    DELETE: /api/medications/<uuid:medication_id>/
    """
    def delete(self, request, medication_id: uuid.UUID):
        MedicationBusiness.purge_medication(str(medication_id))
        return Response(status=status.HTTP_204_NO_CONTENT)

@method_decorator(_api_error_handler, name='dispatch')
class MedicationDetailsUpdateView(APIView):
    """
    Update non-critical details of a medication.
    PATCH: /api/medications/<uuid:medication_id>/details/
    """
    def patch(self, request, medication_id: uuid.UUID):
        MedicationBusiness.update_medication_details(str(medication_id), request.data)
        serializer = serializers.MedicationUpdateDetailsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        MedicationBusiness.update_medication_details(str(medication_id), serializer.validated_data)
        return Response({'status': 'details updated'}, status=status.HTTP_200_OK)

@method_decorator(_api_error_handler, name='dispatch')
class MedicationUpgradeView(APIView):
    """
    Upgrade a prescription to a new strength.
    POST: /api/medications/<uuid:medication_id>/upgrade/
    """
    def post(self, request, medication_id: uuid.UUID):
        new_strength = request.data.get('new_strength')
        if not new_strength:
            return Response({'error': 'new_strength is required'}, status=status.HTTP_400_BAD_REQUEST)
        new_med = MedicationBusiness.upgrade_prescription(str(medication_id), new_strength)
        serializer = serializers.MedicationUpgradeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        new_med = MedicationBusiness.upgrade_prescription(str(medication_id), serializer.validated_data['new_strength'])
        return Response(new_med, status=status.HTTP_200_OK)

@method_decorator(_api_error_handler, name='dispatch')
class MedicationArchiveActionView(APIView):
    """
    Archive a medication (soft delete).
    POST: /api/medications/<uuid:medication_id>/archive/
    """
    def post(self, request, medication_id: uuid.UUID):
        MedicationBusiness.archive_medication(str(medication_id))
        return Response({'status': 'medication archived'}, status=status.HTTP_200_OK)

@method_decorator(_api_error_handler, name='dispatch')
class MedicationRefillAlertsView(APIView):
    """
    Get medications that need a refill.
    GET: /api/medications/refill-alerts/
    """
    def get(self, request):
        alerts = MedicationBusiness.get_refill_alerts()
        return Response(alerts, status=status.HTTP_200_OK)

@method_decorator(_api_error_handler, name='dispatch')
class MedicationRefillView(APIView):
    """
    Refill a medication.
    POST: /api/medications/<uuid:medication_id>/refill/
    """
    def post(self, request, medication_id: uuid.UUID):
        amount_added = request.data.get('amount_added')
        if amount_added is None:
            return Response({'error': 'amount_added is required'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            amount_added = float(amount_added)
        except (ValueError, TypeError):
            return Response({'error': 'amount_added must be a number'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = serializers.RefillSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        MedicationBusiness.refill_medication(str(medication_id), amount_added)
        MedicationBusiness.refill_medication(str(medication_id), serializer.validated_data['amount_added'])
        return Response({'status': 'medication refilled'}, status=status.HTTP_200_OK)

@method_decorator(_api_error_handler, name='dispatch')
class MedicationGenerateScheduleView(APIView):
    """
    Trigger schedule generation for a medication.
    POST: /api/medications/<uuid:medication_id>/generate-schedule/
    """
    def post(self, request, medication_id: uuid.UUID):
        days_ahead = request.data.get('days_ahead', 30)
        DoseLogBusiness.generate_upcoming_schedule(str(medication_id), days_ahead)
        return Response({'status': 'schedule generation triggered'}, status=status.HTTP_202_ACCEPTED)

# === Schedule Views ===

@method_decorator(_api_error_handler, name='dispatch')
class ScheduleListCreateView(APIView):
    """
    Create a new schedule.
    POST: /api/schedules/
    """
    def post(self, request):
        new_schedule = ScheduleBusiness.create_schedule(request.data)
        serializer = serializers.ScheduleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        new_schedule = ScheduleBusiness.create_schedule(serializer.validated_data)
        return Response(new_schedule, status=status.HTTP_201_CREATED)

@method_decorator(_api_error_handler, name='dispatch')
class ScheduleDetailView(APIView):
    """
    Update or delete a schedule.
    PUT: /api/schedules/<uuid:schedule_id>/
    DELETE: /api/schedules/<uuid:schedule_id>/
    """
    def put(self, request, schedule_id: uuid.UUID):
        ScheduleBusiness.update_schedule(str(schedule_id), request.data)
        return Response({'status': 'schedule updated'}, status=status.HTTP_200_OK)

    def delete(self, request, schedule_id: uuid.UUID):
        medication_id = request.data.get('medication_id')
        if not medication_id:
            return Response({'error': 'medication_id is required to delete future logs'}, status=status.HTTP_400_BAD_REQUEST)
        ScheduleBusiness.remove_schedule(str(schedule_id), str(medication_id))
        return Response(status=status.HTTP_204_NO_CONTENT)

# === Dose Log Views ===

@method_decorator(_api_error_handler, name='dispatch')
class DailyDoseView(APIView):
    """
    Get all dose logs for a specific date.
    GET: /api/doses/daily/?date=YYYY-MM-DD
    """
    def get(self, request):
        target_date_str = request.query_params.get('date')
        if not target_date_str:
            return Response({'error': 'date query parameter is required (YYYY-MM-DD)'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            datetime.strptime(target_date_str, '%Y-%m-%d')
        except ValueError:
            return Response({'error': 'Invalid date format. Use YYYY-MM-DD.'}, status=status.HTTP_400_BAD_REQUEST)
            
        doses = DoseLogBusiness.get_daily_planned_doses(target_date_str)
        serializer = serializers.DailyDoseQuerySerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        
        doses = DoseLogBusiness.get_daily_planned_doses(str(serializer.validated_data['date']))
        return Response(doses, status=status.HTTP_200_OK)

@method_decorator(_api_error_handler, name='dispatch')
class DoseLogTakeView(APIView):
    """
    Mark a dose as taken.
    POST: /api/doses/<uuid:log_id>/take/
    """
    def post(self, request, log_id: uuid.UUID):
        DoseLogBusiness.log_dose_as_taken(str(log_id))
        return Response({'status': 'dose marked as taken'}, status=status.HTTP_200_OK)

@method_decorator(_api_error_handler, name='dispatch')
class DoseLogSkipView(APIView):
    """
    Mark a dose as skipped.
    POST: /api/doses/<uuid:log_id>/skip/
    """
    def post(self, request, log_id: uuid.UUID):
        notes = request.data.get('notes')
        DoseLogBusiness.log_dose_as_skipped(str(log_id), notes)
        return Response({'status': 'dose marked as skipped'}, status=status.HTTP_200_OK)

@method_decorator(_api_error_handler, name='dispatch')
class DoseLogRescheduleView(APIView):
    """
    Reschedule a single dose.
    POST: /api/doses/<uuid:log_id>/reschedule/
    """
    def post(self, request, log_id: uuid.UUID):
        new_datetime = request.data.get('new_datetime')
        if not new_datetime:
            return Response({'error': 'new_datetime is required'}, status=status.HTTP_400_BAD_REQUEST)
        DoseLogBusiness.reschedule_single_dose(str(log_id), new_datetime)
        return Response({'status': 'dose rescheduled'}, status=status.HTTP_200_OK)

@method_decorator(_api_error_handler, name='dispatch')
class DoseLogModifyView(APIView):
    """
    Modify a single dose's details.
    PATCH: /api/doses/<uuid:log_id>/
    """
    def patch(self, request, log_id: uuid.UUID):
        new_strength = request.data.get('new_strength')
        new_quantity = request.data.get('new_quantity')
        if new_strength is None or new_quantity is None:
            return Response({'error': 'new_strength and new_quantity are required'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            new_quantity = float(new_quantity)
        except (ValueError, TypeError):
            return Response({'error': 'new_quantity must be a number'}, status=status.HTTP_400_BAD_REQUEST)

        DoseLogBusiness.modify_single_dose(str(log_id), new_strength, new_quantity)
        return Response({'status': 'dose details modified'}, status=status.HTTP_200_OK)

@method_decorator(_api_error_handler, name='dispatch')
class AdHocDoseCreateView(APIView):
    """
    Log an ad-hoc dose.
    POST: /api/doses/ad-hoc/
    """
    def post(self, request):
        medication_id = request.data.get('medication_id')
        quantity = request.data.get('quantity')
        strength = request.data.get('strength') # Optional

        if not medication_id or quantity is None:
            return Response({'error': 'medication_id and quantity are required'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            quantity = float(quantity)
        except (ValueError, TypeError):
            return Response({'error': 'quantity must be a number'}, status=status.HTTP_400_BAD_REQUEST)

        DoseLogBusiness.add_ad_hoc_dose(str(medication_id), quantity, strength)
        return Response({'status': 'ad-hoc dose created'}, status=status.HTTP_201_CREATED)

@method_decorator(_api_error_handler, name='dispatch')
class DoseSweepExpiredView(APIView):
    """
    Sweep for and mark expired doses as 'missed'.
    POST: /api/doses/sweep-expired/
    """
    def post(self, request):
        DoseLogBusiness.sweep_expired_doses()
        return Response({'status': 'sweep complete'}, status=status.HTTP_200_OK)

@method_decorator(_api_error_handler, name='dispatch')
class DoseStatusUpdateView(APIView):
    """
    Revert or update a dose's status.
    PATCH: /api/doses/<uuid:log_id>/status/
    """
    def patch(self, request, log_id: uuid.UUID):
        new_status = request.data.get('new_status')
        new_quantity = request.data.get('new_quantity') # Optional

        if not new_status:
            return Response({'error': 'new_status is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        if new_quantity is not None:
            try:
                new_quantity = float(new_quantity)
            except (ValueError, TypeError):
                return Response({'error': 'new_quantity must be a number'}, status=status.HTTP_400_BAD_REQUEST)

        DoseLogBusiness.revert_or_update_dose_status(str(log_id), new_status, new_quantity)
        return Response({'status': 'dose status updated'}, status=status.HTTP_200_OK)
