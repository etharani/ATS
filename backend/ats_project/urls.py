from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from ats_app import views

urlpatterns = [
    path('', views.home, name='home'),        # HOME page serves frontend index.html
    path('api/', include('ats_app.urls')),    # existing API
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
