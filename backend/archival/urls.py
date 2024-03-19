from django.urls import path
from .views import *
from .multiplexml import *
from archival import multiplexml  # Import the multiplexml module

urlpatterns = [
    path('', home),
    path('upload/', file_upload_view, name='upload'),
    path('formdatasave/', formdatasave, name='formdatasave'),
    path('tabledatashow/', show, name='show'),
    path('generate-xml/', multiplexml.generate_xml, name='generate_xml'),
    # path('register_general/',register),
    # path('authorized_register/', authorized_register),
    # path('login/', login),
    # path('usert_type/', api_user_type),
    # path('forget_password/', forget_password),
    # path('update_fo_password/<str:token>/', update_password),
    # path('xyz/', xyx), #views2
    # path('change_password/', change_password), #views2
    # path('update_ch_password/<int:id>/', ch_updte_password), ##views2
]
