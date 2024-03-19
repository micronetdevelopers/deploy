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
def fty(request):
    return render(request, 'authentification/home.html')

### login api

@api_view(['GET','POST', 'PUT','PATCH','DELETE'])
def forget_password(request):
    if request.method =="GET":
        USERNAME = request.GET.get("USERNAME")
        try:
            obj = User_login_Data.objects.get(USERNAME=request.GET.get("USERNAME"))
            if obj.USER_TYPE == "AU":
                return Response({"USER_TYPE": obj.USER_TYPE, "EMAIL":obj.EMAIL, "USERID":obj.USERID, "USERNAME":obj.USERNAME}, status=status.HTTP_200_OK)
            elif obj.USER_TYPE == "UU":
                if obj.AU_APRO_STAT=="APPROVED" and obj.SU_APRO_STAT=="APPROVED":
                    return Response({"USER_TYPE": obj.USER_TYPE, "EMAIL":obj.EMAIL, "USERID":obj.USERID, "USERNAME":obj.USERNAME, "Q1_ID":obj.Q1_ID,"Q2_ID":obj.Q2_ID}, status=status.HTTP_200_OK)
                else:
                    return Response({"Message": "You have No authority to  Forget Password "}, status=status.HTTP_403_FORBIDDEN)
            else:
                return Response({"Message": "You have No authority to  Forget Password"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"Message":"User Not Exist"}, status=status.HTTP_400_BAD_REQUEST)
    
    elif  request.method == "POST":
        user_info = request.data
        print(user_info)
        serializer = forget_pass_seria(data=user_info)
        if serializer.is_valid():
            x = serializer.validated_data['USERNAME']
            try:
                result = User_login_Data.objects.get(USERNAME=x)
                q1 = result.Q1_AN
                q2 = result.Q2_AN
                print(result)
            except Exception as e:
                return Response({"Message":"USER NOT FOUND"}, status=status.HTTP_403_FORBIDDEN)
            if result.USER_TYPE=="UU":
                if not (q1 == user_info.get("Q1_AN").lower() and q2 == user_info.get("Q2_AN").lower()):
                    return Response({"Message":"Please Provide Correct ANSWER"}, status=status.HTTP_403_FORBIDDEN)
            # if result.exists():-
            #     print(result)
            #     obj = User_login_Data.objects.get(Q(USERNAME=x))
            #     # if obj.USER_TYPE == "GU":
            #     token = str(uuid.uuid4())
            #     x = 1
            #     profile_obj, created = password_table.objects.get_or_create(USERID_id=obj.USERID)
            #     if created:
            #         profile_obj.forget_password_token = token
            #         profile_obj.save()
            #     profile_obj.forget_password_token = token
            #     send_forget_password_mail(obj.EMAIL , token, x)
            #     messages.success(request, 'An email is sent.')
            #     serialized_data = User_login_Data_serialiser(obj).data
            #     print(serialized_data)
            #     profile_obj.save()
            #     return Response({'message': serialized_data, "user":obj.USER_TYPE, "token":token})
            if result.USER_TYPE == "AU" or result.USER_TYPE == "UU":
                print(result)
                letters = string.ascii_letters
                token = ''.join(random.choice(string.digits) for _ in range(6))
                profile_obj, created = password_table.objects.get_or_create(USERID_id=result.USERID)
                if created:
                    profile_obj.forget_password_token = make_password(token)
                profile_obj.forget_password_token = make_password(token)
                profile_obj.save()
                send_forget_password_mail_admin(result.EMAIL , token, result.USERNAME)
                return Response({"Message":"Please Cheak Email For Token", "token": token, "USERID":profile_obj.USERID_id}, status=status.HTTP_200_OK)
            else:
                return Response({"Message":"Invalid Response"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({'message': 'Method Not Allowed'})
            
        # else:
        #     return Response({'message': 'Validation error', 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    #             elif obj.USER_TYPE == "UU":
    #                 obj.appr_status = True
    #                 obj.save()
    #                 token = str(uuid.uuid4())
    #                 profile_obj, created = password_table.objects.get_or_create(user_id=obj.id)
    #                 if created:
    #                     profile_obj.forget_password_token = token
    #                     profile_obj.save()
    #                 profile_obj.forget_password_token = token
    #                 x = 1
    #                 send_forget_password_mail(obj.EMAIL, token, x)
    #                 messages.success(request, 'An email is sent.')
    #                 serialized_data = User_login_Data_serialiser(obj).data
    #                 print(serialized_data)
    #                 profile_obj.save()
    #                 return Response({'message': serialized_data, "user":"authorised", "token":token})
    #             else:
    #                 return Response({'message': 'Not authorised'})
    #         else:
    #             return Response({'message':"No information found"})   
    #     else:
    #         return Response({'message': 'Validation error', 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    # return Response({'message': 'Method not allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


@api_view(['GET','POST', 'PUT','PATCH','DELETE'])
def update_password(request):
    if request.method == "GET":
        x = request.GET.get("token")
        print(x)
        y = request.GET.get("USERID")
        print(y)
        try:
            obj = password_table.objects.get(USERID_id=y)   #status=status.HTTP_400_BAD_REQUEST, status=status.HTTP_403_FORBIDDEN,status=status.HTTP_404_NOT_FOUND
            if check_password(x, obj.forget_password_token):
                return Response({"Message": "MATCH THE CREDENTIAL"}, status=status.HTTP_200_OK)
            else:
                return Response({"Message": "Do not MATCH THE CREDENTIAL"}, status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

    elif request.method == "PATCH":
        password_data = request.data  #token, NEW_PASSWORD, PASSWORD
        keys_to_required = ["USERID", "token", "NEW_PASSWORD", "PASSWORD"]
        password_data_1 = {key: value for key, value in password_data.items() if key  in keys_to_required}
        try:
            obj = password_table.objects.get(USERID_id=password_data_1.get("USERID"))
            if check_password(password_data_1.get("token"), obj.forget_password_token):
                obj = password_table.objects.get(USERID_id = password_data_1.get("USERID"))
                print(password_data_1.get('token'))
                USERID = obj.USERID_id
                print(USERID)
                obj = User_login_Data.objects.get(USERID = USERID) 
                print(obj)
            else:
                  return Response({"Message": "Do not MATCH THE CREDENTIAL"}, status=status.HTTP_200_OK)
        except:
            return Response({"Message":"Link Expired"}, status=status.HTTP_403_FORBIDDEN)
        if password_data_1.get("NEW_PASSWORD") != password_data_1.get("PASSWORD"):
            return Response({"Message":"PASSWORD FIELD NOT MATCH"}, status=status.HTTP_403_FORBIDDEN)
        serializer = User_login_Data_serialiser112(obj, data= password_data_1, partial=True)   #resource, data=request.data, partial=True
        if serializer.is_valid():
            serializer.save()
            obj.PASSWORD = make_password(serializer.validated_data['PASSWORD'])
            obj.save()
            password_change_mail(obj.EMAIL, obj.USERNAME)
            return Response({"Message":"SUCESSFULLY PASSWORD CHANGE", "data": serializer.data}, status=status.HTTP_200_OK)
        else:
            return Response({"Message":serializer.errors}, status=status.HTTP_403_FORBIDDEN)
        
    return Response({'masage':"Method not allow"})


    # elif request.method == "PATCH":
    #     actor = int(request.data.get("USERID"))
    #     # actor = get_user(actor_id)
    #     print("actor_id is print", actor)
    #     with set_actor(actor):
    #         password_data = request.data  #token, NEW_PASSWORD, PASSWORD
    #         keys_to_required = ["USERID", "token", "NEW_PASSWORD", "PASSWORD"]
    #         password_data_1 = {key: value for key, value in password_data.items() if key  in keys_to_required}
    #         try:
    #             obj = password_table.objects.get(USERID_id=password_data_1.get("USERID"))
    #             if check_password(password_data_1.get("token"), obj.forget_password_token):
    #                 obj = password_table.objects.get(USERID_id = password_data_1.get("USERID"))
    #                 print(password_data_1.get('token'))
    #                 USERID = obj.USERID_id
    #                 print(USERID)
    #                 obj = User_login_Data.objects.get(USERID = USERID) 
    #                 print(obj)
    #             else:
    #                 return Response({"Message": "Do not MATCH THE CREDENTIAL"}, status=status.HTTP_200_OK)
    #         except:
    #             return Response({"Message":"Link Expired"}, status=status.HTTP_403_FORBIDDEN)
    #         if password_data_1.get("NEW_PASSWORD") != password_data_1.get("PASSWORD"):
    #             return Response({"Message":"PASSWORD FIELD NOT MATCH"}, status=status.HTTP_403_FORBIDDEN)
    #         serializer = User_login_Data_serialiser112(obj, data= password_data_1, partial=True)   #resource, data=request.data, partial=True
    #         if serializer.is_valid():
    #             serializer.save()
    #             obj.PASSWORD = make_password(serializer.validated_data['PASSWORD'])
    #             obj.save()
    #             password_change_mail(obj.EMAIL, obj.USERNAME)
    #             return Response({"Message":"SUCESSFULLY PASSWORD CHANGE", "data": serializer.data}, status=status.HTTP_200_OK)
    #         else:
    #             return Response({"Message":serializer.errors}, status=status.HTTP_403_FORBIDDEN)
        
    # return Response({'masage':"Method not allow"})
        
    

@api_view(['GET','POST', 'PUT','PATCH','DELETE'])
def register_general(request): #active
    if request.method =="GET":
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
            return  Response({'message': 'userNot Present'}, status=status.HTTP_403_FORBIDDEN)
        serializer_b = User_login_Data_serialiser112(user).data #UserLoginGeneral
        return Response({'message': serializer_b}, status=status.HTTP_200_OK)
    
    elif request.method =='POST':
         resister_info = request.data
         keys_to_remove = ["SU_APRO_STAT", "AU_APRO_STAT", "APRO_DATE", "SU_APRO_REM", "AU_APRO_REM", "THEME_OPT"]
         auth_register_info_1 = {key: value for key, value in resister_info.items() if key not in keys_to_remove}
         if auth_register_info_1.get("USER_TYPE") =="GU" or auth_register_info_1.get("USER_TYPE") == None:
            serializer = User_login_Data_serialiser112(data=auth_register_info_1)
         else:
             return Response({"Message":"You are Not Authorized"}, status=status.HTTP_403_FORBIDDEN)
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
            result_dict_1 = {key: new_field[key] for key in result_dict if key in new_field and result_dict[key] != new_field[key]}
            if not result_dict_1:
                print("empty dict")
                pass
            else:
                print("Change in profile")
                try:
                    remark = remark 
                except:
                    remark= None
                mail_change_in_profile_AU_SU(user.EMAIL, user.USERNAME, result_dict_1, remark)
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
        
        
@api_view(['GET', 'POST', 'PUT', 'PATCH', 'DELETE'])
def login_user(request):
    if request.method == "POST":
        user_info = request.data
        serializer = login_seria(data=user_info)
        if serializer.is_valid():
            user_name = serializer.validated_data['USERNAME']
            user_password = serializer.validated_data['PASSWORD']

            try:
                user = User_login_Data.objects.get(USERNAME=user_name)
                print(user)
            except User_login_Data.DoesNotExist:
                return  Response({'message': 'Invalid UserName'}, status=status.HTTP_401_UNAUTHORIZED)
            if check_password(user_password, user.PASSWORD):
                    if user.USER_TYPE == "SU":
                        access_token = RefreshToken.for_user(user).access_token
                        refresh_token = RefreshToken.for_user(user)
                        print("SU")
                    elif user.USER_TYPE =="AU" and user.SU_APRO_STAT =="APPROVED" and user.AU_APRO_STAT =="INPROGRESS": #approved
                        access_token = RefreshToken.for_user(user).access_token
                        refresh_token = RefreshToken.for_user(user)
                        print("AU")
                    elif user.USER_TYPE =="UU" and user.SU_APRO_STAT =="APPROVED" and user.AU_APRO_STAT=="APPROVED":
                        access_token = RefreshToken.for_user(user).access_token
                        refresh_token = RefreshToken.for_user(user)
                        print("UU")
                    elif user.USER_TYPE =="GU" and user.SU_APRO_STAT =="APPROVED":
                        access_token = RefreshToken.for_user(user).access_token
                        refresh_token = RefreshToken.for_user(user)
                        print("GU")
                    else:
                        return Response({'message': 'You are block'})
                    
                    response_data = {
                    'message': 'Login successful',
                    'access_token': str(access_token),
                    'refresh_token': str(refresh_token),
                    'username':user.USERNAME,
                    'userType':user.USER_TYPE,
                    'userId':user.USERID,
                    'THEME_OPT':user.THEME_OPT
                }

                    return Response(response_data, status=status.HTTP_200_OK)
            else:
                return Response({'message': 'In credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    return Response({'message': 'Method not allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


@api_view(['GET', 'POST', 'PUT', 'PATCH', 'DELETE'])
def user_authorized_function(request): #active
    if request.method == 'GET':
        try:
            authentication_classes = [JWTAuthentication]
            permission_classes = [IsAuthenticated]
            if not (request.user.USER_TYPE == "SU" or request.user.USER_TYPE == "AU" or request.user.USER_TYPE == "UU"):
                return Response({'message': 'Not Authorized SUPERUSER or ADMIN USER'}, status=status.HTTP_403_FORBIDDEN)
        except:
            return Response({'message': 'User Not Authenticate xxx'})
        query_parameters = request.GET
        # print(query_parameters)
        # print(auth_register_info)
        try:
            if request.user.USER_TYPE == "SU" or request.user.USER_TYPE == "AU":
                auth_register_info = request.GET.get("USERID")
                obj = User_login_Data.objects.get(USERID= auth_register_info)
                if not obj.USER_TYPE =="AU":
                    return Response({"message":"Not authorised you"})
                thim_opt = obj.THEME_OPT[3:]
                # print("UU_"+thim_opt)
                user_login_detail_data =  Users_login_Details_Data.objects.select_related("USERID").filter(USERID__THEME_OPT="UU_"+thim_opt).exclude(Q(USERID__AU_APRO_STAT="DELETE") | Q(USERID__SU_APRO_STAT="DELETE"))
            elif request.user.USER_TYPE == "UU":
                obj = User_login_Data.objects.get(USERID= request.user.USERID)
                # thim_opt = obj.THEME_OPT[3:]
                user_login_detail_data =  Users_login_Details_Data.objects.select_related("USERID").filter(USERID__USERID=request.user.USERID).exclude(USERID__AU_APRO_STAT="DELETE")
            else:
                return Response({"Message":"You are Not Authorised"})
        except Exception as e:
            return Response({"Message": "USER ADMIN NOT EXIST"})
            # if not obj.USER_TYPE =="AU":
            #     return Response({"message":"Not authorised you"})
            # thim_opt = obj.THEME_OPT[3:]
            # print("UU_"+thim_opt)
        
        
        cont = len(user_login_detail_data)
        # print(cont)
        if request.GET.get("USERID") is not None and request.GET.get("COUNT")=="COUNT" and len(query_parameters)==2:
            return Response({"COUNT":cont}, status=status.HTTP_200_OK)
        # print(user_login_detail_data)
        list_data = []
        x = 0
        for table_2 in user_login_detail_data:
            empt_dict = {}
            list_data.append(empt_dict)
            list_data[x]["USERNAME"] = table_2.USERID.USERNAME#
            list_data[x]["EMAIL"] = table_2.USERID.EMAIL#
            list_data[x]["MOBILE_NO"] = table_2.USERID.MOBILE_NO#
            list_data[x]["THEME_OPT"] = table_2.USERID.THEME_OPT#
            list_data[x]["COUNTRY"] = table_2.COUNTRY#
            list_data[x]["STATE"] = table_2.STATE#
            list_data[x]["CITY"] = table_2.CITY#
            list_data[x]["ORGANIZATION"] = table_2.ORGANIZATION#
            list_data[x]["DESIGNATION"] = table_2.DESIGNATION#
            list_data[x]["FIRST_NAME"] = table_2.USER_F_NAME#
            list_data[x]["MIDDLE_NAME"] = table_2.USER_M_NAME#
            list_data[x]["LAST_NAME"] = table_2.USER_L_NAME #
            list_data[x]["USERID"] = table_2.USERID.USERID#
            list_data[x]["SU_APRO_REM"] = table_2.USERID.SU_APRO_REM#
            list_data[x]["AU_APRO_REM"] = table_2.USERID.AU_APRO_REM
            list_data[x]["GENDER"] = table_2.GENDER#
            list_data[x]["DOB"] = table_2.DOB#
            list_data[x]["PIN_CODE"] = table_2.PIN_CODE#
            list_data[x]["ADDRESS_1"] = table_2.ADDRESS_1#
            list_data[x]["ADDRESS_2"] = table_2.ADDRESS_2#
            list_data[x]["CREATION_DATE"] = table_2.USERID.CREATION_DATE
            list_data[x]["APRO_DATE"] = table_2.USERID.APRO_DATE
            list_data[x]["USER_TYPE"] = table_2.USERID.USER_TYPE
            list_data[x]["SU_APRO_STAT"] = table_2.USERID.SU_APRO_STAT
            list_data[x]["AU_APRO_STAT"] = table_2.USERID.AU_APRO_STAT
            x = x + 1
        # serializer_a = User_Login_Data_Admin_Serializer(list_data, many=True).data

        serializer_a = User_Detail_Data_Serialiser_All_Field112(user_login_detail_data, many=True).data
        data_ser = {
            "serializer_a1":serializer_a
        }
        # x = 0
        data_info1 = []
        # print(serializer_a)
        for i in serializer_a:
            dict_1 = {}
            d = i["FIRST_NAME"]
            dict_1["USERNAME"] = i['USERID']["USERNAME"]  #very Important code
            dict_1["EMAIL"] = i['USERID']["EMAIL"]
            dict_1["MOBILE_NO"] = i['USERID']["MOBILE_NO"]
            dict_1["THEME_OPT"] = i['USERID']["THEME_OPT"]
            dict_1["USERID"] = i['USERID']["USERID"]
            dict_1["SU_APRO_REM"] = i['USERID']["SU_APRO_REM"]
            dict_1["AU_APRO_REM"] = i['USERID']["AU_APRO_REM"]
            dict_1["CREATION_DATE"] = i['USERID']["CREATION_DATE"]
            dict_1["APRO_DATE"] = i['USERID']["APRO_DATE"]
            dict_1["USER_TYPE"] = i['USERID']["USER_TYPE"]
            dict_1["SU_APRO_STAT"] = i['USERID']["SU_APRO_STAT"]
            dict_1["AU_APRO_STAT"] = i['USERID']["AU_APRO_STAT"]
            dict_1["UU_REM"] = i["UU_REM"]#
            dict_1["COUNTRY"] = i["COUNTRY"]
            dict_1["STATE"] = i["STATE"]
            dict_1["CITY"] = i["CITY"]
            dict_1["ORGANIZATION"] = i["ORGANIZATION"]
            dict_1["DESIGNATION"] = i["DESIGNATION"]
            dict_1["FIRST_NAME"] = i["FIRST_NAME"]
            dict_1["MIDDLE_NAME"] = i["MIDDLE_NAME"]
            dict_1["LAST_NAME"] = i["LAST_NAME"]
            dict_1["GENDER"] = i["GENDER"]
            dict_1["DOB"] = i["DOB"]
            dict_1["PIN_CODE"] = i["PIN_CODE"]
            dict_1["ADDRESS_1"] = i["ADDRESS_1"]
            dict_1["ADDRESS_2"] = i["ADDRESS_2"]
            # dict["MIDDLE_NAME"] = i["MIDDLE_NAME"]
            # print(d)
            data_info1.append(dict_1)
        #     x = x + 1
        # print(data_info1)
        # # USERNAME = serializer_a["USERID"]["USERNAME"]
        # print(USERNAME)
        # return Response({"message":data_ser}, status=status.HTTP_200_OK)
        return Response({"message":data_info1}, status=status.HTTP_200_OK)  #"massage_2":data_ser,

    elif request.method == 'POST':
        auth_register_info = request.data
        auth_register_info1 = [d for d in auth_register_info if d.get('USER_TYPE')  is not None and d.get('THEME_OPT') is not None]
        keys_to_remove = ["SU_APRO_STAT", "AU_APRO_STAT", "APRO_DATE", "SU_APRO_REM", "AU_APRO_REM"]
        auth_register_info2 = [{key:value for key, value in d.items()if key not in keys_to_remove} for d in auth_register_info1 if d.get('USER_TYPE')=="UU" and d.get("USER_TYPE")==d.get("THEME_OPT")[:2]]
        if not auth_register_info2:
            return Response({"Massage":"You are not authorised"}, status=status.HTTP_403_FORBIDDEN) 
        serializer_a = User_login_Data_serialiser112(data=auth_register_info2, context={'USER_TYPE': "UU"}, many=True)   
        serializer_b = User_Detail_Data_Serialiser_All_Field112(data=auth_register_info2,context={'USER_TYPE': "UU"}, many=True)
        if serializer_a.is_valid() and serializer_b.is_valid():
            # serializer_a.validated_data['SU_APRO_STAT'] = "APPROVED"
            # serializer_a.validated_data['AU_APRO_STAT'] = "INPROGRESS"
            serializer_a.save()
            data_a = [dict(data) for data in serializer_a.data]
            data_b = [dict(data) for data in serializer_b.data]
            desired_key1 = 'USERNAME'
            desired_key2 = 'EMAIL'
            serializer_a_data = [[d[desired_key1],d[desired_key2]]  for d in data_a]
            x = 0
            for USERNAME in serializer_a_data:
                user_info = User_login_Data.objects.get(USERNAME = USERNAME[0])
                new_id = user_info.USERID
                new_info = Users_login_Details_Data(USERID_id=new_id,
                            USER_F_NAME=data_b[x].get('FIRST_NAME'),
                            USER_M_NAME=data_b[x].get("MIDDLE_NAME"),USER_L_NAME=data_b[x].get('LAST_NAME'),GENDER=data_b[x].get('GENDER'),
                            DOB=data_b[x].get("DOB"),ORGANIZATION=data_b[x].get("ORGANIZATION"),DESIGNATION=data_b[x].get("DESIGNATION"),
                            ADDRESS_1=data_b[x].get("ADDRESS_1"),ADDRESS_2=data_b[x].get("ADDRESS_2"),CITY= data_b[x].get("CITY"),
                            STATE=data_b[x].get("STATE"),COUNTRY=data_b[x].get("COUNTRY"),PIN_CODE=data_b[x].get("PIN_CODE"),
                            UU_REM=data_b[x].get("UU_REM"))
                THEME_OPT = serializer_a.validated_data[x]["THEME_OPT"]
                THEME_TYPE = THEME_OPT[3:]
                obj = THEME_MODULE.objects.get(THEME_TYPE=THEME_TYPE)
                user_detail = MODUL_VIEW_PERMISSION.objects.create(USERID_id=new_id, USERID_THEME_OPT_id= obj.USERID_THEME_OPT)
                new_info.save()
                # print("zzzzzzzzzgggggggggggggggggggzzzzz")
                # THEME_OPT = serializer_a.validated_data.get["THEME_OPT"]
                # print("zzzzzzzzzzzzzz")
                # print(THEME_OPT)
                # THEME_TYPE = THEME_OPT[3:]
                # print(THEME_TYPE)
                # obj = THEME_MODULE.objects.get(THEME_TYPE=THEME_TYPE)
                # print(obj.USERID_THEME_OPT)
                # user_detail = MODUL_VIEW_PERMISSION.objects.create(USERID_id=new_id, USERID_THEME_OPT_id= obj.USERID_THEME_OPT)
                EMAIL = USERNAME[1]
                UU_resister_mail(EMAIL, USERNAME[0])
                x = x+1
            serializer_a_1 = serializer_a.data
            serializer_b_1 = serializer_b.data
            response_data = {
                    'serializer_a_data': serializer_a_1,
                    'serializer_b_data': serializer_b_1,
                }
            return Response({'masage':'authorised', 'response_data':response_data}, status=status.HTTP_201_CREATED)
        else:
                errors = {
            'serializer_a': serializer_a.errors if not serializer_a.is_valid() else None,
            'serializer_b': serializer_b.errors if not serializer_b.is_valid() else None,
        }
                return Response({'message': 'Validation error', 'errors': errors}, status=status.HTTP_400_BAD_REQUEST)

    elif request.method =="PATCH":  #patcxh===================================================
        auth_register_info = request.data
        print(auth_register_info)
        try:
            if request.user.USER_TYPE == "GU":
                user = User_login_Data.objects.get(USERNAME=request.user.USERNAME)
                print("ccccccc")
                auth_register_info = request.data
                print(auth_register_info)
                keys_to_remove = ["SU_APRO_STAT", "AU_APRO_STAT", "APRO_DATE", "SU_APRO_REM", "AU_APRO_REM","PASSWORD"]
                auth_register_info_1 = {key: value for key, value in auth_register_info.items() if key not in keys_to_remove}
                # print(user.USERID)
                user_detail, created = Users_login_Details_Data.objects.get_or_create(USERID_id=user.USERID)
                print("ppppppp")
                # obj = Users_login_Details_Data.objects.get(USERID_id=user.USERID)
                THEME_OPT = auth_register_info.get("THEME_OPT")
                THEME_TYPE = THEME_OPT[3:]
                # print(THEME_TYPE)
                obj1 = THEME_MODULE.objects.get(THEME_TYPE=THEME_TYPE)
                serializer_a = User_login_Data_serialiser112(user, data= auth_register_info_1, context={'USER_TYPE': "UU"}, partial=True)
                serializer_b = User_Detail_Data_Serialiser_All_Field112(user_detail,  data =auth_register_info_1, context={'USER_TYPE': "UU"}, partial=True)
                if serializer_a.is_valid() and serializer_b.is_valid():
                    
                    permission_module = MODUL_VIEW_PERMISSION.objects.create(USERID_id=user.USERID, USERID_THEME_OPT_id= obj1.USERID_THEME_OPT)
                    serializer_a.save()
                    serializer_b.save()
                    user.USER_TYPE = "UU"
                    user.save()
                    UU_resister_mail(user.EMAIL, user.USERNAME)
                    print("FINISHED")
                    response_data = {
                    'serializer_a_data': serializer_a.data,
                    'serializer_b_data':  serializer_b.data,
                }
            
                    return Response({"data":response_data}, status=status.HTTP_200_OK)
                else:
                    errors = {
                    'serializer_a': serializer_a.errors if not serializer_a.is_valid() else None,
                    'serializer_b': serializer_b.errors if not serializer_b.is_valid() else None,
                }
                    return Response({'message': 'Validation error', 'errors': errors}, status=status.HTTP_400_BAD_REQUEST)
                
            elif request.user.USER_TYPE == "SU":     
                auth_register_info = request.data
                user = User_login_Data.objects.get(USERID=auth_register_info.get("USERID"))
                if user is  None:
                    return Response({"Massage":"No user found"}, status=status.HTTP_400_BAD_REQUEST)
                obj, created = Users_login_Details_Data.objects.get_or_create(USERID_id=user.USERID)
                # obj = Users_login_Details_Data.objects.get(USERID_id=user.USERID)
            elif request.user.USER_TYPE == "AU":
                auth_register_info = request.data
                keys_to_remove = ["SU_APRO_STAT", "SU_APRO_REM","PASSWORD", "THEME_OPT", "EMAIL"]
                auth_register_info = {key: value for key, value in auth_register_info.items() if key not in keys_to_remove}
                user = User_login_Data.objects.get(USERID=auth_register_info.get("USERID"))
                if user is not None:
                    if user.THEME_OPT[3:] != request.user.THEME_OPT[3:]:
                        return Response({"Message":"AU and UU Credintial Not Match"}, status=status.HTTP_400_BAD_REQUEST)
                    else:
                        pass
                else:
                    return Response({"Massage":"No user found"}, status=status.HTTP_400_BAD_REQUEST)
                obj, created = Users_login_Details_Data.objects.get_or_create(USERID_id=user.USERID)
                # obj = Users_login_Details_Data.objects.get(USERID_id=user.USERID)
                # print(auth_register_info)
                print("aaaaaaaaaaaaaaaaaaaa")
                # user = User_login_Data.objects.get(USERID=auth_register_info.get("USERID"))
                # if request.user.USER_TYPE == "AU":
                #     user.SU_APRO_STAT = "BLOCKED"
                # print(user)
                

                # user_detail, created = MODEL_PERMISSION.objects.get_or_create(USERID_id=user.USERID)
                # obj1  = MODEL_PERMISSION.objects.get(USERID_id=user.USERID)
            elif request.user.USER_TYPE == "UU":
                user = User_login_Data.objects.get(USERID=request.user.USERID)
                auth_register_info = request.data
                keys_to_remove = ["SU_APRO_STAT", "AU_APRO_STAT", "APRO_DATE", "SU_APRO_REM", "AU_APRO_REM", "THEME_OPT","PASSWORD", "EMAIL"]
                auth_register_info_1 = {key: value for key, value in auth_register_info.items() if key not in keys_to_remove}
                # print(user.USERID)
                user_detail, created = Users_login_Details_Data.objects.get_or_create(USERID_id=user.USERID)
                serializer_a = User_login_Data_serialiser112(user, data= auth_register_info_1, partial=True)
                serializer_b = User_Detail_Data_Serialiser_All_Field112(user_detail,  data =auth_register_info_1,  partial=True)
                if serializer_a.is_valid() and serializer_b.is_valid():
                    serialized_data = serializer_b.validated_data
                    serialized_data_1 = serializer_a.validated_data
                    print("all data seraliser", dict(serialized_data))
                    print("all data seraliser_1", dict(serialized_data_1))
                    # keys_to_ignore = ['PASSWORD','SU_APRO_STAT','AU_APRO_STAT', 'APRO_DATE', "SU_APRO_REM", "AU_APRO_REM", "CREATION_DATE"]
                    result_dict_1 = {key: value for key, value in serialized_data_1.items()}
                    result_dict_1.update(serialized_data)
                    zx = model_to_dict(user)
                    zy = model_to_dict(user_detail)
                    zx.update(zy)
                    keys_to_required = ['USERID','USERNAME','USER_TYPE', 'EMAIL', "MOBILE_NO", "THEME_OPT", "USER_F_NAME", "USER_L_NAME", "USER_M_NAME", "DOB","ORGANIZATION","DESIGNATION","CITY","STATE","COUNTRY","GENDER","ADDRESS_1","ADDRESS_2","PIN_CODE"]
                    old_data_dict = {key: value for key,value in zx.items() if key in keys_to_required}
                    result_dict = {key: result_dict_1[key] for key in old_data_dict if key in result_dict_1 and result_dict_1[key] != old_data_dict[key]}
                    if not result_dict:
                        pass
                    else:
                        print("dict have something")
                        try:
                            remark = remark 
                        except:
                            remark= None
                        mail_change_in_profile_AU_SU(user.EMAIL , user.USERNAME, result_dict, remark)
                    serializer_a.save()
                    serializer_b.save()
                    response_data = {
                    'serializer_a_data': serializer_a.data,
                    'serializer_b_data':  serializer_b.data,
                }
            
                    return Response({"data":response_data}, status=status.HTTP_200_OK)
                else:
                    errors = {
                    'serializer_a': serializer_a.errors if not serializer_a.is_valid() else None,
                    'serializer_b': serializer_b.errors if not serializer_b.is_valid() else None,
                }
                    return Response({'message': 'Validation error', 'errors': errors}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"Massage":"No User Found"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"Massege":"User Not allowed xxx"})
        print(obj)
        user_detail, created = MODUL_VIEW_PERMISSION.objects.get_or_create(USERID_id = auth_register_info.get("USERID"))
                                                                                                                                                                    
        if user_detail.USERID_THEME_OPT_id is None:
            if request.user.USER_TYPE == "AU":
                THEME_TYPE = request.user.THEME_OPT[3:]
                obj_thim = THEME_MODULE.objects.get(THEME_TYPE=THEME_TYPE)
                if auth_register_info.get("USERID") is None:
                    return Response({"Message":"Required USERID"}, status=status.HTTP_400_BAD_REQUEST)
                # user_detail, created = MODUL_VIEW_PERMISSION.objects.get_or_create(USERID_id = auth_register_info.get("USERID"))
                auth_register_info['AU_ID'] = request.user.USERID
                if created:
                    print(THEME_TYPE)
                    # auth_register_info['THEME_TYPE'] = THEME_TYPE
                    print(obj_thim)
                    auth_register_info['AU_ID'] = request.user.USERID             #for AU ID update
                    # auth_register_info['USERID_THEME_OPT'] = obj_thim.USERID_THEME_OPT
                    print(auth_register_info)
                # user_info = User_login_Data.objects.get(USERID=auth_register_info.get("USERID"))
                # serializer_b = User_login_Data_serialiser112(user_info, data= auth_register_info, partial=True)
                serializer_c = MODUL_VIEW_PERMISSION_serialiser(user_detail, data= auth_register_info, partial=True)

            else:
                # user_info = User_login_Data.objects.get(USERID=auth_register_info.get("USERID"))
                THEME_OPT = auth_register_info.get("THEME_OPT")
                if THEME_OPT is None:
                    THEME_OPT = user.THEME_OPT
                    if THEME_OPT is not None:
                        THEME_TYPE = THEME_OPT[3:]
                        obj_thim = THEME_MODULE.objects.get(THEME_TYPE= THEME_TYPE)
                    else: 
                        return Response({"Message":"Required THEME OPTION"})
                else:
                    THEME_TYPE = THEME_OPT[3:]
                    obj_thim = THEME_MODULE.objects.get(THEME_TYPE= THEME_TYPE)
                serializer_c = MODUL_VIEW_PERMISSION_serialiser(user_detail, data= auth_register_info, partial=True)
        else:
            obj_thim = THEME_MODULE.objects.get(USERID_THEME_OPT= user_detail.USERID_THEME_OPT_id)
            if request.user.USER_TYPE == "AU" or request.user.USER_TYPE == "SU":
                # x = request.user.USER_TYPE0
                auth_register_info['AU_ID'] = request.user.USERID
                serializer_c = MODUL_VIEW_PERMISSION_serialiser(user_detail, data= auth_register_info, partial=True)

        serializer_a = User_login_Data_serialiser112(user, data= auth_register_info, partial=True)
        serializer_b = User_Detail_Data_Serialiser_All_Field112(obj,  data =auth_register_info, partial=True)

        if serializer_a.is_valid() and serializer_b.is_valid() and serializer_c.is_valid():
            serializer_c.validated_data['USERID_THEME_OPT_id'] =  obj_thim.USERID_THEME_OPT
            serialized_data = serializer_b.validated_data
            serialized_data_1 = serializer_a.validated_data
            keys_to_ignore = ['PASSWORD','SU_APRO_STAT','AU_APRO_STAT', 'APRO_DATE',  "CREATION_DATE"]
            result_dict_1 = {key: value for key, value in serialized_data_1.items() if key not in keys_to_ignore}
            result_dict_1.update(serialized_data)
            zx = model_to_dict(user)
            zy = model_to_dict(obj)
            zx.update(zy)
            keys_to_required = ['USERID','USERNAME','USER_TYPE', 'EMAIL', "MOBILE_NO", "THEME_OPT", "USER_F_NAME", "USER_L_NAME", "USER_M_NAME", "DOB","ORGANIZATION","DESIGNATION","CITY","STATE","COUNTRY","GENDER","ADDRESS_1","ADDRESS_2","PIN_CODE","SU_APRO_REM", "AU_APRO_REM"]
            old_data_dict = {key: value for key,value in zx.items() if key in keys_to_required}
            result_dict = {key: result_dict_1[key] for key in old_data_dict if key in result_dict_1 and result_dict_1[key] != old_data_dict[key]}
            if not result_dict:
                pass
            else:
                try:
                    if request.user.USER_TYPE == "SU":
                        remark = dict(serialized_data_1).get("SU_APRO_REM")
                    elif request.user.USER_TYPE == "AU":
                        remark = dict(serialized_data_1).get("AU_APRO_REM")
                except:
                    remark= None
                print("dict have something")
                if len(result_dict)== 1 and (("SU_APRO_REM" in result_dict and result_dict["SU_APRO_REM"] is not None)  or  ("AU_APRO_REM" in result_dict and result_dict["AU_APRO_REM"] is not None)):
                    result_dict = None
                    try:
                        if request.user.USER_TYPE == "SU":
                            remark = dict(serialized_data_1).get("SU_APRO_REM")
                            su_apro_stat = dict(serialized_data_1).get("SU_APRO_STAT")
                            if user.SU_APRO_STAT == su_apro_stat or su_apro_stat is None:
                                if (remark is None or remark == ""):
                                    pass
                                else:
                                    mail_change_in_profile_AU_SU(user.EMAIL , user.USERNAME, result_dict, remark)

                        elif request.user.USER_TYPE == "AU":
                            remark = dict(serialized_data_1).get("AU_APRO_REM")
                            au_apro_stat = dict(serialized_data_1).get("AU_APRO_STAT")
                            if user.AU_APRO_STAT == au_apro_stat or au_apro_stat is None:
                                if (remark is None or remark == ""):
                                    pass
                                else:
                                    mail_change_in_profile_AU_SU(user.EMAIL , user.USERNAME, result_dict, remark)
                    except:
                        remark= None
                    
                    
                    # print(su_apro_stat) #aprove or None
                    # print(au_apro_stat)
                    # # if remark is None or remark == "" and user.SU_APRO_STAT != dict(serialized_data_1).get("SU_APRO_STAT") or user.AU_APRO_STAT != dict(serialized_data_1).get("AU_APRO_STAT"):
                    # # and (user.SU_APRO_STAT != dict(serialized_data_1).get("SU_APRO_STAT") or user.AU_APRO_STAT != dict(serialized_data_1).get("AU_APRO_STAT")):
                    # if user.SU_APRO_STAT == su_apro_stat or user.AU_APRO_STAT == au_apro_stat:
                    #     print("RRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRR")
                    #     if (remark is None or remark == ""):
                    #         pass
                    #     else:
                    #         print('MAIL GOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO')
                    #         mail_change_in_profile_AU_SU(user.EMAIL , user.USERNAME, result_dict, remark)
                    # else:
                    #     if su_apro_stat == None or  au_apro_stat == None:
                    #         print('MAIL GOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO')
                    #         mail_change_in_profile_AU_SU(user.EMAIL , user.USERNAME, result_dict, remark)
                    #     else:
                    #         pass
                else:

                    # try:
                    #     if request.user.USER_TYPE == "SU":
                    #         remark = dict(serialized_data_1).get("SU_APRO_REM")
                    #     elif request.user.USER_TYPE == "AU":
                    #         remark = dict(serialized_data_1).get("AU_APRO_REM")
                    # except:
                    #     remark= None
                    result_dict = {key:result_dict[key] for key in result_dict if key not in ("SU_APRO_REM", "AU_APRO_REM")}
                    mail_change_in_profile_AU_SU(user.EMAIL , user.USERNAME, result_dict, remark)
            serializer_a.save()
            serializer_b.save()
            if user_detail.USERID_THEME_OPT_id == serializer_c.validated_data['USERID_THEME_OPT_id']:
                print("USERID_THEME_OPT_id is same as old")
                au_id_value = serializer_c.validated_data.get('AU_ID', None)
                if au_id_value is None or au_id_value== user_detail.AU_ID:
                    print("There is no au_id-value")
                    serializer_c_1 = serializer_c.validated_data
                    new_permission = {key: value for key, value in serializer_c_1.items() if key not in ["AU_ID", "USERID_THEME_OPT_id"]}
                    zx = model_to_dict(user_detail)
                    old_permission ={key: value for key, value in zx.items() if key not in ["AU_ID", "USERID_THEME_OPT_id"]}
                    final_per_dict = {key: old_permission[key] for key in old_permission if key in new_permission and old_permission[key] != new_permission[key]}
                    if not final_per_dict:
                        print("No change in module permission")
                        pass
                    else:
                        print("change in module permission")
                        serializer_c.save()
                else:
                    if  request.user.USER_TYPE == "SU":
                        pass  #if you want to save permission from SU 
                        # serializer_c.save()    #uncomment
                    else:
                        print("au id change")
                        serializer_c_1 = serializer_c.validated_data
                        new_permission = {key: value for key, value in serializer_c_1.items() if key not in ["AU_ID", "USERID_THEME_OPT_id"]}
                        zx = model_to_dict(user_detail)
                        old_permission ={key: value for key, value in zx.items() if key not in ["AU_ID", "USERID_THEME_OPT_id"]}
                        final_per_dict = {key: old_permission[key] for key in old_permission if key in new_permission and old_permission[key] != new_permission[key]}
                        if not final_per_dict:
                            print("No change in module permission")
                            pass
                        else:
                            print("change in module permission")
                            serializer_c.save()
                        # serializer_c.save()   #code working if require uncomment
                        # pass
            else:
                print("Thim change")
                serializer_c.save()  # code working if require uncomment
            response_data = {
                    'serializer_a_data': serializer_a.data,
                    'serializer_b_data':  serializer_b.data,
                    'serializer_c_data':  serializer_c.data,
                }
            
            return Response({"data":response_data}, status=status.HTTP_200_OK)
        else:
            errors = {
            'serializer_a': serializer_a.errors if not serializer_a.is_valid() else None,
            'serializer_b': serializer_b.errors if not serializer_b.is_valid() else None,
            'serializer_c': serializer_c.errors if not serializer_c.is_valid() else None,
        }
            return Response({'message': 'Validation error', 'errors': errors}, status=status.HTTP_400_BAD_REQUEST)

    elif request.method =="DELETE":   #status=status.HTTP_204_NO_CONTENT
            auth_register_info = request.data
            try:
                user = User_login_Data.objects.get(USERID=auth_register_info.get("USERID"))
            except:
                return Response({"message": "User not found"}, status=status.HTTP_404_NOT_FOUND)
            if user.USER_TYPE == "UU":
                status_DE = "DELETE"
                reason = "-"
                OPT = user.THEME_OPT[3:]
                print(OPT)
                print("AU_"+OPT)
                try:
                    obj = User_login_Data.objects.filter(THEME_OPT="AU_"+OPT, AU_APRO_STAT ="INPROGRESS").first()  #.exclude(AU_APRO_STAT="DELETE")
                except Exception as e:
                    return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                EMAIL_Query = obj.EMAIL
                EMAIL_ALL = [EMAIL_Query]
                print(EMAIL_ALL)
                status_DE = "DELETE"
                if request.user.USER_TYPE =="SU":
                    x = "SU"
                else:
                    x = "AU"
                Delete_UU_mail_to_UU(user.EMAIL, status_DE, user.USERNAME, obj.EMAIL, x)
                mail_Delete_UU_to_admin(EMAIL_ALL , user.USERNAME, status_DE, x) #go to admin for UU Delete
                user.delete()
                return Response({'detail': 'User deleted successfully'}, status=status.HTTP_200_OK)
            else:
                return Response({"message": "User not UU"}, status=status.HTTP_404_NOT_FOUND)
        # except User_login_Data.DoesNotExist:
        #     return Response({"message": "User not found"}, status=status.HTTP_404_NOT_FOUND)
    else:
        return Response({'message': 'Invalid HTTP method'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
   




@api_view(['GET', 'POST', 'PUT', 'PATCH', 'DELETE'])
def admin_function(request):          # active
    if request.method == 'GET':
        try:
            authentication_classes = [JWTAuthentication]
            permission_classes = [IsAuthenticated]
            if not (request.user.USER_TYPE == "SU" or request.user.USER_TYPE == "AU"):
                return Response({'message': 'Not Authorized SUPERUSER'}, status=status.HTTP_403_FORBIDDEN)
        except:
            return Response({'message': 'User Not Authenticate xxx'})
        
        if request.user.USER_TYPE == "SU":
            user_login_detail_data =  Users_login_Details_Data.objects.select_related("USERID").filter(USERID__USER_TYPE="AU").exclude(USERID__AU_APRO_STAT="DELETE")# SU_APPROVE AND AU_APPROVE Not consider yet
        else:
            user_login_detail_data =  Users_login_Details_Data.objects.select_related("USERID").filter(USERID__USERID=request.user.USERID)
        list_data = []
        x = 0
        for table_2 in user_login_detail_data:
            empt_dict = {}
            list_data.append(empt_dict)
            list_data[x]["USERNAME"] = table_2.USERID.USERNAME
            list_data[x]["EMAIL"] = table_2.USERID.EMAIL
            list_data[x]["MOBILE_NO"] = table_2.USERID.MOBILE_NO
            list_data[x]["THEME_OPT"] = table_2.USERID.THEME_OPT
            list_data[x]["COUNTRY"] = table_2.COUNTRY
            list_data[x]["STATE"] = table_2.STATE
            list_data[x]["CITY"] = table_2.CITY
            list_data[x]["ORGANIZATION"] = table_2.ORGANIZATION
            list_data[x]["DESIGNATION"] = table_2.DESIGNATION
            list_data[x]["FIRST_NAME"] = table_2.USER_F_NAME
            list_data[x]["MIDDLE_NAME"] = table_2.USER_M_NAME
            list_data[x]["LAST_NAME"] = table_2.USER_L_NAME 
            list_data[x]["USERID"] = table_2.USERID_id
            list_data[x]["OFF_LOCA"] = table_2.OFF_LOCA
            list_data[x]["ALT_EMAIL"] = table_2.ALT_EMAIL
            list_data[x]["LAN_LINE"] = table_2.LAN_LINE
            list_data[x]["SU_APRO_STAT"] = table_2.USERID.SU_APRO_STAT
            list_data[x]["AU_APRO_STAT"] = table_2.USERID.AU_APRO_STAT
            list_data[x]["SU_APRO_REM"] = table_2.USERID.SU_APRO_REM
            list_data[x]["CREATION_DATE"] = table_2.USERID.CREATION_DATE
            list_data[x]["APRO_DATE"] = table_2.USERID.APRO_DATE 

            x = x + 1
        # serializer_b = User_Login_Data_Serialiser_All_Field(list_data, many=True).data
        serializer_b = User_Detail_Data_Serialiser_All_Field112(user_login_detail_data, many=True).data   #New Added

        data_ser = {
            "serializer_b1":serializer_b
        }
        # return Response({"message":data_ser})
    
        data_info1 = []
        print(serializer_b)
        for i in serializer_b:
            dict_1 = {}
            dict_1["USERNAME"] = i['USERID']["USERNAME"]  #very Important code
            dict_1["EMAIL"] = i['USERID']["EMAIL"]
            dict_1["MOBILE_NO"] = i['USERID']["MOBILE_NO"]
            dict_1["THEME_OPT"] = i['USERID']["THEME_OPT"]
            dict_1["USERID"] = i['USERID']["USERID"]
            dict_1["SU_APRO_REM"] = i['USERID']["SU_APRO_REM"]
            dict_1["CREATION_DATE"] = i['USERID']["CREATION_DATE"]
            dict_1["USER_TYPE"] = i['USERID']["USER_TYPE"]
            dict_1["SU_APRO_STAT"] = i['USERID']["SU_APRO_STAT"]
            dict_1["COUNTRY"] = i["COUNTRY"]
            dict_1["STATE"] = i["STATE"]
            dict_1["CITY"] = i["CITY"]
            dict_1["ORGANIZATION"] = i["ORGANIZATION"]
            dict_1["DESIGNATION"] = i["DESIGNATION"]
            dict_1["FIRST_NAME"] = i["FIRST_NAME"]
            dict_1["MIDDLE_NAME"] = i["MIDDLE_NAME"]
            dict_1["LAST_NAME"] = i["LAST_NAME"]
            dict_1["OFF_LOCA"] = i["OFF_LOCA"]
            dict_1["ALT_EMAIL"] = i["ALT_EMAIL"]
            dict_1["LAN_LINE"] = i["LAN_LINE"]
            dict_1["APRO_DATE"] = i['USERID']["APRO_DATE"]
            data_info1.append(dict_1)
        #     x = x + 1
        # print(data_info1)
        # # USERNAME = serializer_a["USERID"]["USERNAME"]
        # print(USERNAME)
        # return Response({"message":data_ser}, status=status.HTTP_200_OK)
        return Response({"message":data_info1}, status=status.HTTP_200_OK) #"massage_2":data_ser, 

    elif request.method == 'POST':
        try:
            authentication_classes = [JWTAuthentication]
            permission_classes = [IsAuthenticated]
            if not request.user.USER_TYPE == "SU":
                return Response({'message': 'Not Authorized SUPERUSER'}, status=status.HTTP_403_FORBIDDEN)
        except:
            return Response({'message': 'User Not Authenticate xxx'})
        
        auth_register_info = request.data
        for i in auth_register_info:
            if i.get("ADMIN_DELETE")=="777":
                try:
                    obj = User_login_Data.objects.filter(THEME_OPT__exact=i.get("THEME_OPT"), AU_APRO_STAT__exact="INPROGRESS").first()
                    if obj is not None:
                        obj.AU_APRO_STAT = "DELETE"
                        obj.save()
                        xc = None
                        block_admin_mail(obj.EMAIL, obj.AU_APRO_STAT, xc, obj.USERNAME)
                except Exception as e:
                    return Response({"Message":{e}})
                # result_queryset = YourModel.objects.filter(column1__exact=column1_value, column2__exact=column2_value)
            else:
                pass
        list_value = User_login_Data.objects.exclude(AU_APRO_STAT='DELETE').values_list('THEME_OPT', flat=True)
        auth_register_info1 = [d for d in auth_register_info if d.get('USER_TYPE')  is not None and d.get('THEME_OPT') is not None]
        print(auth_register_info1)
        seen_c_values = set()
        filtered_X = []
        for d in auth_register_info1:
            if d['THEME_OPT'] not in seen_c_values:
                seen_c_values.add(d['THEME_OPT'])
                filtered_X.append(d)
        print(filtered_X)
        auth_register_info2 = [d for d in filtered_X if d.get('USER_TYPE')=="AU" and d.get("USER_TYPE")==d.get("THEME_OPT")[:2] and d.get("THEME_OPT") not in list_value]
        if not auth_register_info2:
            return Response({"Massage":"You cannot create a user with a theme that already exists."}, status=status.HTTP_403_FORBIDDEN)
        print(auth_register_info2)
        list_data = []   #main data
       
        for data in auth_register_info2:
            if data.get("PASSWORD") is None:
                special_chars = "!@#$%^&*"
                letters = string.ascii_letters
                digits = string.digits
                password_list = [random.choice(special_chars), random.choice(letters), random.choice(digits)]
                remaining_length = 5
                password_list.extend(random.choice(letters + digits + special_chars) for _ in range(remaining_length))
                random.shuffle(password_list)
                PASSWORD = ''.join(password_list)
                print(PASSWORD,  len(PASSWORD))
                data["PASSWORD"] = PASSWORD
                # data["ADDRESS_1"] = "Null"
                # data["PIN_CODE"] = "Null"
                list_data.append(data)
        serializer_a = User_login_Data_serialiser112(data=list_data, many=True)   
        serializer_b = User_Detail_Data_Serialiser_All_Field112(data=list_data, many=True)
        if serializer_a.is_valid() and serializer_b.is_valid():
            serializer_a.save()
            print(serializer_a.data)
            data_a = [dict(data) for data in serializer_a.data] 
            print(data_a)
            data_b = [dict(data) for data in serializer_b.data]
            desired_key1 = 'USERNAME'
            desired_key2 = "THEME_OPT"
            serializer_a_data = [(d[desired_key1],d[desired_key2]) for d in data_a]
            print(serializer_a_data)
            x = 0
            for USERNAME in serializer_a_data:
                print(x)
                user_info = User_login_Data.objects.get(USERNAME = USERNAME[0])
                new_id = user_info.USERID
                new_info = Users_login_Details_Data(USERID_id=new_id,
                            USER_F_NAME=data_b[x].get('FIRST_NAME'),
                            USER_M_NAME=data_b[x].get("MIDDLE_NAME"),USER_L_NAME=data_b[x].get('LAST_NAME'),GENDER=data_b[x].get('GENDER'),
                            DOB=data_b[x].get("DOB"),ORGANIZATION=data_b[x].get("ORGANIZATION"),DESIGNATION=data_b[x].get("DESIGNATION"),
                            ADDRESS_1=data_b[x].get("ADDRESS_1"),ADDRESS_2=data_b[x].get("ADDRESS_2"),CITY= data_b[x].get("CITY"),
                            STATE=data_b[x].get("STATE"),COUNTRY=data_b[x].get("COUNTRY"),PIN_CODE=data_b[x].get("PIN_CODE"),
                            UU_REM=data_b[x].get("UU_REM"),OFF_LOCA=data_b[x].get("OFF_LOCA"),ALT_EMAIL=data_b[x].get("ALT_EMAIL"), LAN_LINE=data_b[x].get("LAN_LINE"))
                print("username list", USERNAME)
                USERNAME_1 = USERNAME[0]
                print(USERNAME)
                THEME_OPT = USERNAME[1][3::]
                print(THEME_OPT)
                send_admin_password_mail(user_info.EMAIL , PASSWORD, USERNAME_1, THEME_OPT)
                new_info.save()
                x = x+1
            serializer_a_1 = serializer_a.data
            serializer_b_1 = serializer_b.data
            response_data = {
                    'serializer_a_data': serializer_a_1,
                    'serializer_b_data': serializer_b_1,
                }
            return Response({'masage':'Admin Created Succesfully', 'response_data':response_data}, status=status.HTTP_201_CREATED)
        else:
                errors = {
            'serializer_a': serializer_a.errors if not serializer_a.is_valid() else None,
            'serializer_b': serializer_b.errors if not serializer_b.is_valid() else None,
        }
                return Response({'message': 'Validation error', 'errors': errors}, status=status.HTTP_400_BAD_REQUEST)
   
    elif request.method =="PATCH":  #patcxh===================================================
        try:
            auth_register_info = request.data
            if  request.user.USER_TYPE == "SU":
                user = User_login_Data.objects.get(USERID=auth_register_info.get("USERID"))
                if user is  None:
                    return Response({"Massage":"No admin found"}, status=status.HTTP_403_FORBIDDEN)
            elif request.user.USER_TYPE == "AU":
                keys_to_remove = ["SU_APRO_STAT", "SU_APRO_REM", "PASSWORD", "THEME_OPT", "EMAIL"]
                auth_register_info = {key: value for key, value in auth_register_info.items() if key not in keys_to_remove}
                user = User_login_Data.objects.get(USERID= request.user.USERID)
            else:
                return Response({"Message": "You are Not Allowed"}, status=status.HTTP_403_FORBIDDEN)
            user_detail, created = Users_login_Details_Data.objects.get_or_create(USERID_id=user.USERID)
            # obj = Users_login_Details_Data.objects.get(USERID_id=user.USERID)
        except Exception as e:
            return Response({"Massege":"User Not allowed xxx"}, status=status.HTTP_403_FORBIDDEN)
        
        serializer_a = User_login_Data_serialiser112(user, data= auth_register_info, partial=True)
        serializer_b = User_Detail_Data_Serialiser_All_Field112(user_detail,  data=auth_register_info, partial=True)
        if serializer_a.is_valid() and serializer_b.is_valid():
            # cv = {}
            # print(serializer_b.data)
            # if request.user.USER_TYPE == "AU":
            #     pass
            # else:
            serialized_data = serializer_b.validated_data
            serialized_data_1 = serializer_a.validated_data
            keys_to_ignore = ['PASSWORD','SU_APRO_STAT','AU_APRO_STAT', 'APRO_DATE', "CREATION_DATE"]
            result_dict_1 = {key: value for key, value in serialized_data_1.items() if key not in keys_to_ignore}
            result_dict_1.update(serialized_data)
            zx = model_to_dict(user)
            zy = model_to_dict(user_detail)
            zx.update(zy)
            keys_to_required = ['USERID','USERNAME','USER_TYPE', 'EMAIL', "MOBILE_NO", "THEME_OPT", "USER_F_NAME", "USER_L_NAME", "USER_M_NAME", "DOB","ORGANIZATION","DESIGNATION","CITY","STATE","COUNTRY","GENDER","LAN_LINE","ALT_EMAIL","OFF_LOCA","SU_APRO_REM", "AU_APRO_REM"]
            old_data_dict = {key: value for key,value in zx.items() if key in keys_to_required}
            result_dict = {key: result_dict_1[key] for key in old_data_dict if key in result_dict_1 and result_dict_1[key] != old_data_dict[key]}
            if not result_dict:
                pass
            else:
                try:
                    if request.user.USER_TYPE == "SU":
                        remark = dict(serialized_data_1).get("SU_APRO_REM")
                    elif request.user.USER_TYPE == "AU":
                        remark = dict(serialized_data_1).get("AU_APRO_REM")
                except:
                    remark= None
                if len(result_dict)== 1 and ("SU_APRO_REM" in result_dict and result_dict["SU_APRO_REM"] is not None):#  or  ("AU_APRO_REM" in result_dict and result_dict["AU_APRO_REM"] is not None)):

                    result_dict = None
                    su_apro_stat = dict(serialized_data_1).get("SU_APRO_STAT")
                    if user.SU_APRO_STAT == su_apro_stat or su_apro_stat is None:
                        if (remark is None or remark == ""):
                            pass
                        else:
                            mail_change_in_profile_AU_SU(user.EMAIL , user.USERNAME, result_dict, remark)
                else:
                    print("dict have something")
                    result_dict = {key:result_dict[key] for key in result_dict if key not in ("SU_APRO_REM", "AU_APRO_REM")}
                    mail_change_in_profile_AU_SU(user.EMAIL , user.USERNAME, result_dict, remark)
            # print("PRINT SERALISER", serialized_data.get("FIRST_NAME"))
            serializer_a.save()
            serializer_b.save()

            response_data = {
                    'serializer_a_data': serializer_a.data,
                    'serializer_b_data':  serializer_b.data
                }
            return Response({"data":response_data}, status=status.HTTP_200_OK)
        else:
            errors = {
            'serializer_a': serializer_a.errors if not serializer_a.is_valid() else None,
            'serializer_b': serializer_b.errors if not serializer_b.is_valid() else None,
        }
            return Response({'message': 'Validation error', 'errors': errors}, status=status.HTTP_400_BAD_REQUEST)
        
    elif request.method =="DELETE":   #status=status.HTTP_204_NO_CONTENT
        if not request.user.USER_TYPE == "SU":
            return Response({'message': 'Not Authorized SUPERUSER'}, status=status.HTTP_403_FORBIDDEN)
        auth_register_info = request.data
        try:
            user = User_login_Data.objects.get(USERID=auth_register_info.get("USERID"))
        except:
            return Response({"message": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        try:
            if user.USER_TYPE == "AU":
                status_ST = "DELETE"
                reason = "-"
                OPT = user.THEME_OPT[3:]
                print(OPT)
                print("UU_"+OPT)
                obj = User_login_Data.objects.all().filter(THEME_OPT="UU_"+OPT)
                EMAIL_Query = obj.values_list('EMAIL', flat=True)
                EMAIL_ALL = list(EMAIL_Query)
                block_admin_mail(user.EMAIL, status_ST, reason, user.USERNAME)
                mass_mail_block_admin(EMAIL_ALL , user.USERNAME, status_ST)
                user.delete()
                return Response({'detail': 'User deleted successfully'}, status=status.HTTP_200_OK)
            else:
                return  Response({"message": "User not AU"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"messages":f"error : {e}"}, status=status.HTTP_403_FORBIDDEN)

    return Response({'message': 'Invalid HTTP method'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


@api_view(['GET', 'POST', 'PUT', 'PATCH', 'DELETE'])
def permission_function(request):
    if request.method == 'GET':
        try:
            print("Usertype:", request.user.USER_TYPE)
            USER_TYPE = request.user.USER_TYPE
            print(USER_TYPE)
            if USER_TYPE not in ["SU", "AU", "UU"]:
                return Response({'message': 'Not Authorized '}, status=status.HTTP_403_FORBIDDEN)
            else:
                pass
        except:
            return Response({"Message":"Something went wrong"})
        # if request.user.USER_TYPE == "SU":
        #     THEME_OPT = request.GET.get("THEME_OPT")
        #     if THEME_OPT is None:
        #         return Response({"Message":"Required THEME_OPT"})
        #     else:
        #         THEME_TYPE = THEME_OPT[3:]
        # if request.user.USER_TYPE == "AU":
        #     THEME_TYPE = request.user.THEME_OPT[3:]
        
        USERID = request.GET.get("USERID")
        obj, created = MODUL_VIEW_PERMISSION.objects.get_or_create(USERID_id= USERID)
        if created:
            pass
        elif obj is not None:
            obj_thim = THEME_MODULE.objects.get(USERID_THEME_OPT= obj.USERID_THEME_OPT_id)
            id = obj.USERID_THEME_OPT_id
        print("IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII")
        # print(id)
        print("SSSSSSSSSSSSSSSSSSSSSSSSSSSSSS")
        # if id is None:
        #     id = obj_thim.USERID_THEME_OPT
        
        # datainfo = MODUL_VIEW_PERMISSION.objects.get(USERID_id= USERID).select_related("USERID_THEME_OPT").filter(USERID_THEME_OPT__THEME_TYPE= THEME_TYPE)
        try:
            datainfo, created = MODUL_VIEW_PERMISSION.objects.get_or_create(USERID_id = USERID) #, USERID_THEME_OPT__THEME_TYPE=THEME_TYPE)
            print("oooooooooooooooo")
            if request.user.USER_TYPE == "SU":
                if datainfo.USERID_THEME_OPT_id is None:
                    x = User_login_Data.objects.get(USERID=USERID)

                    THEME_OPT = x.THEME_OPT 
                    if THEME_OPT is None:
                        return Response({"Message":"Required THEME_OPT"})
                    else:
                        THEME_TYPE = THEME_OPT[3:]
                        obj_thim = THEME_MODULE.objects.get(THEME_TYPE=THEME_TYPE)
                        id = obj_thim.USERID_THEME_OPT
                        datainfo.save()
              
            elif request.user.USER_TYPE == "AU":
                if datainfo.USERID_THEME_OPT_id is None:
                    THEME_TYPE = request.user.THEME_OPT[3:]
                    obj_thim = THEME_MODULE.objects.get(THEME_TYPE=THEME_TYPE)
                    id = obj_thim.USERID_THEME_OPT
                    datainfo.save()
            elif request.user.USER_TYPE == "UU":
                if request.user.USERID != USERID:
                    return Response({"Message":"Correct yopur ID"}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    pass
                if datainfo.USERID_THEME_OPT_id is None:
                    THEME_TYPE = request.user.THEME_OPT[3:]
                    obj_thim = THEME_MODULE.objects.get(THEME_TYPE=THEME_TYPE)
                    id = obj_thim.USERID_THEME_OPT
                    datainfo.save()
                else:
                    pass
            # id = obj_thim.USERID_THEME_OPT
        except Exception as e:
            return Response({"Message":"Something Went Wrong"})
        print("cccccccccccccccccccc")
        print(datainfo)
        # for table_2 in datainfo:
        print(datainfo.USERID_THEME_OPT.MODEL_1)
        # obj_thim = THEME_MODULE.objects.all()
        serializer_a = MODUL_VIEW_PERMISSION_serialiser(datainfo).data
        print(serializer_a)
        column_names = [key for key in obj_thim.__dict__.keys() if  key.startswith('MODEL_')]
        permission_view = {}  #permission_view
        user_theme_opt_fields = serializer_a["USERID_THEME_OPT"]
        # num = 
        for i in range(1, len(column_names)+1):  # Assuming you have fields MODEL_1 to MODEL_10
            model_field_name = f"MODEL_{i}"
            permission_view[user_theme_opt_fields[model_field_name]] = serializer_a[model_field_name]
        print(permission_view)
        data_ser = {
            "serializer_a1":serializer_a
        }
        return Response({"message":data_ser, "data": permission_view}, status=status.HTTP_200_OK)

    elif request.method == 'POST':
        try:
            if not request.user.USER_TYPE == "AU":
                return Response({'message': 'Not Authorized SUPERUSER'}, status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({"Message":str(e)})
        auth_register_info = request.data
        auth_register_info = {key: value for key, value in auth_register_info.items() if key not in ["AU_ID", "USERID_THEME_OPT_id"]}
        if auth_register_info.get("USERID") is None:
            return Response({"Message":"Required USERID"}, status=status.HTTP_400_BAD_REQUEST)
        print(auth_register_info)
        THEME_TYPE = request.user.THEME_OPT[3:]
        print(THEME_TYPE)
        # auth_register_info['THEME_TYPE'] = THEME_TYPE
        obj_thim = THEME_MODULE.objects.get(THEME_TYPE=THEME_TYPE)
        print(obj_thim)
        auth_register_info['THEME_TYPE'] = THEME_TYPE
        # auth_register_info['USERID_THEME_OPT'] = obj_thim.USERID_THEME_OPT
        auth_register_info['AU_ID'] = request.user.USERID
        print(auth_register_info)
        serializer_a = MODUL_VIEW_PERMISSION_serialiser(data=auth_register_info)
        if serializer_a.is_valid():
            serializer_a.validated_data['USERID_THEME_OPT_id'] =  obj_thim.USERID_THEME_OPT
            serializer_a.validated_data['USERID_id'] =  auth_register_info.get("USERID")
            serializer_a.save()
            # serializer_a['THEME_TYPE'] = THEME_TYPE
            return Response({"Message":"SUCCESFULLY APPROVED", "DATA": serializer_a.data}, status=status.HTTP_201_CREATED)
        else:
            return Response({"error":serializer_a.errors}, status=status.HTTP_400_BAD_REQUEST)
        
    elif request.method == 'PATCH':
        try:
            if not request.user.USER_TYPE == "AU":
                return Response({'message': 'Not Authorized SUPERUSER'}, status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({"Message":str(e)})
        
        auth_register_info = request.data
        print(auth_register_info)
        print("aaaaaaaaaaaaaaaaaaaa")
        THEME_TYPE = request.user.THEME_OPT[3:]
        obj_thim = THEME_MODULE.objects.get(THEME_TYPE=THEME_TYPE)
        if auth_register_info.get("USERID") is None:
            return Response({"Message":"Required USERID"}, status=status.HTTP_400_BAD_REQUEST)
        user_detail, created = MODUL_VIEW_PERMISSION.objects.get_or_create(USERID_id = auth_register_info.get("USERID"))
        if created:
            print(THEME_TYPE)
            # auth_register_info['THEME_TYPE'] = THEME_TYPE
            print(obj_thim)
            auth_register_info['AU_ID'] = request.user.USERID
            # auth_register_info['USERID_THEME_OPT'] = obj_thim.USERID_THEME_OPT
            print(auth_register_info)
        user_info = User_login_Data.objects.get(USERID=auth_register_info.get("USERID"))
        serializer_b = User_login_Data_serialiser112(user_info, data= auth_register_info, partial=True)
        serializer_a = MODUL_VIEW_PERMISSION_serialiser(user_detail, data= auth_register_info, partial=True)
        if serializer_b.is_valid() and serializer_a.is_valid():
            serializer_b.save()
            serializer_a.validated_data['USERID_THEME_OPT_id'] =  obj_thim.USERID_THEME_OPT
            if user_detail.USERID_THEME_OPT_id == serializer_a.validated_data['USERID_THEME_OPT_id']:
                print("USERID_THEME_OPT_id is same as old")
                au_id_value = serializer_a.validated_data.get('AU_ID', None)
                if au_id_value is None or au_id_value == user_detail.AU_ID:
                    print("There is no au_id-value or old AU value")
                    serializer_a_1 = serializer_a.validated_data
                    new_permission = {key: value for key, value in serializer_a_1.items() if key not in ["AU_ID", "USERID_THEME_OPT_id"]}
                    zx = model_to_dict(user_detail)
                    old_permission ={key: value for key, value in zx.items() if key not in ["AU_ID", "USERID_THEME_OPT_id"]}
                    final_per_dict = {key: old_permission[key] for key in old_permission if key in new_permission and old_permission[key] != new_permission[key]}
                    if not final_per_dict:
                        print("No change in module permission")
                        pass
                    else:
                        print("change in module permission")
                        serializer_a.save()
                else:
                    print("au id change")
                    serializer_a.save()
            else:
                print("Thim change")
                serializer_a.save()
            response_data = {
                        'serializer_a_data': serializer_a.data}
            return Response({"data": response_data}, status=status.HTTP_200_OK)
        else:
            return Response({"error":serializer_a.errors}, status=status.HTTP_200_OK)
            

#customer_user_serialiser

@api_view(['GET','POST', 'PUT','PATCH','DELETE'])
def superuser_api(request): #active
    if request.method =="GET":
        if request.user.USER_TYPE == "SU" :
            user_login_detail_data = User_login_Data.objects.prefetch_related('logindata').get(USERID=request.user.USERID)
            try:
                x = user_login_detail_data.logindata.all().first()
                serializer_b = User_Detail_Data_Serialiser_All_Field112(x).data   #New Added
                data_ser = {
                "serializer_b1":serializer_b
                }
                i= serializer_b
                dict_1 = {}
                dict_1["USERNAME"] = i['USERID']["USERNAME"]  #very Important code
                dict_1["EMAIL"] = i['USERID']["EMAIL"]#
                dict_1["MOBILE_NO"] = i['USERID']["MOBILE_NO"]#
                dict_1["USERID"] = i['USERID']["USERID"]
                dict_1["CREATION_DATE"] = i['USERID']["CREATION_DATE"]
                dict_1["COUNTRY"] = i["COUNTRY"]#
                dict_1["STATE"] = i["STATE"]#
                dict_1["CITY"] = i["CITY"]#
                dict_1["ORGANIZATION"] = i["ORGANIZATION"]#
                dict_1["DESIGNATION"] = i["DESIGNATION"]#
                dict_1["FIRST_NAME"] = i["FIRST_NAME"]#
                dict_1["MIDDLE_NAME"] = i["MIDDLE_NAME"]#
                dict_1["LAST_NAME"] = i["LAST_NAME"]#
                dict_1["OFF_LOCA"] = i["OFF_LOCA"]#
                dict_1["ALT_EMAIL"] = i["ALT_EMAIL"]#
                dict_1["LAN_LINE"] = i["LAN_LINE"]#
            except:
                serializer_b = User_login_Data_serialiser112(user_login_detail_data).data
                data_ser = {
                "serializer_b1":serializer_b
                }
                i= serializer_b
                dict_1 = {}
                dict_1["USERNAME"] = i["USERNAME"]
                dict_1["EMAIL"] = i["EMAIL"]
                dict_1["MOBILE_NO"] = i["MOBILE_NO"]
                print(dict_1)
            return Response({"message": dict_1, "seralise_data": data_ser}, status=status.HTTP_200_OK)# 
        
        else:
            return Response({"Message":"User Not Allowed"})
        
    else:
        return Response({"Message":"MEthod Not ALLOwed"})
            
            # user = User_login_Data.objects.get(USERNAME=request.user.USERNAME) #for single User
            
        # except Exception as e:
        #     return  Response({'message': 'userNot Present'})
        # serializer_b = User_login_Data_serialiser112(user).data #UserLoginGeneral
        # return Response({'message': serializer_b}, status=status.HTTP_200_OK)

