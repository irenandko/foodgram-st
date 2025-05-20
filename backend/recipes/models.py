from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator

from foodgram.constants import (RECIPE_MIN_TIME,
                                RECIPE_NAME_MAX_LEN,
                                INGREDIENT_MIN_AMOUNT,
                                INGREDIENT_NAME_MAX_LEN,
                                MEASUREMENT_UNIT_MAX_LEN)

User = get_user_model()


class Ingredient(models.Model):
    """Модель, содержащая информацию о конкретном ингридиенте."""

    name: models.CharField = models.CharField(
        max_length=INGREDIENT_NAME_MAX_LEN,
        verbose_name='Название ингредиента')
    measurement_unit: models.CharField = models.CharField(
        max_length=MEASUREMENT_UNIT_MAX_LEN,
        verbose_name='Единицы измерения')

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='unique_ingredient'
            )
        ]
        ordering = ['-name',]

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'


class Recipe(models.Model):
    """Модель, содержащая информацию о конкретном рецепте."""

    image = models.ImageField(
        upload_to='recipes/images/',
        verbose_name='Фото блюда')
    author: models.ForeignKey = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор рецепта',
        related_name='recipes',
    )
    name: models.CharField = models.CharField(
        max_length=RECIPE_NAME_MAX_LEN,
        verbose_name='Название рецепта')
    cooking_time: models.PositiveSmallIntegerField = (
        models.PositiveSmallIntegerField(
            verbose_name='Время приготовления',
            validators=[
                MinValueValidator(RECIPE_MIN_TIME),
            ],
        )
    )
    ingredients: models.ManyToManyField = models.ManyToManyField(
        Ingredient,
        through='IngredientInRecipe',
        related_name='recipes',
        verbose_name='Ингридиенты'
    )
    text: models.TextField = models.TextField(verbose_name='Описание рецепта')
    pub_date: models.DateTimeField = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации')

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        default_related_name = 'recipes'
        ordering = ['-pub_date',]

    def __str__(self):
        return self.name


class UserRecipeRelation(models.Model):
    """Модель связи пользователя с рецептом."""

    user: models.ForeignKey = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь'
    )
    recipe: models.ForeignKey = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )

    class Meta:
        abstract = True
        constraints = [
            models.UniqueConstraint(fields=['user', 'recipe',],
                                    name='%(class)s_unique')
        ]

    def __str__(self):
        return f'{self.user} -> {self.recipe}'


class ShoppingCart(UserRecipeRelation):
    """Модель списка покупок для пользователя."""

    class Meta(UserRecipeRelation.Meta):
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        default_related_name = 'shopping_carts'


class Favorite(UserRecipeRelation):
    """Модель избранных пользователем рецептов."""

    class Meta(UserRecipeRelation.Meta):
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        default_related_name = "favorites"


class IngredientInRecipe(models.Model):
    """Модель связи ингридиентов и рецептов."""

    recipe: models.ForeignKey = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт')
    ingredient: models.ForeignKey = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент')
    amount: models.PositiveSmallIntegerField = (
        models.PositiveSmallIntegerField(
            validators=[
                MinValueValidator(INGREDIENT_MIN_AMOUNT),
            ],
            verbose_name='Количество',
        )
    )

    class Meta:
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецептах'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient',],
                name='unique_ingredient_in_recipe'
            )
        ]

    def __str__(self):
        return f'{self.ingredient.name} в {self.recipe.name}'
