from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

USER_TYPE_CHOICES = [
    ('Farmer', 'Farmer'),
    ('Agrovet', 'Agrovet'),
]

class UserManager(BaseUserManager):
    def create_user(self, phone_number, password=None, **all_fields):
        if not phone_number:
            raise ValueError('The Phone Number must be set')
        user = self.model(phone_number=phone_number, **all_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

class User(AbstractBaseUser):
    username = models.CharField(_("Username"), max_length=150, unique=True)
    first_name = models.CharField(_("First Name"), max_length=30, blank=True)
    last_name = models.CharField(_("Last Name"), max_length=30, blank=True)
    email = models.EmailField(_("Email Address"), max_length=255, unique=True, blank=True, null=True)
    image = models.ImageField(_("Profile Image"), upload_to='profile_images/', blank=True, null=True)
    user_type = models.CharField(
        _("User Type"),
        max_length=20,
        choices=USER_TYPE_CHOICES,
    )
    phone_number = models.CharField(_("Phone Number"), max_length=20, unique=True)
    date_joined = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    otp = models.CharField(max_length=5, blank=True, null=True)
    agrovets = models.ManyToManyField('self', blank=True, symmetrical=False, related_name='registered_farmers')

   
    objects = UserManager()
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['phone_number', 'email', 'first_name', 'last_name', 'user_type']

    def __str__(self):
        return self.username
