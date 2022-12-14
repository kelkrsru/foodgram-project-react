from drf_extra_fields.fields import Base64ImageField
from recipes.models import Ingredient, IngredientAmount, Recipe, Tag
from rest_framework import serializers
from users.serializers import UserSerializer


class TagSerializer(serializers.ModelSerializer):
    """Serializer for model Tag."""
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')
        read_only_fields = '__all__',


class IngredientSerializer(serializers.ModelSerializer):
    """Serializer for model Ingredient."""
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')
        read_only_fields = '__all__',


class IngredientAmountSerializer(serializers.ModelSerializer):
    """Serializer for model IngredientAmount. """
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientAmount
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    """Serializer for model Recipe."""
    tags = TagSerializer(many=True, read_only=True)
    author = UserSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    @staticmethod
    def get_ingredients(obj):
        queryset = IngredientAmount.objects.filter(recipe=obj)
        return IngredientAmountSerializer(queryset, many=True).data

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return user.favorites.filter(id=obj.id).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return user.user_cart.filter(id=obj.id).exists()

    def validate(self, data):
        name = str(self.initial_data.get('name')).strip()
        tags = self.initial_data.get('tags')
        ingredients = self.initial_data.get('ingredients')
        author = self.context.get('request').user

        if not tags:
            raise serializers.ValidationError({
                'tags': '?????????? ?????????????? ???????? ???? ???????? ??????.'
            })
        tags_list = []
        for tag in tags:
            if tag in tags_list:
                raise serializers.ValidationError({
                    'tags': '???????? ???????????? ???????? ??????????????????????.'
                })
            tags_list.append(tag)

        valid_ingredients = []
        for ingredient in ingredients:
            amount = ingredient.get('amount')
            if int(amount) <= 0:
                raise serializers.ValidationError({
                    'amount': '?????????????? ???????????????????? ?????????????????????? ???????????? 0.'
                })
            valid_ingredients.append(
                {'id': ingredient.get('id'), 'amount': amount}
            )

        data['name'] = name.capitalize()
        data['tags'] = tags
        data['ingredients'] = valid_ingredients
        data['author'] = author
        return data
