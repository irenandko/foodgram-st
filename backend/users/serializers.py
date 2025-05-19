import base64
import imghdr

from rest_framework import serializers
from djoser.serializers import UserSerializer
from django.core.files.base import ContentFile
from users.models import User, Subscription
from recipes.serializers import RecipeShortSerializer


class ReformattingBase64(serializers.ImageField):
    """Переформатирование фото профиля из base64."""

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, img_str = data.split(';base64,')
            ext = imghdr.what(None, h=base64.b64decode(img_str))
            content = ContentFile(
                base64.b64decode(img_str),
                name=f'temp.{ext}')

        return super().to_internal_value(content)


class CustomUserSerializer(UserSerializer):
    """Сериализатор для пользователя."""

    avatar = ReformattingBase64()
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = UserSerializer.Meta.fields + ('avatar', 'is_subscribed')

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        return (request
                and request.user.is_authenticated
                and obj.subscriptions.filter(user=request.user).exists())


class SubscriptionSerializer(CustomUserSerializer):
    """Сериализатор для подписок."""

    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.ReadOnlyField(source='recipes.count')

    class Meta:
        model = User
        fields = CustomUserSerializer.Meta.fields + (
            'recipes', 'recipes_count',
        )

    def get_recipes(self, obj):
        request = self.context.get('request')
        limit = request.query_params.get('recipes_limit')
        queryset = obj.recipes.all()
        if limit and limit.isdigit():
            queryset = queryset[:int(limit)]
        return RecipeShortSerializer(queryset, many=True,
                                     context=self.context).data


class SubscriptionCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для оформления подписки."""

    class Meta:
        model = Subscription
        fields = ('user', 'author')
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=Subscription.objects.all(),
                fields=('user', 'author'),
                message='Уже подписан на этого пользователя.'
            )
        ]

    def validate(self, data):
        if data['user'] == data['author']:
            raise serializers.ValidationError('Нельзя подписаться на себя.')
        return data

    def to_representation(self, instance):
        return SubscriptionSerializer(instance.author,
                                      context=self.context).data


class AvatarSerializer(serializers.ModelSerializer):
    """Сериализатор для фото профиля."""

    avatar = ReformattingBase64()

    class Meta:
        model = User
        fields = ('avatar',)
