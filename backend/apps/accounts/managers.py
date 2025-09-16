from django.contrib.auth.base_user import BaseUserManager

class UserManager(BaseUserManager):
    def create_user(self, username="", email="", password="", **extra_fields):
        if not email:
            raise ValueError("Enter an email address")
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username="", email="", password=""):
        user = self.create_user(
            email=email, password=password, username=username)
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)
        return user