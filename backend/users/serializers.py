from rest_framework import serializers
from djoser.serializers import UserSerializer
from users.models import User, Subscription
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


class SubscriptionCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для оформления подписки на автора."""

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


class SubscriptionSerializer(CustomUserSerializer):
    """Сериализатор для деталей подписок."""

    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.ReadOnlyField(source='recipes.count')

    class Meta:
        model = User
        fields = CustomUserSerializer.Meta.fields + (
            'recipes', 'recipes_count',
        )


class AvatarSerializer(serializers.ModelSerializer):
    """Сериализатор отдельно для фото профиля (обновление)."""

    avatar = ReformattingBase64()

    class Meta:
        model = User
        fields = ('avatar',)
