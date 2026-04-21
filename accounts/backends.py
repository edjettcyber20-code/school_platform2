"""
Backend d'authentification permettant la connexion par email OU username.
"""
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q
from accounts.models import User


class EmailOrUsernameBackend(ModelBackend):
    """
    Permet la connexion avec l'adresse email ou le nom d'utilisateur.
    Compatible avec l'interface Django admin et le login personnalisé.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None or password is None:
            return None
        try:
            # Cherche par email OU par username (insensible à la casse)
            user = User.objects.get(Q(email__iexact=username) | Q(username__iexact=username))
        except User.DoesNotExist:
            # Exécution fictive pour éviter les attaques temporelles
            User().set_password(password)
            return None
        except User.MultipleObjectsReturned:
            # En cas de doublons d'email, tenter via username exact
            try:
                user = User.objects.get(username__iexact=username)
            except User.DoesNotExist:
                return None

        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
