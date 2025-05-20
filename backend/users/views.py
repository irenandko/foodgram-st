from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from djoser.views import UserViewSet

from users.serializers import (CustomUserSerializer,
                               AvatarSerializer,)
from api.serializers import (SubscriptionSerializer,
                             SubscriptionCreateSerializer,)

from users.models import User, Subscription


class CustomUserViewSet(UserViewSet):

    queryset = User.objects.all()
    serializer_class = CustomUserSerializer

    @action(
        methods=['get'],
        permission_classes=[IsAuthenticated],
        url_path='me',
        detail=False,
    )
    def me(self, request):
        serializer = CustomUserSerializer(request.user,
                                          context={'request': request}
                                          )
        return Response(serializer.data,
                        status=status.HTTP_200_OK)

    @action(methods=['put', 'delete'],
            permission_classes=[IsAuthenticated],
            url_path='me/avatar',
            detail=False,)
    def avatar(self, request):
        user = request.user
        if request.method == 'PUT':
            serializer = AvatarSerializer(user, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)

        user.avatar.delete(save=True)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(permission_classes=[IsAuthenticated],
            url_path='subscriptions',
            detail=False,)
    def subscriptions(self, request):
        authors = User.objects.filter(subscriptions__user=request.user)
        page = self.paginate_queryset(authors)
        serializer = SubscriptionSerializer(page,
                                            many=True,
                                            context={'request': request})
        return self.get_paginated_response(serializer.data)

    def _subscribe(self, request, id):

        author = get_object_or_404(User, pk=id)
        serializer = SubscriptionCreateSerializer(
            data={'user': request.user.id,
                  'author': author.id},
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data,
                        status=status.HTTP_201_CREATED)

    @action(methods=['post'],
            permission_classes=[IsAuthenticated],
            url_path='subscribe',
            detail=True,
            )
    def subscribe(self, request, id=None):
        return self._subscribe(request, id)

    def _unsubscribe(self, request, id):

        author = get_object_or_404(User, pk=id)
        deleted_county, _ = Subscription.objects.filter(
            user=request.user,
            author=author).delete()

        if deleted_county <= 0:
            return Response({'error': 'Подписка не найдена.'},
                            status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_204_NO_CONTENT)

    @subscribe.mapping.delete
    def unsubscribe(self, request, id=None):
        return self._unsubscribe(request, id)
