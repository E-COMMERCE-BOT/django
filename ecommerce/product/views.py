from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from django.http import Http404
from django.db import transaction

from .models import Product, Category
from .serializers import ProductSerializer, CategorySerializer

def get_descendants_ids(category):
    descendants = set()
    def collect_children(cat):
        for child in cat.children.all():
            descendants.add(child.id)
            collect_children(child)
    collect_children(category)
    return list(descendants | {category.id})

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = 'id'

    def get_queryset(self):
        qs = (Category.objects
              .select_related('parent')
              .prefetch_related('children'))

        if self.request.query_params.get('tree') == 'true':
            return qs

        parent_param = self.request.query_params.get('parent', None)

        if parent_param is None:
            return qs.filter(parent__isnull=True)

        if parent_param in ('', 'null', 'None'):
            return qs.filter(parent__isnull=True)

        try:
            parent_id = int(parent_param)
        except ValueError:
            raise ValidationError({'parent': 'Must be an integer or null'})

        return qs.filter(parent_id=parent_id)

    def get_object(self):
        queryset = Category.objects.all()
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field

        try:
            return queryset.get(pk=self.kwargs[lookup_url_kwarg])
        except Category.DoesNotExist:
            raise Http404("Сategory not found.")

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            descendants = get_descendants_ids(instance)

            with transaction.atomic():
                Category.objects.filter(id__in=descendants).delete()

            return Response(status=status.HTTP_204_NO_CONTENT)
        except Http404:
            return Response(
                {"error": "Сategory not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        
class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    lookup_field = 'id'

    def get_queryset(self):
        queryset = super().get_queryset()
        category_id = self.request.query_params.get('category_id')
        is_main = self.request.query_params.get('main', 'false') == 'true'

        if category_id:
            try:
                category = Category.objects.get(id=category_id)
            except Category.DoesNotExist:
                return queryset.none()
            
            if is_main and category.parent is None:
                descendant_ids = get_descendants_ids(category)
                queryset = queryset.filter(category__id__in=descendant_ids)
            else:
                queryset = queryset.filter(category__id=category_id)

        return queryset.distinct()

    def create(self, request, *args, **kwargs):
        if "photo" not in request.FILES:
            return Response(
                {"photo": ["This field is required."]},
                status=status.HTTP_400_BAD_REQUEST,
            )
        data = request.data.copy()
        data["photo"] = request.FILES["photo"]
        serializer = self.get_serializer(data=data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        data = request.data.copy()

        if "photo" in request.FILES:
            data["photo"] = request.FILES["photo"]

        serializer = self.get_serializer(
            instance, data=data, partial=True, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        return Response(serializer.data)
        
    