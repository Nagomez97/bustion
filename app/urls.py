from django.urls import path

from . import views

urlpatterns = [
    path('login', views.applogin, name='login'),
    path('logout', views.applogout, name='logout'),
    path('auth', views.auth, name='auth'),
    path('home', views.home, name='home'),
    path('', views.home, name='home'),
    path('projects/add', views.createProject, name='createProject'),
    path('projects/delete', views.deleteProject, name='deleteProject'),
    path('projects/view', views.viewProject, name='viewProject'),
    path('projects/fuzzers', views.viewFuzzers, name='viewFuzzers'),
    path('projects/fuzzers/add', views.addFuzzer, name='addFuzzer'),
    path('projects/fuzzers/delete', views.deleteFuzzer, name='deleteFuzzer'),
    path('projects/fuzzers/update', views.updateFuzzer, name='updateFuzzer'),
    path('projects/webs', views.viewWebs, name='viewWebs'),
    path('projects/webs/add', views.addWeb, name='addWeb'),
    path('projects/webs/update', views.updateWeb, name='updateWeb'),
    path('projects/webs/delete', views.deleteWeb, name='deleteWeb'),
    path('projects/webs/findings', views.findings, name='findings'),
    path('projects/webs/findings/delete', views.deleteFinding, name='deleteFinding'),
    path('projects/webs/findings/deleteall', views.deleteAllFinding, name='deleteAllFinding'),
    path('projects/webs/findings/add', views.addFinding, name='addFinding'),
    path('projects/launchManager', views.launchManager, name='launchManager'),
    path('projects/launch', views.launch, name='launch'),
    path('projects/jobs/kill', views.killJob, name='killJob'),

]