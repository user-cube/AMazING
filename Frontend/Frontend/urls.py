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
from django.urls import path
from django.contrib.auth import views as auth_views

from app.views import profile, home, checkTests, checkTestInfo, editProfile, updateProfile, \
    createUser, userCreation, validateUser, saveUser, rankUp, listUsers, editUser, processUser, \
    searchUser, networkStatus, processNode, searchTest, calendar, registerTest, checkTestInfoAdmin, \
    checkTestsAdmin, searchTestAdmin, createAcessPoint, processAP, registerTestSave, listTemplates, \
    templateInfo, interfaceUP, interfaceDown, openFileTest, iperfServer, iperfClient, processIpServer, \
    processIpClient, userStatistics, adminStatistics, interfaceScan, interfaceConnect


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', networkStatus, name='home'),
    path('login/', auth_views.LoginView.as_view(template_name='login/login.html'), name='login'),
    path('logout', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
    path('profile/', profile, name="profile"),
    path('profile/edit/', editProfile, name="editProfile"),
    path('profile/save/', updateProfile, name="updateProfile"),
    path('profile/rankup', rankUp, name="rankupreq"),
    path('users/', listUsers, name="listusers"),
    path('users/search/', searchUser, name="searchuser"),
    path('users/edit/<int:userId>', editUser, name="edituser"),
    path('users/process', processUser, name="processuser"),
    path('checkTests/', checkTests, name="tests"),
    path('checkTests/search/', searchTest, name="searchtest"),
    path('checkTests/admin/', checkTestsAdmin, name="testsAdmin"),
    path('checkTests/admin/search/', searchTestAdmin, name="searchtestAdmin"),
    path('checkTests/<int:testID>', checkTestInfo, name="testinfo"),
    path('checkTests/admin/<int:testID>', checkTestInfoAdmin, name="testinfoAdmin"),
    path('create/user/', createUser, name="createUser"),
    path('create/user/save', userCreation, name="saveuser"),
    path('create/user/validate/<str:token>', validateUser, name="validateuser"),
    path('create/user/validate/save/', saveUser, name="savepassword"),
    path('network/status/', networkStatus, name="networkstatus"),
    path('network/status/<int:nodeID>', processNode, name="nodestatus"),
    path('network/createAP/<int:nodeID>', createAcessPoint, name="createap"),
    path('network/create/AP/save/<int:nodeID>', processAP, name="saveap"),
    path('network/templates/', listTemplates, name="listtemplates"),
    path('network/templates/<int:templateID>', templateInfo, name="templateinfo"),
    path('calendar/', calendar, name='calendar'),
    path('calendar/test', registerTest, name='registertest'),
    path('calendar/test/save', registerTestSave, name='registertestsave'),
    path('network/interface/<int:node>/<str:iName>/scan', interfaceScan, name = 'interfacescan'),
    path('network/interface/<int:node>/<str:iName>/up', interfaceUP, name = 'interfaceup'),
    path('network/interface/<int:node>/<str:iName>/down', interfaceDown, name = 'interfacedown'),
    path('network/interface/<int:node>/<str:iName>/<str:ssid>/<str:state>/connect/<str:store>', interfaceConnect, name = 'interfaceconn'),
    path('network/createIpServer/<int:nodeID>', iperfServer, name="iperfserver"),
    path('network/createIpClient/<int:nodeID>', iperfClient, name="iperfclient"),
    path('network/create/Iperf/Server/save/<int:nodeID>', processIpServer, name="saveipserver"),
    path('network/create/Iperf/Client/save/<int:nodeID>', processIpClient, name="saveipclient"),
    path('openfile/<int:file>/<int:testID>', openFileTest, name = 'openfile'),
    path('statistics/user/', userStatistics, name='userStatistics'),
    path('statistics/admin', adminStatistics, name='adminStatistics'),
]
