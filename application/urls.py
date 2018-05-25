from django.urls import include, path

from . import views

urlpatterns = [
    path('admin/', include('administrator.urls')),
    path('', views.home, name='home'),
    path('authorize/', views.authorize, name='authorize'),
    path('authenticate/', views.authenticate, name='authenticate')
]
