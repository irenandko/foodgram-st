from rest_framework import serializers
from djoser.serializers import UserSerializer
from users.models import User
from foodgram.reformat_image import ReformattingBase64


class CustomUserSerializer(UserSerializer):
    """Сериализатор для отображения данных пользователя."""

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


class AvatarSerializer(serializers.ModelSerializer):
    """Сериализатор отдельно для фото профиля (обновление)."""

    avatar = ReformattingBase64()

    class Meta:
        model = User
        fields = ('avatar',)
