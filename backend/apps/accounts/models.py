from django.contrib.auth.models import (
    AbstractUser,
    BaseUserManager,
) 
from django.db import models
from django.utils.translation import gettext_lazy as _


class UserRole(models.TextChoices):
    OWNER = "owner", _("Owner")
    MANAGER = "manager", _("Manager")
    EMPLOYEE = "employee", _("Employee")


class UserManager(BaseUserManager):

    def create_user(
        self,
        email,
        password=None,
        **extra_fields
    ):
        if not email:
            raise ValueError(
                "Email is required"
            )

        email = self.normalize_email(email)

        user = self.model(
            email=email,
            **extra_fields
        )

        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(
        self,
        email,
        password=None,
        **extra_fields
    ):
        extra_fields.setdefault(
            "is_staff",
            True
        )

        extra_fields.setdefault(
            "is_superuser",
            True
        )

        extra_fields.setdefault(
            "role",
            UserRole.OWNER
        )

        return self.create_user(
            email,
            password,
            **extra_fields
        )


class User(AbstractUser):
    class Role(models.TextChoices):
        OWNER = "owner", "Owner"
        MANAGER = "manager", "Manager"
        EMPLOYEE = "employee", "Employee"

    email = models.EmailField(
        unique=True
    )

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.EMPLOYEE
    )

    workspace = models.ForeignKey(
        "workspaces.Workspace",
        on_delete=models.CASCADE,
        related_name="users",
        null=True,
        blank=True
    )

    is_verified = models.BooleanField(
        default=False
    )

    def __str__(self):
        return self.email