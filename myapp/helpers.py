from django.contrib.auth.base_user import BaseUserManager
from django.conf import settings
from django.core.mail import send_mail

class Manager(BaseUserManager):
    def create_user(self, email, password = None, **extra_fields):
        if not email:
            raise ValueError('The Email is required')
        first_name = extra_fields.get('first_name')
        last_name = extra_fields.get('last_name')
        email = self.normalize_email(email)
        user = self.model(email = email, **extra_fields)
        user.set_password(password)  # Corrected line
        user.save(using = self._db)
        return user
    
    def create_superuser(self, email, password = None, **extra_fields):
        
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff = True')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser = True')
        
        return self.create_user(email, password, **extra_fields)

def send_email(email, token):
    subject = "Passowrd Rest"
    message = f"Hi, here is your link of forget password recovery http://127.0.0.1:8082/change_password/{token}"
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [email]
    send_mail(subject, message, email_from, recipient_list)
    return True