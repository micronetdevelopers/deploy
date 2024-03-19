from django.core.mail import send_mail
# django.core.mail.send_mass_mail() 
# from django.core.mail import send_mass_mail
from django.conf import settings 


def send_forget_password_mail(email , token, x):
    subject = 'Your forget password link'
    if x == 2:
        message = f'Hi ,  {token}'
        email_from = settings.EMAIL_HOST_USER
        recipient_list = [email]
        send_mail(subject, message, email_from, recipient_list)
        return True
    else:
        message = f'Hi , click on the link to reset your password  http://localhost:3000/Cpassword/{token}/'
        email_from = settings.EMAIL_HOST_USER
        recipient_list = [email]
        send_mail(subject, message, email_from, recipient_list)
        return True
    

def send_admin_password_mail(EMAIL, PASSWORD, USERNAME, THEME_OPT):
    # subject = 'Micronet password'
    # message = f'Hi ,Admin :"{USERNAME}" Please use this password for login "{PASSWORD}"'
    subject = f'Regarding Your {THEME_OPT}-Admin Login Information'
    message = f'Hi {THEME_OPT}-Admin,\n\nUsername: {USERNAME}\nPassword: {PASSWORD}\n\nPlease use this information for login. \n\nBest regards,\nGeoPicX'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [EMAIL]
    send_mail(subject, message, email_from, recipient_list)
    return True

def send_authorised_APPROVED_mail(EMAIL, AU_APRO_STAT, AU_APRO_REM, USERNAME):
    subject = 'Notification Regarding Your Account Status'
    message =f'Hi {USERNAME},\n\n' \
          f'This is to inform you that your account has been {AU_APRO_STAT.lower()}\n' \
          f'Reason: {AU_APRO_REM}\n\n' \
          f'Please refer to this message for more details.\n\n' \
          f'Best regards,\n GeoPicX'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [EMAIL]
    send_mail(subject, message, email_from, recipient_list)
    return True
    
    
def mass_mail_block_admin(EMAIL_LIST, ADMIN_USERNAME, status):
    subject = 'Important: Temporary Suspension of Your Access to Services'
    # message = f'Hi ,Admin :"{ADMIN_USERNAME}" {status} We start your service shortly"'
    message =  f'Hi User,\n\n' \
          f'We regret to inform you that your access to services has been temporarily suspended by the administrator, due to {ADMIN_USERNAME} has been block.\n' \
          f'{status} We will start your service shortly.\n\n' \
          f'Thank you for your understanding.\n\n' \
          f'Best regards,\nGeoPicX'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = EMAIL_LIST
    send_mail(subject, message, email_from, recipient_list)
    return True

def block_admin_mail(EMAIL, SU_APRO_STAT, SU_APRO_REM , USERNAME):
    subject = f'Notification: Your Admin Status is {SU_APRO_STAT.capitalize()}'
    message = f'Hi  ADMIN : {USERNAME},\n\n' \
          f'You are {SU_APRO_STAT.lower()}.\n' \
          f'Reason: {SU_APRO_REM}\n\n' \
          f'Thank you for your attention to this matter.\n\n' \
          f'Best regards,\nGeoPicX'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [EMAIL]
    send_mail(subject, message, email_from, recipient_list)
    return True

def UU_resister_mail(EMAIL, USERNAME):
    subject = 'Registration Confirmation: Await Login Approval'
    message = f'Hi USER "{USERNAME}",\n\n' \
          f'Thank you for registering with us!\n' \
          f'Please wait for some time for your login approval.\n' \
          f'Our admin has sent you a message regarding your approval status.\n\n' \
          f'Thank you for your patience.\n\n' \
          f'Best regards,\nnGeoPicX'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [EMAIL]
    send_mail(subject, message, email_from, recipient_list)
    return True

