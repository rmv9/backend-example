from io import BytesIO

from django.db.models import Exists, OuterRef
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.reverse import reverse

from recipes import models
from recipes.purchase_product import generate_pdf_file
from users.models import Subscriber
from ..filters import IngredientFilterSet, RecipeFilterSet
from ..paginations import FoodgramPagination
from ..permissions import IsOwnerOrReadOnly
from ..shortener.serializers import ShortenerSerializer
from . import serializers


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Tag viewset."""

    queryset = models.Tag.objects.all()
    serializer_class = serializers.TagSerializer
    permission_classes = [permissions.AllowAny]


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Ingredients viewset."""

    queryset = models.Ingredient.objects.all()
    serializer_class = serializers.IngredientSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend]
    filterset_class = IngredientFilterSet


class RecipeViewSet(viewsets.ModelViewSet):
    """Recipes viewset."""

    http_method_names = ['get', 'post', 'patch', 'delete']
    pagination_class = FoodgramPagination
    permission_classes = [IsOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilterSet

    def get_serializer_class(self):
        serializer_map = {
            'list': serializers.RecipeSerializer,
            'retrieve': serializers.RecipeSerializer,
            'get_link': ShortenerSerializer,
            'favorite': serializers.FavoriteSerializer,
            'shopping_cart': serializers.ShoppingCartSerializer
        }
        return serializer_map.get(
            self.action, serializers.RecipeCreateSerializer
        )

    def get_queryset(self):
        user = self.request.user
        qs = models.Recipe.objects
        if self.action in ['list', 'retrieve']:
            qs = (
                qs.select_related('author')
                .prefetch_related(
                    'recipe_ingredients__ingredient',
                    'recipe_ingredients',
                    'tags',
                    Subscriber.get_prefetch_subscribers(
                        'author__subscribers', user
                    ),
                )
                .annotate(
                    is_favorited=Exists(
                        user.favorites.filter(recipe=OuterRef('pk'))
                    ),
                    is_in_shopping_cart=Exists(
                        user.shopping_cart.filter(recipe=OuterRef('pk'))
                    ),
                )
                .all()
            )

        return qs.order_by('-created_at').all()

    @action(
        methods=['get'],
        detail=False,
        url_name='download',
    )
    def download_shopping_cart(self, request):
        """Shopping cart list."""
        recipes = request.user.shopping_cart.values_list(
            'recipe__name',
            flat=True
        ).order_by('recipe__name')
        ingredients = models.RecipeIngredient.get_shopping_ingredients(
            request.user
        )

        pdf_file = generate_pdf_file(ingredients, recipes, request)

        return FileResponse(
            BytesIO(pdf_file),
            as_attachment=True,
            filename='foodgram_shopping_list.pdf',
        )

    @action(
        methods=['post'],
        detail=True,
        url_name='shopping-cart',
    )
    def shopping_cart(self, request, pk=None):
        """Add recipe to shopping cart."""
        return self._post_author_recipe(request, pk)

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, pk=None):
        """Del recipe from shp cart."""
        return self._delete_author_recipe(request, pk, models.ShoppingCart)

    @action(
        methods=['post'],
        detail=True,
    )
    def favorite(self, request, pk=None):
        """Add recipes to favorites."""
        return self._post_author_recipe(request, pk)

    @favorite.mapping.delete
    def delete_favorite(self, request, pk=None):
        """Del recipes from favorites."""
        return self._delete_author_recipe(request, pk, models.FavoriteRecipe)

    @action(
        methods=['get'],
        detail=True,
        url_path='get-link',
        url_name='get-link',
    )
    def get_link(self, request, pk=None):
        """Short link."""
        self.get_object()
        original_url = request.META.get('HTTP_REFERER')
        if original_url is None:
            url = reverse('api:recipe-detail', kwargs={'pk': pk})
            original_url = request.build_absolute_uri(url)
        serializer = self.get_serializer(
            data={'original_url': original_url},
            context={'request': request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)

    def _post_author_recipe(self, request, pk):
        """Add authors recipe."""
        serializer = self.get_serializer(data=dict(recipe=pk))
        serializer.is_valid(raise_exception=True)
        serializer.save(author=self.request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def _delete_author_recipe(self, request, pk, model):
        """Del author recipe."""
        recipe = get_object_or_404(models.Recipe, pk=pk)
        obj_count, _ = model.objects.filter(
            author=self.request.user,
            recipe=recipe,
        ).delete()

        if not obj_count:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_204_NO_CONTENT)
