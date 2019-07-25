from django.contrib.auth.models import AbstractUser, UserManager
from django.contrib.postgres.fields import JSONField
from django.db import models
from django.urls import reverse

from healthfacility.models import HealthFacility


class UserManager(UserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """ Creates and saves a User with the given username, email and password.
        """
        email = self.normalize_email(email)
        user = self.model.objects.filter(email=email).first()
        if user is not None:
            for key, value in extra_fields.items():
                setattr(user, key, value)
        else:
            user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)



class User(AbstractUser):
    """ A user account that can login and access functionality.
    """
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    email = models.EmailField(unique=True)
    username = models.CharField(unique=False, blank=True, max_length=150, null=True)
    password = models.CharField(max_length=199)
    first_name = models.CharField(max_length=150, blank=True, null=True)
    last_name = models.CharField(max_length=150, blank=True, null=True)
    phone_number = models.CharField(max_length=16, unique=True)
    properties = JSONField(blank=True, null=True)
    health_facility = models.ForeignKey(
        HealthFacility,
        on_delete=models.SET_NULL,
        related_name='members',
        blank=True,
        null=True
    )

    objects = UserManager()
    # def get_absolute_url(self):
    #     return reverse('users:user:user-profiles', kwargs={'username': self.username})

    class Meta:
        db_table = 'user'