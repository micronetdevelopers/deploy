from django.db import models
import time
from rest_framework.response import Response
from django.db.models.signals import  post_save, pre_save
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.dispatch import Signal
from django.core.validators import validate_email
instance_update = Signal()
from django.core.management import call_command
import uuid
from threading import Thread
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser
from .manager import UserManager  #, Command
from .validation import *
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
import getpass
from .helpers import *
from datetime import datetime
from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog
def get_secure_input(prompt):
    return getpass.getpass(prompt)


class User_login_Data(AbstractBaseUser, PermissionsMixin):
    USER_TYPE_CHOICES = (
    ('GU', 'General-User'),
    ('SU', 'Superuser-User'),
    ('AU', 'Admin-User'),
    ('UU', 'Athorizised-User')
)
    USER_APRO_CHOICE =(
    ('APPROVED', 'User-APPROVED'),
    ('REJECTED', 'User-REJECTED'),
    ('BLOCKED', 'User-BLOCKED'), #INPROGRESS
    ('DELETE', 'User-DELETE'),
    ('INPROGRESS', 'INPROGRESS')
    )
    USERID = models.CharField(max_length=6, unique=True, null=True, blank=True) 
    USERNAME = models.CharField(max_length=20, unique=True, null=False, blank=False, validators=[validate_no_dot])
    PASSWORD = models.CharField(max_length=150,null=False, blank=False, validators=[validate_password])
    USER_TYPE = models.CharField(max_length=2, choices=USER_TYPE_CHOICES, default='GU', null=True, blank=True)#
    EMAIL = models.EmailField(_("email address"),max_length=100, unique=True)
    MOBILE_NO = models.CharField(max_length=10,null=True, blank=True)
    SU_APRO_STAT = models.CharField(max_length=20,choices=USER_APRO_CHOICE,null=True, blank=True)#
    AU_APRO_STAT = models.CharField(max_length=20,choices=USER_APRO_CHOICE,null=True, blank=True)#
    APRO_DATE = models.DateTimeField(null=True)
    SU_APRO_REM = models.CharField(max_length=100, null=True, blank=True)
    AU_APRO_REM = models.CharField(max_length=100, null=True, blank=True)
    Q1_ID = models.IntegerField(null=True)
    Q2_ID = models.IntegerField(null=True)
    Q1_AN = models.CharField(max_length=20, null=True) 
    Q2_AN = models.CharField(max_length=20, null=True)
    THEME_OPT = models.CharField(max_length=50, null=True, blank=True)
    CREATION_DATE = models.DateTimeField(default=timezone.now, blank=True)
    USERNAME_FIELD = "USERNAME"
    REQUIRED_FIELDS = ["EMAIL","PASSWORD"]
    first_name = None
    last_name = None
    password = None
    last_login = None
    is_superuser =None
    objects = UserManager()
    history = AuditlogHistoryField()
    def __str__(self):
        return self.USERNAME
    # def Q1_AN_field(self, value):
    #     # Customize the normalization logic as needed  abc@gmail.com
    #     normalized_value = value.lower().strip()
    #     return normalized_value
    # def Q2_AN_field(self, value):
    #     # Customize the normalization logic as needed
    #     normalized_value = value.lower().strip()
    #     return normalized_value
    
    # def EMAIL_field(self, value):
    #     # Customize the normalization logic as needed
    #     normalized_value = value.lower().strip()
    #     return normalized_value
    
    # def save(self, *args, **kwargs):
    #     # Normalize the char field before saving
    #     self.Q1_AN = self.Q1_AN_field(self.Q1_AN)
    #     self.Q2_AN = self.Q2_AN_field(self.Q2_AN)
        # self.EMAIL = self.EMAIL_field(self.EMAIL)
        # super().save(*args, **kwargs)

    # def clean(self):
    #     # Validate email using Django's built-in email validator
    #     try:
    #         validate_email(self.EMAIL)
    #     except ValidationError:
    #         raise ValidationError({'EMAIL': 'Enter a valid email address.'})


    class Meta:
        db_table = 'Login_Main_Data'


class Users_login_Details_Data(models.Model):
    USERID = models.ForeignKey(User_login_Data, to_field='USERID', on_delete=models.CASCADE, null=True,  related_name='logindata') #create one column user_id in this table
    USER_F_NAME = models.CharField(max_length=20, null=True)#
    USER_M_NAME = models.CharField(max_length=20, null=True, blank=True)
    USER_L_NAME = models.CharField(max_length=20, null=True)#
    GENDER = models.CharField(max_length=20, null=True, blank=True)#20
    DOB = models.DateField(null=True)
    ORGANIZATION = models.CharField(max_length=100, null=True)#100#
    DESIGNATION = models.CharField(max_length=50,null=True)
    ADDRESS_1 = models.CharField(max_length=100, null=True, blank=True)
    ADDRESS_2 = models.CharField(max_length=100, null=True, blank=True)
    CITY = models.CharField(max_length=50, null=True)
    STATE = models.CharField(max_length=50, null=True)
    COUNTRY = models.CharField(max_length=50, null=True)
    PIN_CODE = models.CharField(max_length=6, null=True, blank=True)
    UU_REM = models.CharField(max_length=200, null=True, blank=True)
    LAN_LINE = models.CharField(max_length=15, null=True, blank=True)
    ALT_EMAIL = models.EmailField(max_length=100, null=True, blank=True)
    OFF_LOCA = models.CharField(max_length=50, null=True, blank=True)#50
    
    def __str__(self):
        return self.USERID_id or "No Name"
    
    class Meta:
        db_table = 'Profile_Main_Data'
    

