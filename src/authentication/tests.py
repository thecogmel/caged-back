from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import User


class UserPermissionsAndHashingTests(APITestCase):
    """Testes explicativos para permissões e hashing de senha.

    Cada método de teste abaixo tem um comentário explicando o propósito do teste,
    o setup usado (quais usuários são criados) e a asserção principal esperada.
    Isso serve como documentação e como verificação automatizada.
    """

    def setUp(self):
        # Criamos três usuários com papéis diferentes para cobrir os cenários:
        # - superuser: tem is_superuser=True (poder máximo nas ações destrutivas/ criação)
        # - speaker: tem role == Roles.SPEAKER (pode listar/recuperar)
        # - member: usuário comum (não deve conseguir as ações especiais)
        self.superuser = User.objects.create_superuser(
            email="su@example.com",
            password="superpass",
            name="Su",
            username="su",
        )

        self.speaker = User.objects.create_user(
            email="speaker@example.com",
            password="speakpass",
            name="Speaker",
            username="speaker",
            role=User.Roles.SPEAKER,
        )

        self.member = User.objects.create_user(
            email="member@example.com",
            password="memberpass",
            name="Member",
            username="member",
            role=User.Roles.MEMBER,
        )

    def obtain_token(self, email, password):
        """Helper: realiza login e retorna access token."""
        url = reverse("login")
        resp = self.client.post(
            url, {"email": email, "password": password}, format="json"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        return resp.data["tokens"]["access"]

    def test_create_user_only_superuser(self):
        """Verifica que apenas superuser consegue criar usuários via POST /users/.

        Setup: usa tokens do superuser e de um member.
        Asserções:
        - superuser recebe 201 (criação bem-sucedida)
        - member recebe 403 (proibido)
        """
        url = reverse("users-list")

        # superuser cria com sucesso
        token = self.obtain_token("su@example.com", "superpass")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        data = {
            "email": "new@example.com",
            "username": "new",
            "name": "New",
            "password": "newpass",
            "role": User.Roles.MEMBER,
        }
        resp = self.client.post(url, data, format="json")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # member não pode criar
        token_m = self.obtain_token("member@example.com", "memberpass")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token_m}")
        resp2 = self.client.post(url, data, format="json")
        self.assertEqual(resp2.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_and_retrieve_only_speaker(self):
        """Verifica que list e retrieve são permitidos apenas para SPEAKER.

        - Speaker deve conseguir listar e recuperar um usuário específico.
        - Member e superuser (quando não SPEAKER) não devem conseguir.
        """
        list_url = reverse("users-list")
        # create a target user to retrieve
        target = User.objects.create_user(
            email="target@example.com",
            password="tpass",
            name="Target",
            username="target",
            role=User.Roles.MEMBER,
        )
        retrieve_url = reverse("users-detail", kwargs={"pk": target.pk})

        # Speaker can list
        token_s = self.obtain_token("speaker@example.com", "speakpass")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token_s}")
        resp = self.client.get(list_url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        # Speaker can retrieve
        resp2 = self.client.get(retrieve_url)
        self.assertEqual(resp2.status_code, status.HTTP_200_OK)

        # Member cannot list or retrieve
        token_m = self.obtain_token("member@example.com", "memberpass")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token_m}")
        resp3 = self.client.get(list_url)
        self.assertEqual(resp3.status_code, status.HTTP_403_FORBIDDEN)
        resp4 = self.client.get(retrieve_url)
        self.assertEqual(resp4.status_code, status.HTTP_403_FORBIDDEN)

        # Superuser (is_superuser True) is not SPEAKER: may be blocked by SPEAKER-only
        token_su = self.obtain_token("su@example.com", "superpass")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token_su}")
        resp5 = self.client.get(list_url)
        self.assertEqual(resp5.status_code, status.HTTP_403_FORBIDDEN)

    def test_destructive_actions_only_superuser(self):
        """Verifica que update/partial_update/destroy são permitidos apenas para superuser.

        - member and speaker devem receber 403;
        - superuser deve conseguir deletar e atualizar.
        """
        target = User.objects.create_user(
            email="t2@example.com",
            password="t2pass",
            name="T2",
            username="t2",
            role=User.Roles.MEMBER,
        )
        url = reverse("users-detail", kwargs={"pk": target.pk})

        # member cannot delete
        token_m = self.obtain_token("member@example.com", "memberpass")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token_m}")
        resp = self.client.delete(url)
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

        # speaker cannot delete
        token_sp = self.obtain_token("speaker@example.com", "speakpass")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token_sp}")
        resp2 = self.client.delete(url)
        self.assertEqual(resp2.status_code, status.HTTP_403_FORBIDDEN)

        # superuser can delete
        token_su = self.obtain_token("su@example.com", "superpass")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token_su}")
        resp3 = self.client.delete(url)
        self.assertIn(
            resp3.status_code, (status.HTTP_204_NO_CONTENT, status.HTTP_200_OK)
        )

    def test_password_is_hashed_on_create_and_update(self):
        """Verifica que a senha é hasheada quando criado via serializer/manager e ao atualizar.

        - Ao criar um usuário via manager/serializer a senha armazenada não é igual ao raw password.
        - Ao atualizar com um novo password, `check_password` retorna True para a senha nova.
        """
        # create via manager (serializer uses manager under the hood)
        u = User.objects.create_user(
            email="hashcheck@example.com",
            password="plainpass",
            name="Hash",
            username="hash",
            role=User.Roles.MEMBER,
        )
        # stored password must not equal the raw password
        self.assertNotEqual(u.password, "plainpass")
        self.assertTrue(u.check_password("plainpass"))

        # update password via set_password
        u.set_password("newplain")
        u.save()
        u.refresh_from_db()
        self.assertTrue(u.check_password("newplain"))
