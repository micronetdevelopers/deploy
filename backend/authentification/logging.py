import logging
import sys


from django.shortcuts import render,redirect, HttpResponse
from django.http import HttpResponse
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpRequest
from django.contrib import messages
from django.core.mail import send_mail
import uuid
from django.forms.models import model_to_dict  #imp for module to dict
from rest_framework import status
from .models import User_login_Data,Users_login_Details_Data,password_table
from .serializers import *
from rest_framework.response import Response
from .helpers import send_forget_password_mail
from .helpers import *
from django.contrib.auth.hashers import make_password, check_password
# Create your views here.
from django.contrib.auth import authenticate, login
from rest_framework.views import APIView
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from django.contrib.auth.decorators import user_passes_test
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from auditlog.registry import auditlog
from django.db import transaction
import random
import string
from auditlog.context import set_actor



logger = logging.getLogger(__name__) #authentification.logging
# console_handler = logging.StreamHandler(stream = sys.stdout)

# file_handler = logging.FileHandler(filename="D:\logs_django\logs.txt")

# logger.addHandler(console_handler)
# logger.addHandler(file_handler)

# def division(numerator, denominator):
#     try:
#         return numerator/ denominator
#     except ZeroDivisionError:
#         logger.error(f"Division by zero error with parameter: {numerator} / {denominator}")

# if __name__ =="__main__":
#     division(4, 0)



@api_view(['GET','POST', 'PUT','PATCH','DELETE'])
def register_general_test(request): #active
    if request.method =="GET":
        logger.info("Testing the logger!")
        logger.warning("Testing the logger!  warning")
        try:
            # if request.user.USER_TYPE == "SU" and 
            if request.user.USER_TYPE == "SU" or request.user.USER_TYPE == "AU":
                user_login_detail_data = User_login_Data.objects.all().filter(USER_TYPE="GU").exclude(SU_APRO_STAT="DELETE")
                serializer_b = User_login_Data_serialiser112(user_login_detail_data, many=True).data
                data_ser = {
            "serializer_b1": serializer_b
              }
        
                return Response({"message": data_ser}, status=status.HTTP_200_OK)
            
            user = User_login_Data.objects.get(USERNAME=request.user.USERNAME) #for single User
            
        except Exception as e:
            logger.error("user with id %s does not exist", 1)
            return  Response({'message': 'userNot Present'})
        serializer_b = User_login_Data_serialiser112(user).data #UserLoginGeneral
        return Response({'message': serializer_b}, status=status.HTTP_200_OK)
    
    elif request.method =='POST':
         resister_info = request.data
         keys_to_remove = ["SU_APRO_STAT", "AU_APRO_STAT", "APRO_DATE", "SU_APRO_REM", "AU_APRO_REM", "THEME_OPT"]
         auth_register_info_1 = {key: value for key, value in resister_info.items() if key not in keys_to_remove}
         print(resister_info)
         if auth_register_info_1.get("USER_TYPE") =="GU" or auth_register_info_1.get("USER_TYPE") == None:
            serializer = User_login_Data_serialiser112(data=auth_register_info_1)
         else:
             return Response({"Message":"You are Not Authorized"})
         print(serializer)
         if serializer.is_valid():
            serializer.validated_data['SU_APRO_STAT'] = "APPROVED"
            serializer.save()
            GU_resister_mail(serializer.validated_data["EMAIL"], serializer.validated_data["USERNAME"])
            return Response(serializer.data, status=status.HTTP_201_CREATED)
         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method =="PATCH":  #patcxh===================================================
        # if not request.user.USER_TYPE == "SU":
        #         return Response({'message': 'Not Authorized SUPERUSER'}, status=status.HTTP_403_FORBIDDEN)
        auth_register_info = request.data
        # keys_to_remove = ["SU_APRO_STAT", "AU_APRO_STAT", "APRO_DATE", "SU_APRO_REM", "AU_APRO_REM", "THEME_OPT"]
        # auth_register_info_1 = {key: value for key, value in auth_register_info.items() if key not in keys_to_remove}
        try:
            if request.user.USER_TYPE == "SU":
                user = User_login_Data.objects.get(USERID=auth_register_info.get("USERID"))
                if user.USER_TYPE == "GU":
                    auth_register_info_1 = auth_register_info
            elif request.user.USER_TYPE == "GU":
                keys_to_remove = ["SU_APRO_STAT", "AU_APRO_STAT", "APRO_DATE", "SU_APRO_REM", "AU_APRO_REM", "THEME_OPT"]
                auth_register_info_1 = {key: value for key, value in auth_register_info.items() if key not in keys_to_remove}
                user = User_login_Data.objects.get(USERID= request.user.USERID) #Need change here
            # user_detail, created = Users_login_Details_Data.objects.get_or_create(USERID_id=user.USERID)
            # obj = Users_login_Details_Data.objects.get(USERID_id=user.USERID)
            else:
                return Response({'message': 'Not Authorized SUPERUSER or GU'}, status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({"Massege":"User Not allowed xxx"})
        
        if user.USER_TYPE == "GU":
            serializer_a = User_login_Data_serialiser112(user, data= auth_register_info_1, partial=True)
        elif user.USER_TYPE == "SU" and request.user.USER_TYPE == "SU":
            serializer_a = User_login_Data_serialiser112(user, data= auth_register_info, partial=True)
        else:
            return Response({"Massege":"Something Went Wrong"})
        if serializer_a.is_valid():
            requred_field = ["USERNAME", "EMAIL", "MOBILE_NO"]
            new_field = {key: value for key, value in serializer_a.validated_data.items() if key  in requred_field}
            xc = model_to_dict(user)
            result_dict =  {key: value for key,value in xc.items() if key in requred_field}
            result_dict_1 = {key: result_dict[key] for key in result_dict if key in new_field and result_dict[key] != new_field[key]}
            if not result_dict_1:
                print("empty dict")
                pass
            else:
                print("Change in profile")
                mail_change_in_profile_AU_SU(user.EMAIL, user.USERNAME, result_dict_1)
            serializer_a.save()
            response_data = {
                        'serializer_a_data': serializer_a.data,
                    }
            return Response({"data":response_data})
        else:
            return Response({'message': 'Validation error', 'errors': serializer_a.errors}, status=status.HTTP_400_BAD_REQUEST)
    # else:
    #     return Response({'message': 'Not GU USER'}, status=status.HTTP_403_FORBIDDEN)

    elif request.method =="DELETE":   #status=status.HTTP_204_NO_CONTENT
        if not request.user.USER_TYPE == "SU":
            return Response({'message': 'Not Authorized SUPERUSER'}, status=status.HTTP_403_FORBIDDEN)

            # return Response({"message": "User Not allowed"})
        auth_register_info = request.data
        print(auth_register_info.get("USERID"))
        try:
            user = User_login_Data.objects.get(USERID=auth_register_info.get("USERID"))
            print(user)
        except Exception as e:
            return Response({"Message": f"User Not Exist. Error: {str(e)}"} , status=status.HTTP_400_BAD_REQUEST)
        if user.USER_TYPE == "GU":
            print("USER! DELETE")
            user.delete()
            return Response({'detail': 'User deleted successfully'}, status=status.HTTP_200_OK)
        else:
            return Response({'detail': 'User Not GU '}, status=status.HTTP_400_BAD_REQUEST)