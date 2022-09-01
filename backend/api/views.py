from django.db.models import F, Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from api.filters import IngredientSearchFilter, RecipeFilters
from api.permissions import AdminOrReadOnly, AuthorOrReadOnly
from api.serializers import (IngredientSerializer, RecipeSerializer,
                             TagSerializer)
from recipes.models import Ingredient, IngredientAmount, Recipe, Tag
from users.models import User
from users.paginators import PageLimitPagination
from users.serializers import ShortRecipeSerializer


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for model Tag."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AdminOrReadOnly,)
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for model Ingredient."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AdminOrReadOnly,)
    pagination_class = None
    filter_backends = (IngredientSearchFilter,)
    search_fields = ('^name',)


class RecipeViewSet(viewsets.ModelViewSet):
    """ViewSet for model Recipe."""
    queryset = Recipe.objects.select_related('author')
    serializer_class = RecipeSerializer
    permission_classes = (AuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilters
    pagination_class = PageLimitPagination
    http_method_names = ['get', 'post', 'patch', 'delete']

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[permissions.IsAuthenticated],
            serializer_class=ShortRecipeSerializer)
    def favorite(self, request, pk):
        user = request.user
        recipe_id = int(pk)
        recipe = get_object_or_404(Recipe, pk=recipe_id)
        if request.method == 'POST':
            if User.objects.filter(favorites=recipe_id).exists():
                return Response(
                    {'errors': 'Этот рецепт уже в избранном.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            user.favorites.add(recipe)
            serializer = self.get_serializer(recipe, context={
                'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        elif request.method == 'DELETE':
            if User.objects.filter(favorites=recipe_id).exists():
                user.favorites.remove(recipe)
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response({'errors': 'Этого рецепта нет в избранном.'},
                            status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[permissions.IsAuthenticated],
            serializer_class=ShortRecipeSerializer)
    def shopping_cart(self, request, pk):
        user = request.user
        recipe_id = int(pk)
        recipe = get_object_or_404(Recipe, pk=recipe_id)
        if request.method == 'POST':
            if User.objects.filter(user_cart=recipe_id).exists():
                return Response(
                    {'errors': 'Этот рецепт уже в списке покупок.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            user.user_cart.add(recipe)
            serializer = self.get_serializer(recipe, context={
                'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        elif request.method == 'DELETE':
            if User.objects.filter(user_cart=recipe_id).exists():
                user.user_cart.remove(recipe)
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response({'errors': 'Этого рецепта нет в списке покупок.'},
                            status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @action(detail=False, methods=['get'],
            permission_classes=[permissions.IsAuthenticated])
    def download_shopping_cart(self, request):
        user = self.request.user
        if not user.user_cart.exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        ingredients = IngredientAmount.objects.filter(
            recipe__in=(user.user_cart.values('id'))
        ).values(
            ingredient_name=F('ingredient__name'),
            measure=F('ingredient__measurement_unit')
        ).annotate(amount=Sum('amount'))

        filename = f'{user.username}_shopping_list.txt'
        shopping_list = (
            f'Список покупок пользователя: {user.get_full_name()}\n\n'
        )
        for ingredient in ingredients:
            shopping_list += (
                f'{ingredient["ingredient_name"]}: {ingredient["amount"]} '
                f'{ingredient["measure"]}\n'
            )

        shopping_list += '\nСформировано с помощью Продуктового помощника'

        response = HttpResponse(
            shopping_list, content_type='text.txt; charset=utf-8'
        )
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response
