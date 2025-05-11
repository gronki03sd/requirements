from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from stats.utils import get_dashboard_stats, get_monthly_sales_data

@login_required
def dashboard_view(request):
    """Dashboard view - requires login"""
    context = {
        'title': 'Dashboard',
        'stats': get_dashboard_stats(),
        'sales_data': get_monthly_sales_data()
    }
    return render(request, 'dashboard/index.html', context)