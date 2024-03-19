from rest_framework import serializers
from .models import *
from rest_framework import status
import random
from django.contrib.auth.hashers import make_password, check_password
from rest_framework.response import Response #
from django.contrib.auth.hashers import make_password
import string
from django.contrib.auth import get_user_model
from threading import Thread
from .helpers import *
from django.core.validators import MinLengthValidator
# from rest_framework.validators import RegexValidator
from django.core.validators import RegexValidator
from datetime import datetime, date
User = get_user_model()
from datetime import date
class login_seria(serializers.Serializer):#active
    USERNAME = serializers.CharField(required=True, allow_blank=False, max_length=100)
    PASSWORD = serializers.CharField(required=True, allow_blank=False, max_length=100)



class forget_pass_seria(serializers.Serializer): #active
    USERNAME = serializers.CharField(required=True, allow_blank=False, max_length=100)


class contact_us_serialiser(serializers.ModelSerializer):
    class Meta:
        model = contact_us
        fields = ['customer_mail', 'customer_mobile_no', 'catagory', 'comment', 'name']

class SpacelessPasswordValidator(MinLengthValidator): #not working
    def __call__(self, value):
        # Replace spaces and calculate length
        value1 = value.strip()
        if " " in value1 or  not (any(char.isalpha() for char in value1)) or not (any(char.isdigit() for char in value1)) or not (any((x in "!@#$%^&*")  for x in value1)):
            raise serializers.ValidationError("No space and atlest require alphabet and digit and special charector  {!@#$%^&*} ")
        super().__call__(value1)

class mobile_Validator(MinLengthValidator):
    def __call__(self, value):
        # Replace spaces and calculate length
        value1 = value.strip()
        if " " in value1 or not value1.isdigit():
            raise serializers.ValidationError("No space or only digit for the mobile no")
        super().__call__(value1)

name_validator = RegexValidator(
    regex="^[A-Za-z]*$",
    message="Only alphabet characters are allowed."
)

###############################################################################################################################################################################################



