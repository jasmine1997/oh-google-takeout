from django.urls import include, path

from application import views

urlpatterns = [
    path('admin/', include('administrator.urls')),
    path('', views.home, name='home'),
    path('authorize/', views.authorize, name='authorize'),
    path('authenticate/', views.authenticate, name='authenticate'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('logout/', views.sign_out, name='logout')
]
