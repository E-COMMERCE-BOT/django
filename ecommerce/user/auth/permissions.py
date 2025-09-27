from rest_framework.permissions import BasePermission
from django.conf import settings

class IsBot(BasePermission):
    def has_permission(self, request, view):
        api_key = request.headers.get("X-Bot-Api-Key")
        return api_key == settings.BOT_API_KEY