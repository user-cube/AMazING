"""Frontend URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
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
from django.urls import path, include
from django.contrib.auth import views as auth_views
from app.views import profile, home, checkTests, checkTestInfo, editProfile, updateProfile

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('login/', auth_views.LoginView.as_view(template_name='login/login.html'), name='login'),
    path('logout', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
    path('profile/', profile, name="profile"),
    path('profile/edit/', editProfile, name="editProfile"),
    path('profile/save/', updateProfile, name="updateProfile"),
    path('checkTests/', checkTests, name="tests"),
    path('checkTests/<int:testID>', checkTestInfo, name="testinfo"),
    path('private_storage/', include('private_storage.urls')),
]
