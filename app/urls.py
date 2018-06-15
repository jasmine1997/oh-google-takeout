from django.urls import path, include

from app import views

urlpatterns = [
    path('admin/', include('admin.urls')),
    path('', views.info, name='info'),
    path('authorize/', views.authorize, name='authorize'),
    path('authenticate/', views.authenticate, name='authenticate'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('sync/', views.sync, name='sync'),
    path('upload/', views.upload, name='upload'),
    path('delete/<int:id>', views.delete, name='delete'),
    path('visualize/', views.visualize, name='visualize'),
    path('logout/', views.log_out, name='logout')
]
