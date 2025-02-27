from rest_framework import serializers
from rest_framework.reverse import reverse

from shortener.models import LinkMapped
from recipes.models import Recipe


class ShortenerSerializer(serializers.ModelSerializer):
    """Get short-link serializer."""

    class Meta:
        model = LinkMapped
        fields = ('original_url',)
        write_only_fields = ('original_url',)

    def get_short_link(self, obj):
        request = self.context.get('request')
        return request.build_absolute_uri(
            reverse(
                'shortener:load_url',
                args=[obj.url_hash]
            )
        )

    def create(self, validated_data):
        instance, _ = LinkMapped.objects.get_or_create(**validated_data)
        return instance

    def to_representation(self, instance):
        return {
            'short-link': self.get_short_link(instance)
        }


class ShortRecipeSerializer(serializers.ModelSerializer):
    """Short data in recipes serializer."""

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )
