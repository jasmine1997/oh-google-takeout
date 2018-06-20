from django.conf import settings
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
    path('download/<int:id>', views.download, name='download'),
    path('delete/<int:id>', views.delete, name='delete'),
    path('visualize/<int:id>', views.visualize, name='visualize'),
    path('logout/', views.log_out, name='logout')
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns.append(path('__debug__/', include(debug_toolbar.urls)))
