"""
URL configuration for aptiv project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path
from process import views
from process.views import home


urlpatterns = [
    path('', home, name='home'),
    path('process-list/', views.process_list, name='process_list'),
    path('kill-process/<int:pid>/', views.kill_process, name='kill_process'),
    path('save-snapshot/', views.save_snapshot, name='save_snapshot'),
    path('snapshots/', views.snapshot_list, name='snapshot_list'),
    path('snapshots/<int:snapshot_id>/', views.snapshot_detail, name='snapshot_detail'),

    path('accounts/login/', LoginView.as_view(template_name='admin/login.html')),
    path('accounts/logout/', LogoutView.as_view(), name='logout'),

    path('admin/', admin.site.urls),
]
