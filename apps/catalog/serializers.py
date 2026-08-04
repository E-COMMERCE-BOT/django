from rest_framework import serializers

from .models import Category, Product


class RecursiveCategorySerializer(serializers.Serializer):
    def to_representation(self, value):
        return CategorySerializer(value, context=self.context).data


class CategorySerializer(serializers.ModelSerializer):
    children = RecursiveCategorySerializer(many=True, read_only=True)

    class Meta:
        model = Category
        fields = ("id", "name", "parent", "children")


class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        source="category",
        write_only=True,
    )
    is_available = serializers.BooleanField(read_only=True)
    photo = serializers.ImageField(use_url=True)

    class Meta:
        model = Product
        fields = (
            "id",
            "name",
            "description",
            "photo",
            "price",
            "stock",
            "category",
            "category_id",
            "is_available",
            "created_at",
        )
        read_only_fields = ("id", "created_at", "is_available")
