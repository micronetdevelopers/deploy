from django.shortcuts import render,redirect, HttpResponse
from django.db.models import Q
from django.contrib import messages
from django.core.mail import send_mail
import uuid
from rest_framework import status
from .models import User_login_Data,Users_login_Details_Data,password_table
from .serializers import *
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .helpers import send_forget_password_mail

def xyx(request):
    return HttpResponse('<h1>cccccccc</h1>')

# @api_view(['GET','POST', 'PUT','PATCH','DELETE'])
# def ch_updte_password(request, id):
#     try:
#         obj = User_login_Data.objects.get(id = id)  
#     except:
#         return Response({"massage":"user not present"})
    
#     if request.method == "PATCH":
#         user_info = request.data
#         print(user_info)
#         ser_li = ch_up(data=user_info)
#         if ser_li.is_valid():
#             new_password = ser_li.validated_data['user_pw']
#             old_password = ser_li.validated_data['user_pw_old']
#             ouestion_id = ser_li.validated_data['ouestion_id']
#             ques_ans = ser_li.validated_data['ques_ans']
#             x = obj.Q1_ID
#             y = obj.Q2_ID
#             if ouestion_id == x:
#                 w = obj.Q1_AN
#             elif ouestion_id == y:
#                 w = obj.Q2_AN
#             else:
#                 return Response({'massage':"question you provide Wrong"})
            
            
#             if old_password == obj.PASSWORD and  ques_ans == w:
#                 serializer = User_login_Data_serialiser(obj, data= request.data, partial=True)
#                 if serializer.is_valid():
#                     serializer.save()
#                     return Response(serializer.data)
#                 else:
#                     return Response(serializer.errors)
#             else:
#                 return Response({"massage":"something went wrong please cheak old password and question"})
                
#         else:
#             return Response(ser_li.errors)
        
#     else:
#         return Response({"masage":"Method not allowed"})

@api_view(['GET','POST', 'PUT','PATCH','DELETE'])
def change_password(request):
    if  request.method == "POST":
        user_info = request.data
        print("user_info ",user_info)
        x = user_info.get("USERNAME")
        y = user_info.get("PASSWORD")
        try:
            result = User_login_Data.objects.get(USERNAME=x)
            if check_password(y, result.PASSWORD):
                return Response({"Message":"Credintial Match"}, status=status.HTTP_200_OK)
            else:
                return Response({"Message":"Password Not Match"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"Message": f"User Not Exist. Error: {str(e)}"} , status=status.HTTP_400_BAD_REQUEST)

    elif request.method == "PATCH":
        user_info = request.data
        keys_to_required = ["USERNAME", "OLD_PASSWORD", "NEW_PASSWORD", "PASSWORD"]
        user_info_1 = {key: value for key, value in user_info.items() if key  in keys_to_required}

        x = user_info_1.get("USERNAME")
        y = user_info_1.get("OLD_PASSWORD")
        try:
            result = User_login_Data.objects.get(USERNAME=x)
            if check_password(y, result.PASSWORD):
                if user_info_1.get("PASSWORD") == user_info_1.get("NEW_PASSWORD"):
                    serializer_a = User_login_Data_serialiser112(result, data= user_info_1, partial=True)
                    if serializer_a.is_valid():
                        result.PASSWORD = make_password(serializer_a.validated_data['PASSWORD'])
                        result.save()
                        password_change_mail(result.EMAIL, result.USERNAME)
                        # serializer_a.save()
                        return Response({"Message":"PASSWORD CHANGE SUCCESFULLY"}, status=status.HTTP_200_OK)
                    else:
                        return Response({"error":serializer_a.errors}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response({"Message":"Password Not Match"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"Message":"Password Not Match"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"Message": f"User Not Exist. Error: {str(e)}"} , status=status.HTTP_400_BAD_REQUEST)
        
    else:
        return Response({'message': 'Method not allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


    #     # serializer = forget_pass_seria(data=user_info)
    #     # if serializer.is_valid():
    #         print("fffff")
    #         x = serializer.validated_data['user_un']
    #         print(x)
    #         print(type(x))
    #         result = User_login_Data.objects.filter(Q(USERNAME=x) | Q(EMAIL=x))
    #         if result.exists():
    #             print(result)
    #             obj = User_login_Data.objects.get(Q(USERNAME=x) | Q(EMAIL=x))
    #             print("xxxxx")
    #             print(obj.id)
    #             if obj. USER_TYPE == "GU":
    #                 serialized_data = User_login_Data_serialiser(obj).data 
    #                 return Response({'data': serialized_data, "Massage":"Please Use forget password"})
    #             elif obj.   USER_TYPE == "UU":
    #                 obj.appr_status = True
    #                 obj.save()
    #                 token = "Your MARS Password Changed"
    #                 x = 2
    #                 send_forget_password_mail(obj.EMAIL , token, x)
    #                 messages.success(request, 'An email is sent.')
    #                 serialized_data = User_login_Data_serialiser(obj).data
    #                 print(serialized_data)
    #                 return Response({'message': serialized_data, "user":"authorised"})
    #             else:
    #                 return Response({'message': 'Not authorised'})
    #         else:
    #             return Response({'message':"No information found"})   
    #     else:
    #         return Response({'message': 'Validation error', 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    # return Response({'message': 'Method not allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)



@api_view(['GET','POST', 'PUT','PATCH','DELETE'])
def contact_us(request):
    if request.method =='POST':
         resister_info = request.data
         serializer = contact_us_serialiser(data=resister_info)
         if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    return Response({'message': 'Method not allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
#lfjkgfkg

# @api_view(['GET','POST', 'PUT','PATCH','DELETE'])
# def general_to_authorized(request, USERNAME):
#     try:
#         obj = User_login_Data.objects.get(id = id)  
#     except:
#         return Response({"massage":"user not present"})