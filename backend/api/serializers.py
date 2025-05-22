from rest_framework import serializers
from users.models import User, Subscription
from recipes.serializers import RecipeShortSerializer
from users.serializers import CustomUserSerializer


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

    def get_recipes(self, obj):
        request = self.context.get('request')
        limit = request.query_params.get('recipes_limit')
        queryset = obj.recipes.all()

        if limit and limit.isdigit():
            queryset = queryset[:int(limit)]

        return RecipeShortSerializer(
            queryset,
            many=True,
            context=self.context).data
