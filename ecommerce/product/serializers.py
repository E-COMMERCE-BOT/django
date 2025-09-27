from rest_framework import serializers
from django.conf import settings

from .models import Category, Product

class RecursiveCategorySerializer(serializers.Serializer):
    def to_representation(self, value):
        serializer = self.parent.parent.__class__(value, context=self.context)
        return serializer.data

class CategorySerializer(serializers.ModelSerializer):
    children = RecursiveCategorySerializer(many=True, read_only=True)
    class Meta:
        model = Category
        fields = ['id', 'name', 'parent', 'children']


class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), source='category', write_only=True
    )
    is_available = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)

    class Meta:
        model = Product
        fields = '__all__'

    def get_is_available(self, obj):
        return obj.is_available()

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if instance.photo:
            photo_path = instance.photo.url 
            photo_url = f"{settings.SITE_URL}{photo_path}"
            representation['photo'] = photo_url
        else:
            representation['photo'] = None
        return representation