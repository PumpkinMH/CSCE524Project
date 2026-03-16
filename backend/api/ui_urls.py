from django.urls import path
from . import ui_views

app_name = 'ui'

urlpatterns = [
    path('', ui_views.index, name='index'),
    path('tabs/daily-doses/', ui_views.daily_doses_tab, name='daily_doses_tab'),
    path('tabs/medications/', ui_views.medications_tab, name='medications_tab'),
    path('tabs/schedules/', ui_views.schedules_tab, name='schedules_tab'),
]