from io import BytesIO
from django.db.models import Sum
from django.http import FileResponse
from recipes.models import IngredientInRecipe


def get_ingredients_list(user):
    return (
        IngredientInRecipe.objects
        .filter(recipe__shopping_carts__user=user)
        .values('ingredient__name', 'ingredient__measurement_unit')
        .annotate(total_amount=Sum('amount'))
        .order_by('ingredient__name')
    )


def create_shop_list_text(ingredients):
    return '\n'.join(
        f'{item["ingredient__name"]} —> '
        f'{item["total_amount"]} '
        f'{item["ingredient__measurement_unit"]}'
        for item in ingredients
    )


def create_shop_list_file(user):
    ingredients = get_ingredients_list(user)
    content = create_shop_list_text(ingredients)

    buffer = BytesIO()
    buffer.write(content.encode('utf-8'))
    buffer.seek(0)

    return FileResponse(
        buffer,
        as_attachment=True,
        filename='shopping_list.txt',
        content_type='text/plain'
    )
