from django.db import models # noqa
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, \
    PermissionsMixin


class UserManager(BaseUserManager):
    """Manager for user model"""
    def create_user(self, email, password=None, **extra_fields):
        """Create and save a new user"""
        if not email:
            raise ValueError("User must have an email address")
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password) # noqa
        user.save(using=self._db) # noqa
        return user

    def create_superuser(self, email, password):
        """Create and save a new superuser"""
        user = self.create_user(email=email, password=password)
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db) # noqa
        return user


class User(AbstractBaseUser, PermissionsMixin):
    """Custom user model that supports using email instead of username"""
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True) # noqa
    is_staff = models.BooleanField(default=False) # noqa

    objects = UserManager()

    USERNAME_FIELD = 'email'


class Recepie(models.Model):
    """Recepie object"""
    title = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=5, decimal_places=2)
    time_minutes = models.IntegerField()
    description = models.TextField()
    link = models.CharField(max_length=255, blank=True)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )
    tags = models.ManyToManyField('Tag')

    def __str__(self):
        return self.title


class Tag(models.Model):
    """Tag object"""
    name = models.CharField(max_length=255)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return self.name
