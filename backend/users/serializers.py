from recipes.models import Recipe
from rest_framework import serializers
from users.models import User


class ShortRecipeSerializer(serializers.ModelSerializer):
    """Serializer for model Recipe and short view."""
    class Meta:
        model = Recipe
        fields = 'id', 'name', 'image', 'cooking_time'
        read_only_fields = '__all__',


class UserSerializer(serializers.ModelSerializer):
    """Serializer for model User."""
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'password',
        )
        extra_kwargs = {'password': {'write_only': True}}

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous or (user == obj):
            return False
        return user.subscribe.filter(id=obj.id).exists()


class PasswordSerializer(serializers.ModelSerializer):
    """Serializer for password change endpoint."""
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True)

    class Meta:
        model = User
        fields = ('old_password', 'new_password')

    def validate(self, data):
        old_password = self.initial_data.get('old_password')
        new_password = self.initial_data.get('new_password')
        user = self.context.get('request').user

        if not user.check_password(old_password):
            raise serializers.ValidationError(
                {"old_password": ["Неверно указан старый пароль."]})
        if old_password == new_password:
            raise serializers.ValidationError(
                {"new_password": ["Новый пароль совпадает со старым."]})
        return data


class UserSubscribeSerializer(UserSerializer):
    """Serializer for user ."""
    recipes = ShortRecipeSerializer(many=True, read_only=True)
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
        )
        read_only_fields = '__all__',

    def get_recipes(self, obj):
        request = self.context.get('request')
        recipes = obj.recipes.all()
        recipes_limit = request.query_params.get('recipes_limit')
        if recipes_limit:
            recipes = recipes[:int(recipes_limit)]
        return ShortRecipeSerializer(recipes, many=True).data

    @staticmethod
    def get_recipes_count(obj):
        return obj.recipes.count()
