from api.users.urls import user_router
from django.urls import include, path

app_name = 'api'

urlpatterns = [
    path('', include('api.recipes.urls')),
    path('', include(user_router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]
