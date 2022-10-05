from django.db import models
from django.apps import apps

from django.contrib.auth.models import AbstractUser, UserManager
from django.utils.translation import ugettext_lazy as _

class CustomUserManager(UserManager):
    use_in_migrations = True

    def _create_user(self, username, email, password, **extra_fields):
        """
        Create and save a user with the given username, email, and password.
        """
        print('*' * 35)
        print('*' * 35)
        print(extra_fields)
        print('*' * 35)
        print('*' * 35)
        
        if not username:
            raise ValueError('The given username must be set')

        if not extra_fields.get('api_client_name'):
            raise ValueError('The given api_client_name must be set')

        email = self.normalize_email(email)
        # Lookup the real model class from the global app registry so this
        # manager method can be used in migrations. This is fine because
        # managers are by definition working on the real model.
        GlobalUserModel = apps.get_model(self.model._meta.app_label, self.model._meta.object_name)
        username = GlobalUserModel.normalize_username(username)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

class User(AbstractUser):
    CLIENT_CHOICES = [
        ('procon', 'Procon'),
        ('gsi', 'GSI'),
    ]
    
    api_client_name = models.CharField(max_length=128, choices=CLIENT_CHOICES)

    REQUIRED_FIELDS = ('api_client_name',)

    objects = CustomUserManager()