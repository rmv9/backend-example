from django.contrib.auth import get_user_model
from djoser import views as djoser_views
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from users.models import Subscriber

from ..paginations import FoodgramPagination
from .serializers import AvatarSerializer, SubscribeSerializer

User = get_user_model()


class UserViewSet(djoser_views.UserViewSet):
    """Вьюсет Пользователей"""

    pagination_class = FoodgramPagination

    def get_queryset(self):
        user = self.request.user
        if self.action in ('list', 'retrieve'):
            return (
                User.objects.prefetch_related(
                    Subscriber.get_prefetch_subscribers('subscribers', user),
                )
                .order_by('id')
                .all()
            )

        elif self.action in ('subscriptions',):
            return (
                Subscriber.objects.filter(user=user)
                .prefetch_related(
                    Subscriber.get_prefetch_subscribers(
                        'author__subscribers', user
                    ),
                    'author__recipes',
                )
                .order_by('id')
                .all()
            )

        elif self.action in ('subscribe',):
            return User.objects.prefetch_related(
                Subscriber.get_prefetch_subscribers('subscribers', user),
            ).all()

        return User.objects.all()

    @action(
        methods=['get'],
        detail=False,
        permission_classes=[IsAuthenticated],
        url_name='me',
    )
    def me(self, request, *args, **kwargs):
        """Данные о себе"""
        return super().me(request, *args, **kwargs)

    @action(
        methods=['put'],
        detail=False,
        permission_classes=[IsAuthenticated],
        url_path='me/avatar',
        url_name='me-avatar',
    )
    def avatar(self, request):
        """Добавление или удаление аватара"""
        serializer = self._change_avatar(request.data)
        return Response(serializer.data)

    @avatar.mapping.delete
    def delete_avatar(self, request):
        data = request.data
        if 'avatar' not in data:
            data = {'avatar': None}
        self._change_avatar(data)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=['get'],
        detail=False,
        permission_classes=[IsAuthenticated],
        url_path='subscriptions',
        url_name='subscriptions',
    )
    def subscriptions(self, request):
        """Список подписок"""
        page = self.paginate_queryset(self.get_queryset())
        serializer = SubscribeSerializer(
            page, many=True, context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(
        methods=['post'],
        detail=True,
        permission_classes=[IsAuthenticated],
        url_path='subscribe',
        url_name='subscribe',
    )
    def subscribe(self, request, id):
        """Подписка или отписка пользователя"""
        serializer = SubscribeSerializer(
            data={'author': self.get_object()},
            context={'request': request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @subscribe.mapping.delete
    def unsubscribe(self, request, id):
        subscriber_deleted, _ = Subscriber.objects.filter(
            author=self.get_object(), user=request.user
        ).delete()

        if subscriber_deleted == 0:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def _change_avatar(self, data):
        instance = self.get_instance()
        serializer = AvatarSerializer(instance, data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return serializer
