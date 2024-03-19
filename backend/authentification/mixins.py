# mixins.py
# from django.db.models.signals import pre_save
# from django.utils.functional import curry
# from rest_framework_simplejwt.authentication import JWTAuthentication
# from auditlog.compat import is_authenticated
# from auditlog.compat import is_authenticated
# from auditlog.middleware import threadlocal, AuditlogMiddleware
# from auditlog.models import LogEntry


# class DRFDjangoAuditModelMixin:
#     """
#     Mixin to integrate django-auditlog with Django Rest Framework.

#     This is needed because DRF does not perform the authentication at middleware layer
#     instead it performs the authentication at View layer.

#     This mixin adds behavior to connect/disconnect the signals needed by django-auditlog to auto
#     log changes on models.
#     It assumes that AuditlogMiddleware is activated in settings.MIDDLEWARE_CLASSES
#     """

#     def should_connect_signals(self, request):
#         """Determines if the signals should be connected for the incoming request."""
#         # By default only makes sense to audit when the user is authenticated
#         return is_authenticated(request.user)

#     def initial(self, request, *args, **kwargs):
#         """Overwritten to use django-auditlog if needed."""
#         super().initial(request, *args, **kwargs)

#         if self.should_connect_signals(request):
#             set_actor = curry(AuditlogMiddleware.set_actor, user=request.user,
#                               signal_duid=threadlocal.auditlog['signal_duid'])
#             pre_save.connect(set_actor, sender=LogEntry,
#                              dispatch_uid=threadlocal.auditlog['signal_duid'], weak=False)

#     def finalize_response(self, request, response, *args, **kwargs):
#         """Overwritten to cleanup django-auditlog if needed."""
#         response = super().finalize_response(request, response, *args, **kwargs)

#         if hasattr(threadlocal, 'auditlog'):
#             pre_save.disconnect(sender=LogEntry, dispatch_uid=threadlocal.auditlog['signal_duid'])
#         return response

# from django.contrib.auth.middleware import get_user
# from django.utils.deprecation import MiddlewareMixin
# from django.utils.functional import SimpleLazyObject

# from rest_framework_simplejwt.authentication import JWTAuthentication


# class JWTAuthenticationMiddleware(MiddlewareMixin):

#     def process_request(self, request):
#         request.user = SimpleLazyObject(
#             lambda: self.__class__.get_jwt_user(request))

#     @staticmethod
#     def get_jwt_user(request):
#         user = get_user(request)
#         if user.is_authenticated:
#             return user
#         jwt_authentication = JWTAuthentication()
#         if jwt_authentication.get_header(request):
#             user, jwt = jwt_authentication.authenticate(request)
#         return user


# ```
# from rest_framework_jwt.authentication import JSONWebTokenAuthentication

# from django.utils.functional import SimpleLazyObject





# Workaround simialr to https://github.com/GetBlimp/django-rest-framework-jwt/issues/45 # noqa

# class AuthenticationTokenMiddleware:

#     """Authentication middleware which return user from token."""



#     def __init__(self, get_response):

#         """Initializer."""

#         self.get_response = get_response



#     def __call__(self, request):

#         """Response."""

#         user = request.user

#         request.user = SimpleLazyObject(lambda: self.get_token_user(request,

#                                                                     user))

#         return self.get_response(request)



#     def get_token_user(self, request, user):

#         """Return user from DRF token."""

#         try:

#             authenticator = JSONWebTokenAuthentication()

#             return authenticator.authenticate(request)[0]

#         except Exception:

#             return user