from django.core.exceptions import ValidationError
from django.db import models
import re
# from .models import User_login_Data

def validate_no_dot(value):
    value12 = value.strip()
    if " " in value12 or  '.' in value12 or len(value12) < 6 or not (any(char.isalpha() for char in value12) and re.match("^[a-zA-Z0-9@%&*_\-]*$", value12)): 
        raise ValidationError("Usernames cannot contain space, dots and less than six charector and required at leat one letter and only accept spacial charectors are @%&*")
    
# def email_validation(value):
#     norm_email = value.lower().strip()
#     if User_login_Data.objects.filter(EMAIL__iexact=norm_email).exists():
#             raise ValidationError("Not unique email")
    
    #     value12 = value.replace(" ", "")
    # print(value12)
def validate_password(value):
    value = value.strip()

    if " " in value:
        raise ValidationError("Password cannot contain spaces.")
    
    if len(value) < 8:
        raise ValidationError("Password should be at least 8 characters long.")
    
    if not any(char.isalpha() for char in value):
        raise ValidationError("Password should contain at least one alphabet character.")
    
    if not any(char.isdigit() for char in value):
        raise ValidationError("Password should contain at least one digit.")
    
    # if not any(x in "!@#$%^&*" for x in value):
    #     raise ValidationError("Password should contain at least one of the special characters: !@#$%^&*")
    allowed_special_characters = set("!@#$%^&*")
    if not any(x in allowed_special_characters for x in value) or any(x for x in value if not (x.isalpha() or x.isdigit()  or x in allowed_special_characters)):
        raise ValidationError("Password should contain only the special characters: !@#$%^&*  ")
