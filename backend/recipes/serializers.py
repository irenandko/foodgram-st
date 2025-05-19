from rest_framework import serializers
from django.conf import settings
from rest_framework.exceptions import ValidationError
from foodgram.constants import (RECIPE_MIN_TIME,
                                INGREDIENT_MIN_AMOUNT,)
from users.serializers import ReformattingBase64, CustomUserSerializer

from recipes.models import (
    Ingredient, Recipe, RecipeIngredient,
    Favorites, ShoppingBasket
)


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для ингредиентов."""

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement')


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для ингридиентов и рецептов."""

    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all())
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement = serializers.ReadOnlyField(
        source='ingredient.measurement')
    amount = serializers.IntegerField(
        min_value=INGREDIENT_MIN_AMOUNT)

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement', 'amount')


class RecipeReadSerializer(serializers.ModelSerializer):
    """Сериализатор прочтения конкретного рецепта."""

    author = CustomUserSerializer(read_only=True)
    image = ReformattingBase64()
    ingredients = RecipeIngredientSerializer(
        many=True, source='recipeingredient_set', read_only=True
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_basket = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'author', 'name', 'image',
            'description', 'cooking_time', 'ingredients',
            'is_favorited', 'is_in_shopping_basket',
        )

    def _check_user_relation(self, related_manager):
        user = self.context.get('request').user
        return (user.is_authenticated and
                related_manager.filter(user=user).exists())

    def get_is_favorited(self, obj):
        return self._check_user_relation(obj.favorites)

    def get_is_in_shopping_cart(self, obj):
        return self._check_user_relation(obj.shopping_carts)


class RecipeWriteSerializer(serializers.ModelSerializer):
    """Сериализатор добавления конкретного рецепта."""

    image = ReformattingBase64()
    ingredients = RecipeIngredientSerializer(many=True)
    cooking_time = serializers.IntegerField(
        min_value=RECIPE_MIN_TIME,
    )

    class Meta:
        model = Recipe
        fields = (
            'id', 'name', 'image',
            'description', 'cooking_time', 'ingredients',
        )

    def validate(self, data):
        ingredients_data = self.initial_data.get('ingredients')

        if not ingredients_data:
            raise ValidationError(
                {"ingredients": ["Список ингредиентов не может быть пустым."]}
            )
        ingredient_ids = [item['id'] for item in ingredients_data]
        if len(ingredient_ids) != len(set(ingredient_ids)):
            raise ValidationError(
                {"ingredients": "Этот ингридиент уже использован."}
            )

        return data

    def create_ingredients(self, recipe, ingredients):
        RecipeIngredient.objects.bulk_create(
            RecipeIngredient(
                recipe=recipe,
                ingredient=item['id'],
                amount=item['amount']
            )
            for item in ingredients
        )

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        self.create_ingredients(recipe, ingredients)
        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients')
        instance = super().update(instance, validated_data)
        instance.recipeingredient_set.all().delete()
        self.create_ingredients(instance, ingredients)
        return instance

    def to_representation(self, instance):
        return RecipeReadSerializer(instance, context=self.context).data


class ShoppingBasketSerializer(serializers.ModelSerializer):
    """Сериализатор корзины."""

    class Meta:
        model = ShoppingBasket
        fields = ('user', 'recipe')
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=ShoppingBasket.objects.all(),
                fields=('user', 'recipe'),
                message='Ингридиенты рецепта уже в списке покупок.'
            )
        ]

    def to_representation(self, instance):
        return RecipeShortSerializer(instance.recipe,
                                     context=self.context).data


class FavoriteSerializer(serializers.ModelSerializer):
    """Сериализатор избранных рецептов."""

    class Meta:
        model = Favorites
        fields = ('user', 'recipe')
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=Favorites.objects.all(),
                fields=('user', 'recipe'),
                message='Рецепт уже добавлен в избранное.'
            )
        ]

    def to_representation(self, instance):
        return RecipeShortSerializer(instance.recipe,
                                     context=self.context).data


class RecipeShortSerializer(serializers.ModelSerializer):
    """Краткое отображение рецепта."""

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
