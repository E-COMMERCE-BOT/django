import secrets

from django.conf import settings
from rest_framework.permissions import BasePermission


class IsBot(BasePermission):
    message = "Invalid bot API key."

    def has_permission(self, request, view) -> bool:
        provided = request.headers.get("X-Bot-Api-Key", "")
        expected = settings.BOT_API_KEY

        return bool(
            provided
            and expected
            and secrets.compare_digest(provided, expected)
        )
