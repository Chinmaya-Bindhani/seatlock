from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth.validators import UnicodeUsernameValidator


class UserManager(BaseUserManager):
    use_in_migrations = True
    def create_user(self,email,username,password,**extra_fields):
        if not email:
            raise ValueError("email is required ! ")
        email = self.normalize_email(email.strip()).lower()

        if not username or not username.strip():
            raise ValueError("Username is required.")
        username=self.model.normalize_username(username.strip())

        extra_fields.setdefault("role", self.model.Role.CUSTOMER)
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)

        if extra_fields["role"] not in self.model.Role.values:
            raise ValueError("Invalid user role.")

        user = self.model(email=email,username=username,**extra_fields)

        user.username = self.model._meta.get_field("username").clean(
            user.username,
            user,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self,email,username,password,**extra_fields):
        extra_fields.setdefault("role", self.model.Role.ADMIN)
        extra_fields.setdefault('is_staff',True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault('is_active',True)

        if extra_fields.get("role") != self.model.Role.ADMIN:
            raise ValueError("Superuser must have role=ADMIN.")

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")

        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email,username,password,**extra_fields)


class User(AbstractUser):
    email = models.EmailField(unique=True, max_length=255,verbose_name="EMAIL")
    username = models.CharField(max_length = 100,validators=[UnicodeUsernameValidator()])
    first_name = models.CharField(max_length = 100)
    last_name = models.CharField(max_length = 100)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    class Role(models.TextChoices):
        CUSTOMER = "CUSTOMER", "Customer"
        AGENT = "AGENT", "Agent"
        ADMIN = "ADMIN", "Administrator"

    role = models.CharField(
        max_length=8,
        choices=Role.choices,
        default=Role.CUSTOMER,
    )
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name','last_name','username']
    objects = UserManager()

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(role__in=["CUSTOMER", "AGENT","ADMIN"]),
                name="accounts_user_valid_role",
            ),
        ]

    def __str__(self):
        return self.username
