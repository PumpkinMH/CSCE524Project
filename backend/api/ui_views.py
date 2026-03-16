from django.shortcuts import render
from datetime import date, datetime, timedelta

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

    context = {
        'today': target_date.strftime('%Y-%m-%d'),
        'display_date': target_date.strftime('%A, %B %d, %Y'),
        'prev_date': (target_date - timedelta(days=1)).strftime('%Y-%m-%d'),
        'next_date': (target_date + timedelta(days=1)).strftime('%Y-%m-%d'),
    }
    return render(request, 'api/partials/daily_doses.html', context)

def medications_tab(request):
    """Renders the partial for the medications list tab content area."""
    return render(request, 'api/partials/medication_list.html')