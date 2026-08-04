from django.db import transaction
from rest_framework import status, viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from .models import Category, Product
from .serializers import CategorySerializer, ProductSerializer
from .services import get_descendant_ids


class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer

    def get_queryset(self):
        queryset = Category.objects.select_related("parent").prefetch_related(
            "children"
        )
        parent = self.request.query_params.get("parent")

        if parent is None or parent in {"", "null", "None"}:
            return queryset.filter(parent__isnull=True)

        try:
            parent_id = int(parent)
        except ValueError as exc:
            raise ValidationError(
                {"parent": "Must be an integer or null."}
            ) from exc

        return queryset.filter(parent_id=parent_id)

    @transaction.atomic
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        Category.objects.filter(
            id__in=get_descendant_ids(instance)
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer

    def get_queryset(self):
        queryset = Product.objects.select_related("category")
        category_id = self.request.query_params.get("category_id")
        include_descendants = (
            self.request.query_params.get("main", "false").lower()
            == "true"
        )

        if not category_id:
            return queryset

        try:
            category = Category.objects.get(pk=int(category_id))
        except (Category.DoesNotExist, ValueError):
            return queryset.none()

        if include_descendants:
            return queryset.filter(
                category_id__in=get_descendant_ids(category)
            )

        return queryset.filter(category=category)
