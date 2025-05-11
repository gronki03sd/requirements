from django.shortcuts import render

def statistics_view(request):
    """عرض الإحصائيات"""
    context = {
        'title': 'الإحصائيات'
    }
    return render(request, 'stats/statistics.html', context)