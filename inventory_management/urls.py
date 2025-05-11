from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect

# Redirect root to dashboard
def home_redirect(request):
    return redirect('dashboard')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home_redirect, name='home'),  # Redirect to dashboard
    path('dashboard/', include('dashboard.urls')),
    path('inventory/', include('inventory.urls')),
    path('orders/', include('orders.urls')),
    path('invoices/', include('invoices.urls')),
    path('statistics/', include('statistics.urls')),
    path('users/', include('users.urls')),
    path('settings/', include('settings_app.urls')),
]

# Add media urls in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)