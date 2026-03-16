from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .business import MedicationBusiness, ScheduleBusiness, DoseLogBusiness
from . import serializers
import uuid
from datetime import datetime
from django.utils.decorators import method_decorator
from rest_framework.exceptions import APIException
from django.http import JsonResponse

def _api_error_handler(func):
    """Decorator for APIView dispatch method to handle common exceptions."""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as e:
            return JsonResponse({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except APIException as e:
            # Catch DRF-specific exceptions (like ValidationErrors) to return clean JSON
            error_data = e.detail if isinstance(e.detail, dict) else {'error': str(e.detail)}
            return JsonResponse(error_data, status=e.status_code)
        except Exception as e:
            # In a real app, you'd want to log this exception.
            # import logging
            # logging.exception("An unexpected error occurred")
            # Exposing str(e) so your console actually tells you what went wrong instead of generic 500
            return JsonResponse({'error': f'An unexpected server error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
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
        serializer = serializers.RefillSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        MedicationBusiness.refill_medication(str(medication_id), serializer.validated_data['amount_added'])
        return Response({'status': 'medication refilled'}, status=status.HTTP_200_OK)

@method_decorator(_api_error_handler, name='dispatch')
class MedicationGenerateScheduleView(APIView):
    """
    Trigger schedule generation for a medication.
    POST: /api/medications/<uuid:medication_id>/generate-schedule/
    """
    def post(self, request, medication_id: uuid.UUID):
        serializer = serializers.MedicationGenerateScheduleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        DoseLogBusiness.generate_upcoming_schedule(str(medication_id), serializer.validated_data['days_ahead'])
        return Response({'status': 'schedule generation triggered'}, status=status.HTTP_202_ACCEPTED)

# === Schedule Views ===

@method_decorator(_api_error_handler, name='dispatch')
class ScheduleListCreateView(APIView):
    """
    List all schedules or create a new schedule.
    GET: /api/schedules/
    POST: /api/schedules/
    """
    def get(self, request):
        schedules = ScheduleBusiness.get_all_schedules()
        return Response(schedules, status=status.HTTP_200_OK)

    def post(self, request):
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
        serializer = serializers.ScheduleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        ScheduleBusiness.update_schedule(str(schedule_id), serializer.validated_data)
        return Response({'status': 'schedule updated'}, status=status.HTTP_200_OK)

    def delete(self, request, schedule_id: uuid.UUID):
        serializer = serializers.ScheduleDeleteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        ScheduleBusiness.remove_schedule(str(schedule_id), str(serializer.validated_data['medication_id']))
        return Response(status=status.HTTP_204_NO_CONTENT)

# === Dose Log Views ===

@method_decorator(_api_error_handler, name='dispatch')
class DailyDoseView(APIView):
    """
    Get all dose logs for a specific date.
    GET: /api/doses/daily/?date=YYYY-MM-DD
    """
    def get(self, request):
        serializer = serializers.DailyDoseQuerySerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        
        doses = DoseLogBusiness.get_daily_planned_doses(str(serializer.validated_data['date']))
        return Response(doses, status=status.HTTP_200_OK)

@method_decorator(_api_error_handler, name='dispatch')
class DoseLogDetailView(APIView):
    """
    Retrieve, modify, or delete a specific dose log.
    GET: /api/doses/<uuid:log_id>/
    PATCH: /api/doses/<uuid:log_id>/
    DELETE: /api/doses/<uuid:log_id>/
    """
    def get(self, request, log_id: uuid.UUID):
        log = DoseLogBusiness.get_dose_log_by_id(str(log_id))
        return Response(log, status=status.HTTP_200_OK)

    def patch(self, request, log_id: uuid.UUID):
        serializer = serializers.DoseLogModifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        DoseLogBusiness.modify_single_dose(str(log_id), serializer.validated_data['new_strength'], serializer.validated_data['new_quantity'])
        return Response({'status': 'dose details modified'}, status=status.HTTP_200_OK)

    def delete(self, request, log_id: uuid.UUID):
        DoseLogBusiness.delete_dose_log(str(log_id))
        return Response(status=status.HTTP_204_NO_CONTENT)

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
        serializer = serializers.DoseLogSkipSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        DoseLogBusiness.log_dose_as_skipped(str(log_id), serializer.validated_data.get('notes'))
        return Response({'status': 'dose marked as skipped'}, status=status.HTTP_200_OK)

@method_decorator(_api_error_handler, name='dispatch')
class DoseLogRescheduleView(APIView):
    """
    Reschedule a single dose.
    POST: /api/doses/<uuid:log_id>/reschedule/
    """
    def post(self, request, log_id: uuid.UUID):
        serializer = serializers.DoseLogRescheduleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        DoseLogBusiness.reschedule_single_dose(str(log_id), str(serializer.validated_data['new_datetime']))
        return Response({'status': 'dose rescheduled'}, status=status.HTTP_200_OK)

@method_decorator(_api_error_handler, name='dispatch')
@method_decorator(_api_error_handler, name='dispatch')
class AdHocDoseCreateView(APIView):
    """
    Log an ad-hoc dose.
    POST: /api/doses/ad-hoc/
    """
    def post(self, request):
        serializer = serializers.AdHocDoseSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        DoseLogBusiness.add_ad_hoc_dose(
            str(serializer.validated_data['medication_id']), 
            serializer.validated_data['quantity'], 
            serializer.validated_data.get('strength')
        )
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
        serializer = serializers.DoseStatusUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        DoseLogBusiness.revert_or_update_dose_status(
            str(log_id), 
            serializer.validated_data['new_status'], 
            serializer.validated_data.get('new_quantity')
        )
        return Response({'status': 'dose status updated'}, status=status.HTTP_200_OK)
