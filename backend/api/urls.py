from django.urls import path
from . import views

app_name = 'api'

urlpatterns = [
    # Medication URLs
    path('medications/', views.MedicationListCreateView.as_view(), name='medication-list-create'),
    path('medications/refill-alerts/', views.MedicationRefillAlertsView.as_view(), name='medication-refill-alerts'),
    path('medications/<uuid:medication_id>/', views.MedicationDetailView.as_view(), name='medication-detail'),
    path('medications/<uuid:medication_id>/details/', views.MedicationDetailsUpdateView.as_view(), name='medication-details-update'),
    path('medications/<uuid:medication_id>/upgrade/', views.MedicationUpgradeView.as_view(), name='medication-upgrade'),
    path('medications/<uuid:medication_id>/archive/', views.MedicationArchiveActionView.as_view(), name='medication-archive'),
    path('medications/<uuid:medication_id>/refill/', views.MedicationRefillView.as_view(), name='medication-refill'),
    path('medications/<uuid:medication_id>/generate-schedule/', views.MedicationGenerateScheduleView.as_view(), name='medication-generate-schedule'),

    # Schedule URLs
    path('schedules/', views.ScheduleListCreateView.as_view(), name='schedule-create'),
    path('schedules/<uuid:schedule_id>/', views.ScheduleDetailView.as_view(), name='schedule-detail'),

    # DoseLog URLs
    path('doses/daily/', views.DailyDoseView.as_view(), name='doses-daily'),
    path('doses/ad-hoc/', views.AdHocDoseCreateView.as_view(), name='doses-ad-hoc'),
    path('doses/sweep-expired/', views.DoseSweepExpiredView.as_view(), name='doses-sweep-expired'),
    path('doses/<uuid:log_id>/', views.DoseLogDetailView.as_view(), name='dose-detail'), # Combined GET, PATCH, DELETE
    path('doses/<uuid:log_id>/take/', views.DoseLogTakeView.as_view(), name='dose-take'),
    path('doses/<uuid:log_id>/skip/', views.DoseLogSkipView.as_view(), name='dose-skip'),
    path('doses/<uuid:log_id>/revert/', views.DoseLogRevertView.as_view(), name='dose-revert'),
    path('doses/<uuid:log_id>/reschedule/', views.DoseLogRescheduleView.as_view(), name='dose-reschedule'),
    path('doses/<uuid:log_id>/status/', views.DoseStatusUpdateView.as_view(), name='dose-status-update'),
]