class password_table(models.Model):
    USERID = models.OneToOneField(User_login_Data, to_field='USERID', on_delete=models.CASCADE, null=True) #create one column user_id in this table
    forget_password_token = models.CharField(max_length=100,default=None, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.USERID_id or "No Name"
        # return str(self.user.pk)
    
class THEME_MODULE(models.Model):
    USERID_THEME_OPT = models.CharField(max_length=6, unique=True, null=True, blank=True)
    THEME_TYPE = models.CharField(max_length=50, unique=True)
    MODEL_1 = models.CharField(max_length=50, null=True, blank=True)
    MODEL_2 = models.CharField(max_length=50, null=True, blank=True)
    MODEL_3 = models.CharField(max_length=50, null=True, blank=True)
    MODEL_4 = models.CharField(max_length=50, null=True, blank=True)
    MODEL_5 = models.CharField(max_length=50, null=True, blank=True)
    MODEL_6 = models.CharField(max_length=50, null=True, blank=True)
    MODEL_7 = models.CharField(max_length=50, null=True, blank=True)
    MODEL_8 = models.CharField(max_length=50, null=True, blank=True)
    MODEL_9 = models.CharField(max_length=50, null=True, blank=True)
    MODEL_10 = models.CharField(max_length=50, null=True, blank=True)
    def __str__(self):
        return self.THEME_TYPE 
    class Meta:
        db_table = 'THEME_MODULE'


class MODUL_VIEW_PERMISSION(models.Model):
    USERID = models.OneToOneField(User_login_Data, to_field='USERID', on_delete=models.CASCADE, unique=True)
    AU_ID = models.CharField(max_length=6)
    USERID_THEME_OPT = models.ForeignKey(THEME_MODULE, to_field='USERID_THEME_OPT', on_delete=models.CASCADE, null=True)
    MODEL_1 = models.BooleanField(null=True, blank=True)
    MODEL_2 = models.BooleanField(null=True, blank=True)
    MODEL_3 = models.BooleanField(null=True, blank=True)
    MODEL_4 = models.BooleanField(null=True, blank=True)
    MODEL_5 = models.BooleanField(null=True, blank=True)
    MODEL_6 = models.BooleanField(null=True, blank=True)
    MODEL_7 = models.BooleanField(null=True, blank=True)
    MODEL_8 = models.BooleanField(null=True, blank=True)
    MODEL_9 = models.BooleanField(null=True, blank=True)
    MODEL_10 = models.BooleanField(null=True, blank=True)
    class Meta:
        db_table = 'MODUL_VIEW_PERMISSION'
    

class contact_us(models.Model):
    customer_mail = models.EmailField(null=True, blank=True)
    customer_mobile_no = models.CharField(max_length=20,null=True, blank=True)
    catagory = models.CharField(max_length=100, null=True, blank=True)
    comment = models.CharField(max_length=100, null=True, blank=True)
    name = models.CharField(max_length=100, null=True)


class Myclass(Thread):
    def __init__(self, n):
        super().__init__()
        self.n = n
    def run(self):
        time.sleep(360)
        try:
            x = password_table.objects.get(USERID_id=self.n)
            x.forget_password_token = None 
            print("FORGET PASSWORD INSTANCE DELETE")
            x.delete()
        except password_table.DoesNotExist:
            print(f"password_table object Deleted")

# class permission_mail(Thread):
#     def __init__(self, n):
#         super().__init__()
#         self.n = n
#     def run(self):
#         try:
#             x = password_table.objects.get(USERID_id=self.n)
#             x.forget_password_token = None 
#             print("FORGET PASSWORD INSTANCE DELETE")
#             x.delete()
#         except password_table.DoesNotExist:
#             print(f"password_table object Deleted")


@receiver(post_save, sender = password_table)
def call_pass(sender, instance, created, **kwargs):
    val = instance.USERID_id # this is use for extract value from instance of primary key
    print(val)
    if not created:
        instance_update.send(sender=password_table, instance=instance)
        try:
            x = password_table.objects.get(USERID_id=instance.USERID_id)
            if x.forget_password_token == None:
                pass
            else:
                t1=Myclass(instance.USERID_id)
                t1.start()
        except password_table.DoesNotExist:
            print(f"password_table object Deleted")

# @receiver(post_save, sender = password_table)
# def call_pass(sender, instance, created, **kwargs):

@receiver(post_save, sender = MODUL_VIEW_PERMISSION)
def call_pass(sender, instance, created, **kwargs):
    val = instance.USERID_id # this is use for extract value from instance of primary key
    print(val)
    if not created:
        instance_update.send(sender=MODUL_VIEW_PERMISSION, instance=instance)
        try:
            x = MODUL_VIEW_PERMISSION.objects.get(USERID_id=instance.USERID_id)  #.select_related("USERID").filter(USERID__USERID=instance.USERID_id)
            print(x)
            y = THEME_MODULE.objects.get(USERID_THEME_OPT =  x.USERID_THEME_OPT_id)
            print(y)
            result_dict = {getattr(y, f"MODEL_{i}") : getattr(x, f"MODEL_{i}") for i in range(1, 11) if getattr(x, f"MODEL_{i}") == True}
            print(result_dict)
            s = ", ".join(result_dict.keys())
            k = User_login_Data.objects.get(USERID=instance.USERID_id)
            EMAIL = k.EMAIL
            USERNAME = k.USERNAME
            print(USERNAME)
            print(k.SU_APRO_STAT)
            print(k.AU_APRO_STAT)
            if k.SU_APRO_STAT == "APPROVED" and k.AU_APRO_STAT == "APPROVED":
                if k.AU_APRO_STAT == "APPROVED" and s:
                    send_UU_model_permission(EMAIL, s, USERNAME)
                    print("FINISHED")
                else:
                    pass
            else:
                pass
            
        except:
            print("SOMETHING WENT WORNG")

        #     if x.forget_password_token == None:
        #         pass
        #     else:
        #         t1=Myclass(instance.USERID_id)
        #         t1.start()
        # except password_table.DoesNotExist:
        #     print(f"password_table object Deleted")
# from django.contrib.auth.hashers import check_password         
# @receiver(pre_save, sender=User_login_Data)
# def user_login_data_pre_save(sender, instance, **kwargs):
#     # Check if the instance is being updated (has a primary key)
#     if instance.pk:
#         # Retrieve the original instance from the database
#         original_instance = User_login_Data.objects.get(pk=instance.pk)

#         # Check if the password has changed
#         print("current password", original_instance.PASSWORD)
#         print("New passsword", instance.PASSWORD)
#         if original_instance.PASSWORD == instance.PASSWORD:
#             # Password has changed, execute your custom functionality here
#             print("Password has been not updated. Execute your functionality.")
#         else:
#             print("PASSWORD CHANGE BUT NOT IDENTIFY")
# from auditlog.models import LogEntry

# @receiver(post_save, sender = LogEntry)
# def call_pass(sender, instance, created, **kwargs):
#     val = instance.object_pk # this is use for extract value from instance of primary key
#     print(val)
#     print("Call table cccccccccccccccccccccccccc")
#     if not created:
#         # instance_update.send(sender=MODUL_VIEW_PERMISSION, instance=instance)
#         try:
#             x = LogEntry.objects.get(USERID_id=instance.USERID_id)  #.select_related("USERID").filter(USERID__USERID=instance.USERID_id)
#             print(x)
#             y = THEME_MODULE.objects.get(USERID_THEME_OPT =  x.USERID_THEME_OPT_id)
#             print(y)
#             result_dict = {getattr(y, f"MODEL_{i}") : getattr(x, f"MODEL_{i}") for i in range(1, 11) if getattr(x, f"MODEL_{i}") == True}
#             print(result_dict)
#             s = ", ".join(result_dict.keys())
#             k = User_login_Data.objects.get(USERID=instance.USERID_id)
#             EMAIL = k.EMAIL
#             USERNAME = k.USERNAME
#             print(USERNAME)
#             print(k.SU_APRO_STAT)
#             print(k.AU_APRO_STAT)
#             if k.SU_APRO_STAT == "APPROVED" and k.AU_APRO_STAT == "APPROVED":
#                 send_UU_model_permission(EMAIL, s, USERNAME)
#                 print("FINISHED")
#             else:
#                 pass
            
#         except:
#             print("SOMETHING WENT WORNG")


# from django.dispatch import receiver

# from auditlog.signals import post_save
# from auditlog.models import LogEntry
# from django.db.models.signals import post_save
# @receiver(post_save, sender=LogEntry)
# def handle_post_log(sender, instance, **kwargs):
#     # Your custom logic here
#     print(f'Audit log entry saved for {instance.object_repr}')
            
# class YourModelAuditlogModel(AuditlogHistoryModel):
#     # Additional fields or customization
    # pass

auditlog.register(User_login_Data, mask_fields=['PASSWORD'])
# auditlog.register(password_table)



# @auditlog.register(YourModel)


