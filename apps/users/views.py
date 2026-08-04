from rest_framework import mixins, status, viewsets
from rest_framework.response import Response

from .models import User
from .serializers import UserSerializer


class UserViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = "tg_id"

    def create(self, request, *args, **kwargs):
        tg_id = request.data.get("tg_id")
        if not tg_id:
            return Response(
                {"detail": "tg_id is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user, created = User.objects.get_or_create(tg_id=tg_id)
        return Response(
            self.get_serializer(user).data,
            status=(
                status.HTTP_201_CREATED
                if created
                else status.HTTP_200_OK
            ),
        )
