from django.conf import settings
from django.db import models


class AuthorModel(models.Model):
    """Author abstr"""

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='Автор',
    )

    class Meta:
        abstract = True

    def __str__(self):
        return f'{self.author.username!r}'


class AuthorRecipeModel(AuthorModel):
    """Recipe abstr"""

    recipe = models.ForeignKey(
        'recipes.Recipe',
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )

    class Meta:
        abstract = True


class AuthorCreatedModel(AuthorModel):
    """Abstract create model by auth"""

    created_at = models.DateTimeField(
        'Создано',
        auto_now_add=True
    )

    class Meta:
        abstract = True
