from django.urls import path, include

from app import views

urlpatterns = [
    path('admin/', include('admin.urls')),
    path('', views.info, name='info'),
    path('authorize/', views.authorize, name='authorize'),
    path('authenticate/', views.authenticate, name='authenticate'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('upload/', views.upload, name='upload'),
    path('logout/', views.log_out, name='logout')
]
