from django.urls import path, include
from ats_app import views

urlpatterns = [
    path('', views.home, name='home'),        # HOME page serves frontend index.html
    path('api/', include('ats_app.urls')),    # existing API
]