from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.hashers import make_password
from django.contrib.auth.hashers import make_password
from django.core.management.base import BaseCommand
from django.contrib.auth.management.commands import createsuperuser
from django.core.management.base import CommandError
import sys
from .models import *
from .validation import *
from .helpers import *
import getpass
def get_secure_input(prompt):
    return getpass.getpass(prompt)


def get_secure_input(prompt):
    return getpass.getpass(prompt)

class UserManager(BaseUserManager):
    use_in_migrations = True
    def get_queryset(self):
        return super().get_queryset()
    # PASSWORD = get_secure_input("Enter your custom field value: ")
    def all_users(self):
        user = self.get_queryset().all()
        return user

    def create_user(self, USERNAME, EMAIL, PASSWORD, **extra_fields):
        EMAIL = self.normalize_email(EMAIL)
        user = self.model(USERNAME=USERNAME, EMAIL=EMAIL, PASSWORD=PASSWORD, **extra_fields)
        user.save(using=self._db)
        
        if user.id is not None:
            user_id_num = str(user.id)
            string_lenth = "000000"
            print(string_lenth[:-len(user_id_num)] + user_id_num)
            if len(user_id_num) < 7:
                x = string_lenth[:-len(user_id_num)] + user_id_num
                user.USERID = x
                send_SU_EMAIL_CREATE(user.EMAIL , user.USERNAME)
                user.PASSWORD = make_password(user.PASSWORD)
                user.save()
                print("FINISHED")
        return user

    def create_superuser(self, USERNAME, EMAIL, PASSWORD, **extra_fields):
        USERNAME = USERNAME.replace(" ","")
        if self.all_users().filter(USER_TYPE='SU').exists()  or self.all_users().filter(EMAIL__iexact=EMAIL).exists() or self.all_users().filter(USERNAME__iexact=USERNAME).exists():
            sys.exit("Super User Already Created OR CHECK Email already exist")
        # USERNAME = USERNAME.replace(" ","")
        user = self.create_user(USERNAME=USERNAME, EMAIL=EMAIL.lower(), PASSWORD=PASSWORD,  **extra_fields)
        user.USER_TYPE = "SU"
        user.save(using=self._db)
        return user
    
    # def validate_EMAIL(self, value):
    #     norm_email = value.lower().strip()
    #     print("LLLLLLLLLLLLLLLLL")
    #     print(norm_email)
    #     if User_login_Data.objects.filter(EMAIL__iexact=norm_email).exists():
    #         raise serializers.ValidationError("Not unique email")
    #     return norm_email
# class Command(BaseCommand):
#     help = 'Create a superuser with a custom field value'

#     def handle(self, *args, **options):
#         USERNAME = input('Enter desired username: ')
#         EMAIL = input('Enter desired username: ')
#         PASSWORD = getpass('Enter your custom field value: ')
#         User = UserManager()
