from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse
from api.permissions import IsAuthorOrReadOnly

from recipes.filters import RecipeFilter
from recipes.serializers import (RecipeReadSerializer,
                                 RecipeWriteSerializer,
                                 IngredientSerializer,
                                 FavoriteSerializer,
                                 ShoppingCartSerializer)
from recipes.models import (Recipe,
                            Ingredient,
                            Favorite,
                            ShoppingCart)
from recipes.utils import create_shop_list_file


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None

    def get_queryset(self):
        name = self.request.query_params.get('name')
        if name:
            return self.queryset.filter(name__istartswith=name)
        return self.queryset


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = [IsAuthorOrReadOnly]
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return RecipeWriteSerializer
        return RecipeReadSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def _add_to(self, request, pk, serializer_class):
        recipe = get_object_or_404(Recipe, pk=pk)
        serializer = serializer_class(
            data={'user': request.user.id,
                  'recipe': recipe.id},
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data,
                        status=status.HTTP_201_CREATED)

    def _remove_from(self, request, pk, model):
        recipe = get_object_or_404(Recipe, pk=pk)
        deleted_count, _ = model.objects.filter(user=request.user,
                                                recipe=recipe).delete()
        if deleted_count <= 0:
            return Response({'errors': 'Рецепт не найден.'},
                            status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['get'],
            permission_classes=[IsAuthenticated],
            detail=False,)
    def download_shopping_cart(self, request):
        return create_shop_list_file(request.user)

    @action(methods=['get'],
            url_path='get-link',
            detail=True,)
    def get_short_link(self, request, pk=None):
        path = reverse('recipes:recipe_short_link', kwargs={'pk': pk})
        url = request.build_absolute_uri(path)
        return Response(data={"short-link": url})

    @action(methods=['post'],
            detail=True,
            url_path='favorite')
    def add_favorite(self, request, pk):
        return self._add_to(request, pk, FavoriteSerializer)

    @action(methods=['post'],
            detail=True,
            url_path='shopping_cart')
    def add_shopping_cart(self, request, pk):
        return self._add_to(request, pk, ShoppingCartSerializer)
   
    @add_favorite.mapping.delete
    def delete_favorite(self, request, pk):
        return self._remove_from(request, pk, Favorite)

    @add_shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, pk):
        return self._remove_from(request, pk, ShoppingCart)


def redirect_short_link(request, pk):
    get_object_or_404(Recipe, id=pk)
    return redirect(f'/recipes/{pk}/')
