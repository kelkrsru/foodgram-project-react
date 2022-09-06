from django_filters.rest_framework import FilterSet, filters
from recipes.models import Recipe, Tag
from rest_framework.filters import SearchFilter


class IngredientSearchFilter(SearchFilter):
    """Filter for Ingredient. Search field name."""
    search_param = 'name'


class RecipeFilters(FilterSet):
    """Filters for Recipes. Filters include tags, is_favorited,
    is_in_shopping_cart, author."""
    tags = filters.AllValuesMultipleFilter(field_name='tags__slug')
    is_favorited = filters.BooleanFilter(method='get_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        method='get_is_in_shopping_cart')

    class Meta:
        model = Recipe
        fields = ('tags', 'author', 'is_favorited', 'is_in_shopping_cart')

    def get_is_favorited(self, queryset, name, value):
        if value:
            return queryset.filter(favorite=self.request.user.id)
        return queryset

    def get_is_in_shopping_cart(self, queryset, name, value):
        if value:
            return queryset.filter(cart=self.request.user.id)
        return queryset
