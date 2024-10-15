from django.urls import include, path
from rest_framework import routers

from . import views


router = routers.DefaultRouter()
router.register('tags', views.TagViewSet, 'tag')
router.register('recipes', views.RecipeViewSet, 'recipe')
router.register('ingredients', views.IngredientViewSet, 'ingredient')

urlpatterns = [
    path('', include(router.urls)),
]