class User_login_Data_serialiser112(serializers.ModelSerializer):#active, Post admin, patch admin, post UU, patchUU, post gu patch gu
    # EMAIL = serializers.EmailField(max_length=100)
    MOBILE_NO = serializers.CharField(max_length=10, validators=[mobile_Validator(10, message="Mobile No must be  10 characters.")])
    # PASSWORD = serializers.CharField(max_length=40, validators=[SpacelessPasswordValidator(8, message="Password must be at least 8 characters.")])
    # login_profile_data_seraliser = User_Detail_Data_Serialiser_All_Field112(many=True, read_only=True)
    class Meta:
        model = User
        fields = '__all__'
    
    def validate(self, data):
        if 'USERNAME' in data:
            data['USERNAME'] = data.get("USERNAME", "").replace(" ", "")
        # if 'PASSWORD' in data:
        #     data['PASSWORD'] = data.get("PASSWORD", "").replace(" ", "")
        context = self.context.get("USER_TYPE", "Not in context")
        user_type = data.get('USER_TYPE', "No user_type")
        required_fields_user_types = context
        if user_type == required_fields_user_types:
            for field in ['Q1_ID', 'Q2_ID', 'Q1_AN', 'Q2_AN']:
                 if field not in data:
                    raise serializers.ValidationError(f"{field} is required for user type {user_type}")
                 data['Q1_AN'] = data.get("Q1_AN", "").lower()
                 data['Q2_AN'] = data.get("Q2_AN", "").lower()
        else:
            pass
        
        if 'THEME_OPT' in data:
            if data.get('USER_TYPE') != None:
                if user_type == "AU" or user_type =="UU":
                    if data['THEME_OPT'] in ("", None):
                        raise serializers.ValidationError(f" THEME_OPT is required for user type {user_type}")
                elif user_type =="SU":
                    if data['THEME_OPT'] in ("", None):
                        data['THEME_OPT'] = None
                else:
                    raise serializers.ValidationError(f" check user type {user_type} required only AU, SU, UU")
            else:
                raise serializers.ValidationError(f"required  user type {user_type}")
        return data
    
    

    def validate_EMAIL(self, value):
        norm_email = value.lower().strip()
        if self.instance is None or not self.instance.id:
            if User_login_Data.objects.filter(EMAIL__iexact=norm_email).exists():
                raise serializers.ValidationError("Not unique email")
        elif self.instance.USERID:
            if User_login_Data.objects.filter(EMAIL__iexact=norm_email).exclude(USERID=self.instance.USERID).exists():
                raise serializers.ValidationError("Not unique email")
            return norm_email
        return norm_email

    def create(self, validated_data):
        user = User(**validated_data)
        user.save()
        print(user.id)
        if  user.id is not None:
            user_id_num = str(user.id)
            string_lenth = "000000"
            if len(user_id_num) < 7:
                x = string_lenth[:-len(user_id_num)] + user_id_num
                user.USERID = x
                user.PASSWORD = make_password(user.PASSWORD)
                user.SU_APRO_STAT = "APPROVED"
                user.AU_APRO_STAT = "INPROGRESS"
                user.save()
            else:
                return Response({'message': 'User_id is Full'})
        else:
            return Response({'massage':"user not able to signup"})

        return user
    
    def update(self, instance, validated_data):
        validated_data.pop('USER_TYPE', None)
        # print("EEEEEEEEEEEEEE")
        # print(self.context)
        # print("FFFFFFFFFFFFFFFF")
        # user_type = self.context.get('request').user.USER_TYPE
        # print(user_type)
        # # print(self.USERNAME)
        # print("NAMEEEEEEEEEEEEE")
        if validated_data.get("AU_APRO_STAT") is not None and validated_data.get("AU_APRO_STAT") != "" and instance.USER_TYPE =="UU":
            # instance.AU_APRO_STAT = validated_data.get("AU_APRO_STAT")
            # instance.AU_APRO_REM = validated_data.get("AU_APRO_REM")
            if instance.AU_APRO_STAT == validated_data.get("AU_APRO_STAT"):
                print("Same credantial previous")
                pass
            else:
                print("AU send mail about approval status")
                send_authorised_APPROVED_mail(instance.EMAIL , validated_data.get("AU_APRO_STAT"), validated_data.get("AU_APRO_REM"), instance.USERNAME)
        elif validated_data.get("SU_APRO_STAT") is not None and validated_data.get("SU_APRO_STAT") != "" and  instance.USER_TYPE in ["UU", "GU"]:
            # instance.SU_APRO_STAT = validated_data.get("SU_APRO_STAT")
            # instance.SU_APRO_REM = validated_data.get("SU_APRO_REM")
            if instance.SU_APRO_STAT ==  validated_data.get("SU_APRO_STAT"):
                print("new and old su_approve same")
                pass
            else:
                print("SU send mail to UU about status")
                send_authorised_APPROVED_mail(instance.EMAIL , validated_data.get("SU_APRO_STAT"), validated_data.get("SU_APRO_REM"), instance.USERNAME)
                if instance.USER_TYPE == "UU":
                    try:
                        obj = User_login_Data.objects.filter(THEME_OPT="AU_"+instance.THEME_OPT[3:], AU_APRO_STAT= "INPROGRESS")#vfgvfdgfgfg  
                    except Exception as e:
                        return Response({"error": str(e), "Message":"ADMIN NOT PRESENT IN DATABASE PLESE CREATE"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                    
                    EMAIL = [list(obj.values())[0]["EMAIL"]]
                    x = "SU"
                    mail_Delete_UU_to_admin(EMAIL , instance.USERNAME, validated_data.get("SU_APRO_STAT"), x)
                else:
                    pass

        elif validated_data.get("SU_APRO_STAT") =="BLOCKED" and instance.USER_TYPE =="AU": #implement here unblock email functionality
            OPT = instance.THEME_OPT[3:]
            print(OPT)
            print("UU_"+OPT)
            obj = User_login_Data.objects.all().filter(THEME_OPT="UU_"+OPT, SU_APRO_STAT="APPROVED", AU_APRO_STAT="APPROVED")
            EMAIL_Query = obj.values_list('EMAIL', flat=True)
            EMAIL_ALL = list(EMAIL_Query)
            for instance_1 in obj:
                instance_1.AU_APRO_STAT = "BLOCKED"
                instance_1.save()
            instance.SU_APRO_STAT = validated_data.get("SU_APRO_STAT")
            instance.SU_APRO_REM = validated_data.get("SU_APRO_REM")
            instance.save()
            mass_mail_block_admin(EMAIL_ALL , instance.USERNAME, validated_data.get("SU_APRO_STAT"))
            block_admin_mail(instance.EMAIL, validated_data.get("SU_APRO_STAT"),  validated_data.get("SU_APRO_REM"), instance.USERNAME)
        elif validated_data.get("SU_APRO_STAT") =="APPROVED" and instance.USER_TYPE =="AU" and  instance.AU_APRO_STAT =="INPROGRESS":
            # Email = 
            # x = validated_data.get("SU_APRO_STAT")
            if instance.SU_APRO_STAT == "APPROVED":
                pass
            else:
                re = None
                block_admin_mail(instance.EMAIL, validated_data.get("SU_APRO_STAT"), re, instance.USERNAME)
        else:
            pass
        validated_data.pop('USERID', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
    
    # def save(self, **kwargs):
    #     # Assuming YourModel is the model you want to save data into
    #     instance = User_login_Data(**self.validated_data)
    #     instance.save()
    #     return instance




#second table 
class User_Detail_Data_Serialiser_All_Field112(serializers.ModelSerializer):#active postUU,patchUU,postAU,PATCHAU,getAU,getUU
    FIRST_NAME = serializers.CharField(source="USER_F_NAME",required=True, max_length=20, validators=[name_validator])
    MIDDLE_NAME = serializers.CharField(source="USER_M_NAME", allow_blank=True, required=False, allow_null=True, max_length=20, validators=[name_validator]) #, default="null"
    LAST_NAME = serializers.CharField(source="USER_L_NAME",required=True, max_length=20, validators=[name_validator])
    DOB = serializers.DateField(allow_null=True, required=False, format="%Y-%m-%d", input_formats=["%Y-%m-%d", ""]) #1900-01-01 this date always show null
    ORGANIZATION = serializers.CharField(required=True, max_length=100) #organization
    DESIGNATION = serializers.CharField(required=True, max_length=50)#designation
    CITY = serializers.CharField(required=True, max_length=50)
    STATE = serializers.CharField(required=True, max_length=50)
    COUNTRY = serializers.CharField(required=True, max_length=50)
    login_data_seraliser = User_login_Data_serialiser112(many=True, read_only=True)
    class Meta:
        model = Users_login_Details_Data
        fields = '__all__'
        depth = 1 

    def validate(self, data):
        context = self.context.get("USER_TYPE", "Not in context")
        user_type = self.context.get('USER_TYPE', "No user_type")
        required_fields_user_types =  context 
        if user_type == required_fields_user_types:
            for field in ['ADDRESS_1', 'PIN_CODE']:
                if field not in data:
                    raise serializers.ValidationError(f"{field} is required for user type {user_type}")
                else:
                    if field == "PIN_CODE":
                        value = data.get("PIN_CODE", "")
                        if " " in  value or not value.isdigit() or len(value) < 6:
                            raise serializers.ValidationError(f"{field} is accept only digit 0 to 9 and have 6 digit for {user_type}")
                        else:
                            pass
                    else:
                        pass
        return data
    def validate_DOB(self, value):
        date_string = "1900-01-01"
        date_object = datetime.strptime(date_string, "%Y-%m-%d").date()
        if value == date_object:
            return None  # Convert empty string to null
        return value

    def update(self, instance, validated_data):
        instance.USER_F_NAME = validated_data.get("FIRST_NAME", instance.USER_F_NAME)
        instance.USER_F_NAME = validated_data.get("MIDDLE_NAME", instance.USER_F_NAME)
        instance.USER_F_NAME = validated_data.get("LAST_NAME", instance.USER_F_NAME)
        
        for attr, value in validated_data.items():
            print(attr, value)
            setattr(instance, attr, value)
        instance.save()
        return instance
    

class THEME_MODULE_serialiser(serializers.ModelSerializer):
    class Meta:
        model = THEME_MODULE
        fields = '__all__'

class MODUL_VIEW_PERMISSION_serialiser(serializers.ModelSerializer):
    # USERID = serializers.PrimaryKeyRelatedField(
    #     queryset=User_login_Data.objects.all(),  write_only=True
    # )
    # USERID_THEME_OPT = serializers.PrimaryKeyRelatedField(
    #     queryset=THEME_MODULE.objects.all(), write_only=True
    # )
    thim_model_seraliser = THEME_MODULE_serialiser(read_only=True)
    class Meta:
        model = MODUL_VIEW_PERMISSION
        fields = '__all__'
        depth = 1



