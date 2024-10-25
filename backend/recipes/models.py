from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django_cleanup.cleanup import cleanup_select

from core import abstract_models
from core.constants import (
    INGR_MAX, INGR_MIN, INGR_NAME_MAX,
    MIN_COOKING_TM, REC_NAME_MAX, TAG_MAX,
    VALUE_MAX,
)

class Tag(models.Model):
    """Tag model"""

    name = models.CharField(
        verbose_name='Название',
        max_length=TAG_MAX,
        unique=True
    )
    slug = models.SlugField(
        verbose_name='Слаг',
        max_length=TAG_MAX,
        unique=True
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ('name',)

    def __str__(self):
        return self.name


class LowerField(models.CharField):
    """Field -> lowercase for ingredients"""

    def get_prep_value(self, value):
        return str(value).lower()


class Ingredient(models.Model):
    """Ingred model"""

    name = LowerField(
        'Название',
        max_length=INGR_MAX,
        db_index=True,

    )
    measurement_unit = models.CharField(
        'Единицы измерения',
        max_length=INGR_NAME_MAX
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='name_measurement_unit',
            )
        ]

    def __str__(self):
        return f'{self.name} ({self.measurement_unit})'


@cleanup_select
class Recipe(abstract_models.AuthorCreatedModel):
    """Recipe model"""

    image = models.ImageField(
        'Картинка',
        upload_to='recipes/'
    )
    name = models.CharField(
        'Название',
        max_length=REC_NAME_MAX
    )
    text = models.TextField('Описание')
    cooking_time = models.PositiveSmallIntegerField(
        'Время приготовления (мин)',
        validators=[
            MinValueValidator(
                MIN_COOKING_TM,
                f'Не должно быть меньше {MIN_COOKING_TM}',
            ),
            MaxValueValidator(
                VALUE_MAX,
                f'Не должно быть больше {VALUE_MAX}',
            ),
        ],
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Теги'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='Ингредиенты',
        through='RecipeIngredient'
    )

    class Meta:
        ordering = ('-created_at',)
        default_related_name = 'recipes'
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    """Recipe-Ingredient related model"""

    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE
    )
    amount = models.PositiveSmallIntegerField(
        'Количество',
        validators=[
            MinValueValidator(
                INGR_MIN,
                f'Не может быть меньше {INGR_MIN}',
            ),
            MaxValueValidator(
                VALUE_MAX,
                f'Не может быть больше {VALUE_MAX}',
            ),
        ],
    )

    @classmethod
    def get_shopping_ingredients(cls, user):
        """
        :param user:
        :return: [
                    {
                        'name': str,
                        'unit': str,
                        'count': int
                    },
                ]
        """

        return (
            cls.objects.filter(
                models.Q(recipe__in=user.shopping_cart.values('recipe'))
            )
            .values(name=models.F('ingredient__name'))
            .annotate(
                unit=models.F('ingredient__measurement_unit'),
                count=models.Sum('amount'),
            )
            .order_by('ingredient__name')
        )

    class Meta:
        default_related_name = 'recipe_ingredients'
        constraints = [
            models.UniqueConstraint(
                fields=['ingredient', 'recipe'],
                name='unique ingredient'
            )
        ]
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return f'{self.ingredient} - {self.amount}'


class FavoriteRecipe(abstract_models.AuthorRecipeModel):
    """Fav recipes model"""

    class Meta:
        default_related_name = 'favorites'
        verbose_name = 'Избранное'
        verbose_name_plural = verbose_name
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'recipe'],
                name='unique recipe favorite'
            )
        ]

    def __str__(self):
        return f'{self.recipe.name!r} в избранном у {self.author.username!r}'


class ShoppingCart(abstract_models.AuthorRecipeModel):
    """Shoppingcart model."""

    class Meta:
        default_related_name = 'shopping_cart'
        verbose_name = 'Корзина'
        verbose_name_plural = verbose_name
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'recipe'],
                name='unique recipe shopping cart'
            )
        ]

    def __str__(self):
        return f'{self.recipe.name!r} в корзине {self.author.username!r}'
