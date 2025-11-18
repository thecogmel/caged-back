from django.contrib.auth.models import BaseUserManager


class UserManager(BaseUserManager):
    def create_user(
        self, email: str | None = None, password: str | None = None, **extra_fields
    ):
        """Cria e salva um usuário com email e senha (hasheada).

        - Valida que o email foi informado.
        - Normaliza o email e força lowercase.
        - Se a senha não for fornecida, marca a conta como sem senha utilizável.
        - Salva usando self._db para compatibilidade com múltiplos bancos.
        """
        if not email:
            raise ValueError("O e-mail deve ser informado")

        email = self.normalize_email(email).lower()
        user = self.model(email=email, **extra_fields)

        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()

        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        """Cria um superuser garantindo os flags necessários."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault(
            "role", getattr(self.model, "Roles", None) and self.model.Roles.ADMIN
        )

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser precisa ter is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser precisa ter is_superuser=True.")

        return self.create_user(email=email, password=password, **extra_fields)
