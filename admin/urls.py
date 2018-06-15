from django.urls import path

from admin import views

urlpatterns = [
    path('login/', views.log_in, name='admin_login'),
    # path('config/', views.config, name='admin_config'),
    # path('add_file/', views.add_file, name='admin_add_file'),
    # path('delete_file/<int:id>', views.delete_file, name='admin_delete_file')
]
