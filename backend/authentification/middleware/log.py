
# from rest_framework_simplejwt.authentication import JSONWebTokenAuthentication
# # from rest_framework_simplejwt.authentication import JWTAuthentication

# from django.utils.functional import SimpleLazyObject

# class AuthenticationTokenMiddleware:

#     """Authentication middleware which return user from token."""



#     def __init__(self, get_response):

#         """Initializer."""

#         self.get_response = get_response



#     def __call__(self, request):

#         """Response."""

#         user = request.user

#         request.user = SimpleLazyObject(lambda: self.get_token_user(request, user))

#         return self.get_response(request)



#     def get_token_user(self, request, user):

#         """Return user from DRF token."""

#         try:

#             authenticator = JSONWebTokenAuthentication()

#             return authenticator.authenticate(request)[0]

#         except Exception:

#             return user
from authentification.models import User_login_Data
import jwt        
from django.contrib.auth.models import AnonymousUser
from django.conf import settings
from rest_framework_simplejwt.tokens import AccessToken

def simple_middleware(get_response):
    # One-time configuration and initialization.

    def middleware(request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.
        

        response = get_response(request)
        
        authorization_header = request.headers.get('Authorization')
        if authorization_header and authorization_header.startswith('Bearer '):
            token = authorization_header.split(' ')[1]
            try:
                # Verify the JWT token
                access_token = AccessToken(token)
                user_id = access_token.payload.get('user_id')
                # Assuming the payload contains user information, you can access it like:
                if user_id:
                    # Assuming the payload contains user information, you can access it like:
                    USERNAME = User_login_Data.objects.get(id = user_id)
                    actor_id = user_id
                    request.user = User_login_Data.objects.get(id = user_id)
                else:
                    # Handle the case where user information is not present in the token
                    USERNAME = "Anonymous"
            except jwt.ExpiredSignatureError:
                # Handle expired token
                USERNAME = "Anonymous"
            except jwt.InvalidTokenError:
                # Handle invalid token
                USERNAME = "Anonymous"
        else:
            # Handle the case for requests without a valid JWT token
            USERNAME = "Anonymous"
    #     if request.user.is_authenticated:
    #         username = "Anonymous"
    #     else:
    # # Access attributes for authenticated users
    #         username = request.user.USERNAME
    #         print(request.user.USERNAME)
    #     # Code to be executed for each request/response after
    #     # the view is called.
            

        return response

    return middleware



import threading
import time
from django.conf import settings
from django.db.models.signals import pre_save
# from django.utils.functional import curry   #not working
from functools import partial
from django.apps import apps
from auditlog.models import LogEntry
from django.http import JsonResponse
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
threadlocal = threading.local()
from django.utils.deprecation import MiddlewareMixin

# # from django.utils.middleware import MiddlewareMixin
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
class MyMiddleware(MiddlewareMixin):
    def process_request(self, request):
        threadlocal.auditlog = {
            'signal_duid': (self.__class__, time.time()),
            'remote_addr': request.META.get('REMOTE_ADDR'),
        }
        
        if request.META.get('HTTP_X_FORWARDED_FOR'):
            threadlocal.auditlog['remote_addr'] = request.META.get('HTTP_X_FORWARDED_FOR').split(',')[0]

        # Connect signal for automatic logging
        set_actor = partial(self.set_actor, request=request, signal_duid=threadlocal.auditlog['signal_duid'])
        pre_save.connect(set_actor, sender=LogEntry, dispatch_uid=threadlocal.auditlog['signal_duid'], weak=False)

        # return None

    def process_response(self, request, response):
        if hasattr(threadlocal, 'auditlog'):
            pre_save.disconnect(sender=LogEntry, dispatch_uid=threadlocal.auditlog['signal_duid'])

        return response
    
    
    def process_exception(self, request, exception):
        """
        Disconnects the signal receiver to prevent it from staying active in case of an exception.
        """
        if hasattr(threadlocal, 'auditlog'):
            pre_save.disconnect(sender=LogEntry, dispatch_uid=threadlocal.auditlog['signal_duid'])

        return None

    @staticmethod
    def set_actor(request, sender, instance, signal_duid, **kwargs):
        """
        Signal receiver with an extra, required 'user' kwarg. This method becomes a real (valid) signal receiver when
        it is curried with the actor.
        """
        if hasattr(threadlocal, 'auditlog'):
            if not hasattr(request, 'user') or not request.user.is_authenticated:
                return
            if signal_duid != threadlocal.auditlog['signal_duid']:
                return
            try:
                app_label, model_name = settings.AUTH_USER_MODEL.split('.')
                auth_user_model = apps.get_model(app_label, model_name)
            except ValueError:
                auth_user_model = apps.get_model('auth', 'user')
            if sender == LogEntry and isinstance(request.user, auth_user_model) and instance.actor is None:
                instance.actor = request.user

            instance.remote_addr = threadlocal.auditlog['remote_addr']
        