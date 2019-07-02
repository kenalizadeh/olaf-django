from django.contrib.auth.models import (
    AbstractBaseUser, PermissionsMixin, BaseUserManager
)


class UserManager(BaseUserManager):

    def _create_user(self, password, **extra_fields):
        """
        Creates and saves a User with the given email,and password.
        """
        try:
            user = self.model(**extra_fields)
            user.set_password(password)
            user.save(using=self._db)
            return user
        except:
            raise ValueError('ValueError: Cannot create new user')

    def create_user(self, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        extra_fields.setdefault('is_business', False)
        
        return self._create_user(password, **extra_fields)

    def create_superuser(self, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_business', False)

        return self._create_user(password=password, **extra_fields)
