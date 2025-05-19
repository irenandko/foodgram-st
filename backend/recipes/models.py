from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from foodgram.constants import (PRODUCT_NAME_MAX_LENGTH,
                                MEASUREMENT_MAX_LENGTH,
                                RECIPE_MIN_TIME,
                                RECIPE_MAX_NAME_LENGTH,
                                INGREDIENT_MIN_AMOUNT)


class Ingredient(models.Model):
    """Модель для ингридиента."""

    name: models.CharField = models.CharField(
        max_length=PRODUCT_NAME_MAX_LENGTH,
        verbose_name="Название ингредиента")
    measurement: models.CharField = models.CharField(
        max_length=MEASUREMENT_MAX_LENGTH,
        verbose_name="Единицы измерения")

    class Meta:
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"
        ordering = ['name']
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='unique_ingredient'
            )
        ]

    def __str__(self):
        return f'{self.name}, {self.measurement}'


class Recipe(models.Model):
    """Модель рецепта."""

    author: models.ForeignKey = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name="Автор"
    )
    image = models.ImageField(
        upload_to='recipes/images/',
        verbose_name="Фото рецепта")
    name: models.CharField = models.CharField(
        max_length=RECIPE_MAX_NAME_LENGTH,
        verbose_name="Название блюда")
    description: models.TextField = models.TextField(
        verbose_name="Описание рецепта")
    cooking_time: models.PositiveSmallIntegerField = (
        models.PositiveSmallIntegerField(
            verbose_name="Время приготовления",
            validators=[
                MinValueValidator(RECIPE_MIN_TIME),
            ],
        )
    )
    ingredients: models.ManyToManyField = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        related_name='recipes'
    )
    pub_date: models.DateTimeField = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата публикации")

    class Meta:
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"
        ordering = ['-pub_date']
        default_related_name = 'recipes'

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    """Модель ингридента в рецепте."""

    recipe: models.ForeignKey = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name="Рецепт")
    ingredient: models.ForeignKey = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name="Ингредиент")
    amount: models.PositiveSmallIntegerField = (
        models.PositiveSmallIntegerField(
            verbose_name="Количество",
            validators=[
                MinValueValidator(INGREDIENT_MIN_AMOUNT),
            ],
        )
    )

    class Meta:
        verbose_name = "Ингредиент в рецепте"
        verbose_name_plural = "Ингредиенты в рецептах"
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_ingredient_in_recipe'
            )
        ]

    def __str__(self):
        return f'{self.ingredient.name} в {self.recipe.name}'


class UserRecipeRelations(models.Model):
    """Модель соотношения пользователя и рецепта."""

    user: models.ForeignKey = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Пользователь"
    )
    recipe: models.ForeignKey = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name="Рецепт"
    )

    class Meta:
        abstract = True
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='%(class)s_unique')
        ]

    def __str__(self):
        return f'{self.user} - {self.recipe}'


class ShoppingBasket(UserRecipeRelations):
    """Модель для корзины покупок."""

    class Meta(UserRecipeRelations.Meta):
        verbose_name = "Список покупок"
        verbose_name_plural = "Списки покупок"
        default_related_name = 'shopping_basket'


class Favorites(UserRecipeRelations):
    """Модель избранных рецептов."""

    class Meta(UserRecipeRelations.Meta):
        verbose_name = "Избранное"
        verbose_name_plural = "Избранное"
        default_related_name = "favorites"
