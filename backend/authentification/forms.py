# from django.contrib.auth.forms import UserCreationForm, UserChangeForm  
# from django import forms
# from .models import User_login_Data  
# from django.contrib.auth import get_user_model 

# User = get_user_model()  

# class CustomUserCreationForm(UserCreationForm):  
#     user_type_choices = (
#         ('Au_MARS', 'MARS-Archival'),
#         ('Au_MARS', 'MARS-Retrival'),
#         ('Au_MARS', 'MARS-Search'),
#         ('Au_Agriculture', 'Agriculture-Admin'),
#         ('Au_Agriculture', 'Water-Admin'),
#     )
#     password1 = forms.CharField(widget=forms.PasswordInput)
#     password2 = forms.CharField(label='Confirm Password', widget=forms.PasswordInput)
#     user_type = forms.ChoiceField(choices=user_type_choices, required=True)
#     class Meta:  
#         model = User_login_Data  
#         fields = ('EMAIL',)

#     def clean_email(self):  
#         EMAIL = self.cleaned_data.get('EMAIL')  
#         qs = User.objects.filter(EMAIL=EMAIL)  
#         if qs.exists():
#             raise forms.ValidationError("Email is taken")  
#         return EMAIL    
    
#     def clean(self):  
#         '''  
#         Verify both passwords match.  
#         '''  
#         cleaned_data = super().clean()  
#         password1 = cleaned_data.get("password1")  
#         password2 = cleaned_data.get("password2")
#         if password1 is not None and password1 != password2:
#             self.add_error("password2", "Your passwords must match")
#         return cleaned_data 
    
#     def save(self, commit=True):  
#         # Save the provided password in hashed format  
#         user = super().save(commit=False)  
#         user.set_password(self.cleaned_data["password1"])  
#         if commit:  
#             user.save()  
#         return user
    
# class CustomUserChangeForm(UserChangeForm):  
#     class Meta:  
#         model = User_login_Data  
#         fields = ('EMAIL', )  
  
#     def clean_password(self):  
#         # Regardless of what the user provides, return the initial value.  
#         # This is done here, rather than on the field, because the
#         # field does not have access to the initial value  
        # return self.initial["password1"]
            