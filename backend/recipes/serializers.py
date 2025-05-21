from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from foodgram.reformat_image import ReformattingBase64

from recipes.models import (
    Ingredient,
    Recipe,
    Favorite,
    ShoppingCart,
    IngredientInRecipe
)
from users.serializers import CustomUserSerializer

from foodgram.constants import (RECIPE_MIN_TIME,
                                RECIPE_MAX_TIME,
                                INGREDIENT_MIN_AMOUNT,
                                INGREDIENT_MAX_AMOUNT,)


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для представления ингредиента в рецепте."""

    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all())
    name = serializers.ReadOnlyField(source='ingredient.name')
    amount = serializers.IntegerField(
        min_value=INGREDIENT_MIN_AMOUNT,
        max_value=INGREDIENT_MAX_AMOUNT)
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')

    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'name', 'amount', 'measurement_unit',)


class RecipeReadSerializer(serializers.ModelSerializer):
    """Сериализатор для чтения рецепта."""

    image = ReformattingBase64()
    author = CustomUserSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'image',
            'author',
            'name',
            'cooking_time',
            'ingredients',
            'text',
            'is_favorited',
            'is_in_shopping_cart',
        )

    def _check_user_relation(self, related_manager):
        user = self.context.get('request').user
        return (
            user.is_authenticated
            and related_manager.filter(user=user).exists()
        )

    def get_is_favorited(self, obj):
        return self._check_user_relation(obj.favorites)

    def get_is_in_shopping_cart(self, obj):
        return self._check_user_relation(obj.shopping_carts)
 
    def get_ingredients(self, obj):
        ingredients = []
        for ingredient_in_recipe in obj.ingredientinrecipe_set.all():
            ingredient = ingredient_in_recipe.ingredient
            ingredients.append({
                'id': ingredient.id,
                'name': ingredient.name,
                'amount': ingredient_in_recipe.amount,
                'measurement_unit': ingredient.measurement_unit
            })
        return ingredients


class RecipeWriteSerializer(serializers.ModelSerializer):
    """Сериализатор для создания и обновления рецептов."""

    image = ReformattingBase64()
    cooking_time = serializers.IntegerField(
        min_value=RECIPE_MIN_TIME,
        max_value=RECIPE_MAX_TIME
    )
    ingredients = RecipeIngredientSerializer(many=True)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'image',
            'name',
            'cooking_time',
            'ingredients',
            'text',
        )

    def validate(self, data):
        ingreds_data = self.initial_data.get('ingredients')

        if not ingreds_data:
            raise ValidationError(
                {'ingredients': [
                    'В рецепте должен содержаться хотя бы один ингридиент.'
                ]}
            )
        ingredients_ids = [item['id'] for item in ingreds_data]
        if len(ingredients_ids) != len(set(ingredients_ids)):
            raise ValidationError(
                {'ingredients':
                 ['Этот ингридиент уже использован в списке ингредиентов.']}
            )
        return data

    def create_ingredients(self, recipe, ingredients):
        IngredientInRecipe.objects.bulk_create(
            IngredientInRecipe(
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
        instance.ingredientinrecipe_set.all().delete()
        self.create_ingredients(instance, ingredients)
        return instance

    def to_representation(self, instance):
        return RecipeReadSerializer(
            instance,
            context=self.context).data


class FavoriteSerializer(serializers.ModelSerializer):
    """Сериализатор для добавления рецепта в избранное."""

    class Meta:
        model = Favorite
        fields = ('user', 'recipe')
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=Favorite.objects.all(),
                fields=('user', 'recipe'),
                message='Рецепт уже добавлен в избранное.'
            )
        ]

    def to_representation(self, instance):
        return RecipeShortSerializer(
            instance.recipe,
            context=self.context).data


class ShoppingCartSerializer(serializers.ModelSerializer):
    """Сериализатор для добавления рецепта в список покупок."""

    class Meta:
        model = ShoppingCart
        fields = ('user', 'recipe',)
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=ShoppingCart.objects.all(),
                fields=('user', 'recipe'),
                message='Рецепт уже в списке покупок.'
            )
        ]

    def to_representation(self, instance):
        return RecipeShortSerializer(
            instance.recipe,
            context=self.context).data


class RecipeShortSerializer(serializers.ModelSerializer):
    """Сериализатор для сокращенного представления рецепта."""

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time',)


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для представления данных ингредиента."""

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')
