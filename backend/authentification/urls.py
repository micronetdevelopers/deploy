from django.urls import path
from .views import *
from .views2 import *
from .logging import *
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('', fty),
    path('forget_password/', forget_password),#active
    path('update_fo_password/', update_password),#active
    path('xyz/', xyx), #views2   
    path('change_password/', change_password), #views2
    # path('update_ch_password/<int:id>/', ch_updte_password), ##views2
    path('contact_us/', contact_us),#active
    

    #general signup apihttp://127.0.0.1:8000/login_user/
    path('general_signup/',register_general),#active 
    #login api
    path('login_user/', login_user),#active
    #authorized api
    path('authorized_singup/', user_authorized_function),#active
    #admin api
    path('admin_url/', admin_function),#active
    path('permission_function_url/', permission_function), #active
    path('superuser_api/', superuser_api),

    # path('general_signup_test/', register_general_test),#logg testing from logging
    
]