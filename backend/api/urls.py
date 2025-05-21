from django.urls import include, path
from rest_framework import routers

from users.views import CustomUserViewSet
from recipes.views import RecipeViewSet, IngredientViewSet

router = routers.DefaultRouter()

router.register("recipes", RecipeViewSet, basename="recipes")
router.register("ingredients", IngredientViewSet, basename="ingredients")
router.register("users", CustomUserViewSet, basename="users")

urlpatterns = [
    path("", include(router.urls)),
    path("auth/", include("djoser.urls.authtoken")),
]
