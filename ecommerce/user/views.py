import logging
from rest_framework import viewsets, mixins, status
from rest_framework.response import Response
from dotenv import load_dotenv
from django.http import Http404

from .models import User
from .serializers import UserSerializer


load_dotenv()
logger = logging.getLogger(__name__)

class UserViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet
):
    lookup_field = 'tg_id'
    queryset = User.objects.all().order_by("-created_at")
    serializer_class = UserSerializer

    def get_object(self):
        tg_id = self.kwargs[self.lookup_field]
        try:
            return User.objects.get(tg_id=tg_id)
        except User.DoesNotExist:
            logger.error(f"User tg_id={tg_id} not found")
            raise Http404

    def create(self, request):
        data = request.data
        tg_id = data.get('tg_id')
        if not tg_id:
            logger.error("tg_id is required for user creation")
            return Response({"detail": "tg_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        user, created = User.objects.get_or_create(
            tg_id=tg_id,
        )

        serializer = UserSerializer(user)
        status_code = status.HTTP_201_CREATED if created else status.HTTP_200_OK
        logger.info(f"User tg_id={tg_id} {'created' if created else 'found'}, status={status_code}")
        return Response(serializer.data, status=status_code)

    def retrieve(self, request, *args, **kwargs):
        user = self.get_object()
        return Response(UserSerializer(user).data)

    def partial_update(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            logger.info(f"User tg_id={user.tg_id} updated successfully")
            return Response(serializer.data)
        logger.error(f"Incorrect user data tg_id={user.tg_id}: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)