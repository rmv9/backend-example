from django.db import transaction
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from api.users.serializers import UserSerializer
from recipes.models import (
    FavoriteRecipe,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Tag,
)

msg = {
    'required': 'Поле обязательно для заполнения',
    'image': 'Треубется изображение',
    'tag': 'Тег не выбран',
    'uniq_tag': 'Тег уже добавлен',
    'ingredient': 'Ингредиент не выбран',
    'uniq_ingredient': 'Ингредиент уже добавлен',
}


class TagSerializer(serializers.ModelSerializer):
    """Tags serializer"""

    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    """Ingredient serializer"""

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientGetSerializer(serializers.ModelSerializer):
    """Ingredients list serializer"""

    id = serializers.IntegerField(
        source='ingredient.id'
    )
    name = serializers.CharField(
        source='ingredient.name'
    )
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount'
        )


class RecipeIngredientPredictSerializer(serializers.ModelSerializer):
    """Recipe short prediction serializer"""

    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        source='ingredient',
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    """Recipe serializer"""

    author = UserSerializer(read_only=True)
    image = Base64ImageField()
    tags = TagSerializer(many=True)
    ingredients = IngredientGetSerializer(
        many=True, source='recipe_ingredients'
    )
    is_favorited = serializers.BooleanField(
        default=False, read_only=True
    )
    is_in_shopping_cart = serializers.BooleanField(
        default=False, read_only=True
    )

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )


class RecipeCreateSerializer(serializers.ModelSerializer):
    """Recipe creator serializer"""

    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    ingredients = RecipeIngredientPredictSerializer(
        many=True,
        source='recipe_ingredients'
    )
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time',
        )

    def validate_image(self, image_data):
        if image_data is None:
            raise serializers.ValidationError(msg['image'])
        return image_data

    def validate(self, attrs):
        tags = attrs.get('tags', [])
        if len(tags) == 0:
            raise serializers.ValidationError(msg['tag'])

        if len(set(tags)) != len(tags):
            raise serializers.ValidationError(msg['uniq_tag'])

        ingredients = attrs.get('recipe_ingredients', [])
        if len(ingredients) == 0:
            raise serializers.ValidationError(msg['ingredient'])

        id_ingredients = {
            ingredient['ingredient'] for ingredient in ingredients
        }
        if len(ingredients) != len(id_ingredients):
            raise serializers.ValidationError(
                msg['uniq_ingredient']
            )

        return attrs

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('recipe_ingredients')
        with transaction.atomic():
            recipe = Recipe.objects.create(
                author=self.context['request'].user, **validated_data
            )
            self.add_tags_and_ingrdnts_to_rec(recipe, tags, ingredients)
            return recipe

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('recipe_ingredients')
        with transaction.atomic():
            instance.ingredients.clear()
            instance.tags.clear()
            self.add_tags_and_ingrdnts_to_rec(
                instance, tags, ingredients
            )
            super().update(instance, validated_data)
            return instance

    @staticmethod
    def add_tags_and_ingrdnts_to_rec(recipe, tags, ingredients):
        """Add and put tags/ingredients"""
        recipe.tags.set(tags)
        RecipeIngredient.objects.bulk_create(
            RecipeIngredient(
                recipe=recipe,
                ingredient=ingredient['ingredient'],
                amount=ingredient['amount'],
            )
            for ingredient in ingredients
        )

    def to_representation(self, instance):
        return RecipeSerializer(instance, context=self.context).data


class ShortRecipeSerializer(serializers.ModelSerializer):
    """Short data serializer"""

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )


class AuthorRecipeSerializer(serializers.ModelSerializer):
    """Author and recipe base serializer model"""

    _recipe_added_to: str = None

    class Meta:
        model = None
        fields = ('author', 'recipe')
        read_only_fields = ('author',)

    def validate(self, attrs):
        recipe = attrs['recipe']
        user = self.context['request'].user
        if self.Meta.model.objects.filter(author=user, recipe=recipe).exists():
            raise serializers.ValidationError(
                f'Рецепт уже добавлен в {self._recipe_added_to}'
            )
        return attrs

    def to_representation(self, instance):
        return ShortRecipeSerializer(
            instance.recipe, context=self.context
        ).data


class FavoriteSerializer(AuthorRecipeSerializer):
    """Favorite recipes serializer"""

    _recipe_added_to = 'избранное'

    class Meta(AuthorRecipeSerializer.Meta):
        model = FavoriteRecipe


class ShoppingCartSerializer(AuthorRecipeSerializer):
    """Shopping cart serializer"""

    _recipe_added_to = 'корзину'

    class Meta(AuthorRecipeSerializer.Meta):
        model = ShoppingCart
