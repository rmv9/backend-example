from django.contrib import admin
from django.utils.html import format_html

from core.constants import INGR_MIN
from .models import (
    FavoriteRecipe, Ingredient,
    Recipe, RecipeIngredient,
    ShoppingCart, Tag,
)

hlp_txt = {
    'search_rec_user': 'Поиск по названию или `username` автора',
    'search_ing_name': 'Поиск по ингредиенту',
    # 'search_ing_unit': 'Поиск по ед измерения',
}


class RecipeIngredientInline(admin.TabularInline):
    """ingredients -> str"""

    model = RecipeIngredient
    extra = 1
    min_num = INGR_MIN


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Recipes admin-zone"""

    list_display = ('name', 'author')
    list_display_links = ('name', 'author')
    search_fields = ('name', 'author__username')
    search_help_text = hlp_txt['search_rec_user']
    filter_horizontal = ('tags',)
    list_filter = ('tags',)
    readonly_fields = ('in_favorites',)
    inlines = [RecipeIngredientInline]

    fieldsets = (
        (
            None,
            {
                'fields': (
                    'author',
                    ('name', 'cooking_time', 'in_favorites'),
                    'text',
                    'image',
                    'tags',
                )
            },
        ),
    )

    @admin.display(
        description=format_html('<strong>Рецептов в избранных</strong>')
    )
    def in_favorites(self, obj):
        """Fav Recipes count"""
        return FavoriteRecipe.objects.filter(recipe=obj).count()


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Tags admin-zone"""

    list_display = ('id', 'name', 'slug')
    list_display_links = ('id', 'name', 'slug')


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Ingr admin-zone"""

    list_display = ('name', 'measurement_unit')
    list_display_links = ('name',)
    search_fields = ('name',)
    search_help_text = hlp_txt['search_ing_name']


@admin.register(FavoriteRecipe, ShoppingCart)
class AuthorRecipeAdmin(admin.ModelAdmin):
    """Shoppingcart and fav rec admin-zone"""

    list_display = ('id', '__str__')
    list_display_links = ('id', '__str__')
