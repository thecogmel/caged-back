import jwt
from django.conf import settings
from django.shortcuts import get_object_or_404
from rest_framework import generics, status, viewsets
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.tokens import RefreshToken, TokenError

from .models import User

from .serializers import (
    LoginSerializer,
    LogoutSerializer,
    PrivateResetPasswordSerializer,
    ResetPasswordSerializer,
    UpdatePasswordSerializer,
    UserProfileSerializer,
    UserSerializer,
)


class UserViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        # Allow only super admins to create users via /users (POST)
        if getattr(self, "action", None) == "create":
            permission_classes = [IsAuthenticated, IsAdminUser]
        else:
            permission_classes = [IsAuthenticated]
        return [perm() for perm in permission_classes]


class LoginViewSet(generics.GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        return Response(serializer.validated_data, status.HTTP_200_OK)


class RefreshTokenView(generics.GenericAPIView):
    permission_classes = [AllowAny]

    def get_user_from_jwt_raw_token(self) -> User:
        token = jwt.decode(
            self,
            settings.SECRET_KEY,
            algorithms=settings.SIMPLE_JWT["ALGORITHM"],
        )
        return get_object_or_404(User, id=token["user_id"])

    def post(self, request):
        serializer = TokenRefreshSerializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except TokenError:
            return Response(
                {"detail": ("Invalid token.")},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        user = self.get_user_from_jwt_raw_token(request.data["refresh"])
        user_data = self.get_serializer(user=user).data

        return Response(
            {"user": user_data, "tokens": serializer.validated_data},
            status=status.HTTP_200_OK,
        )


class LogoutView(APIView):
    def post(self, request):
        try:
            serializer = LogoutSerializer(data=request.data["refresh"])
            serializer.is_valid(raise_exception=True)

            RefreshToken(serializer.validated_data["refresh"]).blacklist()

            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class ResetPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = User.objects.get(email=serializer.validated_data["email"])

        if not user:
            return Response(
                status=status.HTTP_404_NOT_FOUND,
                data={"detail": "Usuário não encontrado."},
            )

        if user.is_superuser or user.is_staff:
            return Response(
                status=status.HTTP_403_FORBIDDEN,
                data={"detail": "Não é possível resetar a senha deste usuário."},
            )

        # mail_reset_password(user, generate_random_string())
        return Response(
            status=status.HTTP_200_OK,
            data={
                "detail": "Enviamos o e-mail com as instruções de recuperação de senha.",
            },
        )


class UpdatePasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UpdatePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = User.objects.get(email=serializer.validated_data["email"])

        # if get_and_delete_from_cache(serializer.validated_data["token"]) is None:
        #     return Response(
        #         status=status.HTTP_400_BAD_REQUEST,
        #         data={"detail": "Token inválido."},
        #     )

        if not user:
            return Response(
                status=status.HTTP_404_NOT_FOUND,
                data={"detail": "Usuário não encontrado."},
            )

        user.set_password(serializer.validated_data["password"])
        user.save()

        return Response(
            status=status.HTTP_200_OK,
            data={
                "detail": "Senha atualiza com sucesso.",
            },
        )


class UserProfileView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class PrivateResetPasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = PrivateResetPasswordSerializer(
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        user = User.objects.get(email=request.user.email)

        user.set_password(serializer.validated_data["password"])
        user.save()

        return Response(
            status=status.HTTP_200_OK,
            data={
                "detail": "Senha atualiza com sucesso.",
            },
        )
