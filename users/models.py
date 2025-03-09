import uuid

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.contrib.auth.models import Group as Role
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField

from core.models import BaseModel


def upload_profile_picture_to(instance, filename):
    ext = filename.split(".")[-1]
    return f"profile-pictures/{uuid.uuid4()}.{ext}"


class UserManager(BaseUserManager):
    def create_user(
        self, email, first_name=None, last_name=None, password=None, **extra_fields
    ):
        if not email:
            raise ValueError("Users must have an email address")

        # Assign first and last name if not given in method call, safely
        if not isinstance(first_name, str) and not isinstance(last_name, str):
            name_parts = self.normalize_email(email).split("@")[0].split(".")
            if len(name_parts) == 2:
                first_name, last_name = name_parts
            elif len(name_parts) == 1:
                first_name, last_name = name_parts[0], ""
            else:
                first_name, last_name = name_parts[0], " ".join(name_parts[1:])

        user = self.model(
            email=email,
            first_name=first_name.capitalize(),
            last_name=last_name.capitalize(),
            **extra_fields,
        )

        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()

        user.save(using=self._db)

        # Assign default role
        # Assumes "not-assigned" role is pre-seeded
        role = Role.objects.get(name="Not-Assigned")
        user.groups.add(role)
        user.save()

        return user

    def create_superuser(self, first_name, last_name, email, password, **extra_fields):
        if not first_name:
            raise ValueError("Users must have a first name")
        if not last_name:
            raise ValueError("Users must have a last name")
        if not email:
            raise ValueError("Users must have an email address")
        if not password:
            raise ValueError("Users must have a password")

        user = self.model(
            first_name=first_name, last_name=last_name, email=email, **extra_fields
        )
        user.set_password(password)
        user.is_superuser = True
        user.is_staff = True
        user.is_active = True
        user.save(using=self._db)

        # Assign default role
        # Assumes "super-admin" role is pre-seeded
        role = Role.objects.get(name="Super-Admin")
        user.groups.add(role)
        user.save()

        return user


class User(AbstractUser, BaseModel):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=30, blank=True, null=True)
    profile_picture = models.ImageField(
        upload_to=upload_profile_picture_to, blank=True, null=True
    )
    first_name = models.CharField(max_length=30, null=False)
    last_name = models.CharField(max_length=30, null=False)
    bio = models.TextField(blank=True, null=True)
    phone_number = PhoneNumberField(blank=True, null=True, unique=True)
    position = models.OneToOneField(
        "basedata.Position",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="user",
    )
    is_not_deactivated = models.BooleanField(
        default=True
    )  # used for manual deactivation

    created_by = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="users_created_by",
    )
    updated_by = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="users_updated_by",
    )
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["password", "first_name", "last_name"]

    objects = UserManager()

    def __str__(self):
        return self.email