def mail_Delete_UU_to_admin(EMAIL_LIST, USERNAME, status, Deleted_by):
    subject = f'User Deletion Notification: {USERNAME} {status.capitalize()} by {Deleted_by}'
    # message = f'Hi ,Admin :" user :{USERNAME}"  status:{status} by {Deleted_by}"'
    message =  f'Hi Admin,\n\n' \
          f'The user "{USERNAME}" has been {status.lower()} by {Deleted_by}.\n\n' \
          f'Thank you for managing user accounts.\n\n' \
          f'Best regards,\nGeoPicX'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = EMAIL_LIST
    send_mail(subject, message, email_from, recipient_list)
    return True

def Delete_UU_mail_to_UU(EMAIL, status,USERNAME, admin_email, DELETE_BY):
    subject = f'Important: Your Account "{USERNAME}" Status Update'
    message = f'Hi User,\n\n' \
          f'Your account "{USERNAME}" has been {status.lower()} and is no longer active.\n' \
          f'Please contact the administrator at {admin_email} for further assistance.\n\n' \
          f'This action was performed by {DELETE_BY}.\n\n' \
          f'Thank you for using our services.\n\n' \
          f'Best regards,\nGeoPicX'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [EMAIL]
    send_mail(subject, message, email_from, recipient_list)
    return True

def send_forget_password_mail_admin(EMAIL , token, USERNAME):
    subject = 'Password Change Request OTP'
    message = f'Hi user,\n\n' \
          f'The user "{USERNAME}" has requested a OTP to change their password.\n' \
          f'User OTP: {token}\n\n' \
          f'If you did not request this, please disregard this email.\n\n' \
          f'Best regards,\nGeoPicX'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [EMAIL]
    send_mail(subject, message, email_from, recipient_list)
    return True

def send_UU_model_permission(EMAIL , s, USERNAME):
    subject = f'Permission Granted: {s} Access for {USERNAME}'
    message = f'Hi {USERNAME},\n\n' \
              f'You have been granted permission in the application: {s}.\n\n' \
              f'Thank you for using our services.\n\n' \
              f'Best regards,\nGeoPicX'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [EMAIL]
    send_mail(subject, message, email_from, recipient_list)
    return True

def send_SU_EMAIL_CREATE(EMAIL , USERNAME):
    subject = f'Account Creation Confirmation for SUPERUSER {USERNAME}'
    message = message = f'Hi SUPERUSER {USERNAME},\n\n' \
          f'Your account has been successfully created.\n\n' \
          f'Thank you for joining us!\n\n' \
          f'Best regards,\nGeoPicX'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [EMAIL]
    send_mail(subject, message, email_from, recipient_list)
    return True

def password_change_mail(EMAIL , USERNAME):
    subject = 'password change'
    message = f'Hi USER {USERNAME},\n\n' \
          f'Your password has been changed successfully.\n\n' \
          f'Thank you for maintaining the security of your account.\n\n' \
          f'Best regards,\nGeoPicX'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [EMAIL]
    send_mail(subject, message, email_from, recipient_list)
    return True

# def mail_change_in_profile_AU_SU(EMAIL , USERNAME, result_dict, remark):
def mail_change_in_profile_AU_SU(*arg):
    subject = f'Profile Data Update Notification for USER {arg[1]}'
    message = f'Hi USER {arg[1]},\n\n' \
          f'Your profile data has been updated. The changes made are:\n\n' \
          f'{arg[2]}\n\n' \
          f'Thank you for keeping your information up-to-date.\n\n' \
          f'Remark : {arg[3]} \n\n' \
          f'Best regards,\nYour Organization'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [arg[0]]
    send_mail(subject, message, email_from, recipient_list)
    return True

def GU_resister_mail(EMAIL, USERNAME):
    subject = subject = f'Account Creation Confirmation for USER {USERNAME}'
    message = f'Hi USER {USERNAME},\n\n' \
          f'Your account has been created successfully.\n\n' \
          f'Thank you for joining us!\n\n' \
          f'Best regards,\nYour Organization'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [EMAIL]
    send_mail(subject, message, email_from, recipient_list)
    return True

                                                                                      