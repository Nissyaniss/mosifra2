import base64

import requests
from django.conf import settings
from django.core.mail.backends.smtp import EmailBackend
from django.core.mail.utils import DNS_NAME

"""Pour envoyer des mails avec gmail en oauth2
On demande un access token à Google
Puis on se connecte au server smtp.
"""
class GmailOAuth2Backend(EmailBackend):
    token_url = "https://oauth2.googleapis.com/token"

    def open(self) -> bool:
        #Connexion au serveur SMTP et login xoauth
        if not super().open():
            return False

        access_token = self._get_access_token()
        self._login_with_token(access_token)
        return True

    def _get_access_token(self) -> str:
        client_id = getattr(settings, "GMAIL_CLIENT_ID", "")
        client_secret = getattr(settings, "GMAIL_CLIENT_SECRET", "")
        refresh_token = getattr(settings, "GMAIL_REFRESH_TOKEN", "")

        if not client_id or not client_secret or not refresh_token:
            raise RuntimeError("Google OAuth2: renseigne les variables GMAIL_* dans settings.")

        payload = {
            "client_id": client_id,
            "client_secret": client_secret,
            "refresh_token": refresh_token,
            "grant_type": "refresh_token",
        }

        try:
            response = requests.post(self.token_url, data=payload, timeout=10)
            response.raise_for_status()
        except requests.RequestException as exc:
            raise RuntimeError("Google OAuth2: impossible d’obtenir un access token.") from exc

        data = response.json()
        token = data.get("access_token")
        if not token:
            raise RuntimeError("Google OAuth2: la réponse ne contient pas d’access_token.")
        return token

    def _login_with_token(self, token: str) -> None:
        if not self.connection:
            raise RuntimeError("Google OAuth2: la connexion SMTP n’est pas ouverte.")

        fqdn = DNS_NAME.get_fqdn()
        self.connection.ehlo(fqdn)

        raw_auth = f"user={self.username}\x01auth=Bearer {token}\x01\x01"
        encoded_auth = base64.b64encode(raw_auth.encode("utf-8")).decode("utf-8")

        code, response = self.connection.docmd("AUTH", "XOAUTH2 " + encoded_auth)
        if code != 235:
            text = response.decode("utf-8", errors="ignore")
            raise RuntimeError(f"Google OAuth2: XOAUTH2 a échoué ({code} {text}).")
