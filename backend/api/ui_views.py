from django.shortcuts import render
from datetime import date, datetime, timedelta
from .business import MedicationBusiness, ScheduleBusiness, DoseLogBusiness

def index(request):
    """Renders the main page shell with the tab bar."""
    return render(request, 'api/index.html')

def daily_doses_tab(request):
    """Renders the partial for the daily doses tab content area."""
    date_str = request.GET.get('date')
    if date_str:
        try:
            target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            target_date = date.today()
    else:
        target_date = date.today()

    # Fetch exact same data the console app requests via GET
    doses = DoseLogBusiness.get_daily_planned_doses(target_date.strftime('%Y-%m-%d'))
    medications = MedicationBusiness.get_active_inventory()

    context = {
        'today': target_date.strftime('%Y-%m-%d'),
        'display_date': target_date.strftime('%A, %B %d, %Y'),
        'prev_date': (target_date - timedelta(days=1)).strftime('%Y-%m-%d'),
        'next_date': (target_date + timedelta(days=1)).strftime('%Y-%m-%d'),
        'taken_doses': [d for d in doses if d['status'] == 'taken'],
        'pending_doses': [d for d in doses if d['status'] == 'pending'],
        'missed_doses': [d for d in doses if d['status'] in ['missed', 'skipped']],
        'medications': medications,
    }
    return render(request, 'api/partials/daily_doses.html', context)

def medications_tab(request):
    """Renders the partial for the medications list tab content area."""
    medications = MedicationBusiness.get_active_inventory()
    schedules = ScheduleBusiness.get_all_schedules()
    
    for med in medications:
        med['schedules'] = [s for s in schedules if str(s['medication_id']) == str(med['medication_id'])]

    context = {
        'medications': medications,
        'alerts': MedicationBusiness.get_refill_alerts()
    }
    return render(request, 'api/partials/medication_list.html', context)

def schedules_tab(request):
    """Renders the partial for the schedules tab content area."""
    schedules = ScheduleBusiness.get_all_schedules()
    medications = MedicationBusiness.get_active_inventory()
    
    med_dict = {med['medication_id']: med['name'] for med in medications}
    for sched in schedules:
        sched['medication_name'] = med_dict.get(sched['medication_id'], 'Unknown Medication')
        
    context = {'schedules': schedules, 'medications': medications}
    return render(request, 'api/partials/schedule_list.html', context)