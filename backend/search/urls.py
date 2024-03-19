from django.urls import path
from .views import *
from .transco import *

urlpatterns = [
    path('', home),
    path('searchbyattributeapi/', searchbyattributeapi, name='searchbyattributeapi'),
    path('upload_gdb/', upload_gdb, name='upload_gdb'),

]
