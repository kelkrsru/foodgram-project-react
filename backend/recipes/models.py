from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from users.models import User


class CreatedChangedModel(models.Model):
    """Abstract model. Adds the date, time of creation and modification."""
    created = models.DateTimeField(
        verbose_name='Дата и время создания',
        help_text='Автоматически задается при создании',
        auto_now_add=True,
    )
    changed = models.DateTimeField(
        verbose_name='Дата и время изменения',
        help_text='Автоматически задается при каждом изменении',
        auto_now=True,
    )

    class Meta:
        abstract = True


class Ingredient(CreatedChangedModel):
    """Model Ingredient."""
    name = models.CharField(
        verbose_name='Ингредиент',
        help_text='Наименование ингредиента',
        max_length=200
    )
    measurement_unit = models.CharField(
        verbose_name='Единица измерения',
        help_text='Единица измерения ингредиента',
        max_length=200
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ['name']
        unique_together = ['name', 'measurement_unit']


class Tag(CreatedChangedModel):
    """Model Tag."""
    name = models.CharField(
        verbose_name='Тег',
        help_text='Наименование тега',
        max_length=200,
        unique=True
    )
    color = models.CharField(
        verbose_name='Цвет',
        help_text='Цвет тега в HEX-формате (напр. #000000 - Черный)',
        max_length=7,
        null=True,
        default=None
    )
    slug = models.SlugField(
        verbose_name='Адрес',
        help_text='Уникальный адрес тега',
        max_length=200,
        unique=True,
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ['name']


class Recipe(CreatedChangedModel):
    """Model Recipe."""
    name = models.CharField(
        verbose_name='Рецепт',
        help_text='Наименование рецепта',
        max_length=200,
    )
    text = models.TextField(
        verbose_name='Описание',
        help_text='Описание рецепта',
    )
    image = models.ImageField(
        verbose_name='Изображение',
        upload_to='recipes/',
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления',
        help_text='Время приготовления рецепта в минутах',
        validators=(
            MinValueValidator(1, 'Время приготовления не может быть меньше'
                                 'минуты'),
            MaxValueValidator(1440, 'Время приготовления не может быть больше'
                                    '24 часов')
        ),
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        help_text='Автор рецепта',
        related_name='recipes',
        on_delete=models.CASCADE
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Теги',
        help_text='Список тегов рецепта',
        related_name='recipes',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='Ингредиенты',
        help_text='Список ингредиентов рецепта',
        related_name='recipes',
        through='IngredientAmount',
    )
    favorite = models.ManyToManyField(
        User,
        verbose_name='Избранное',
        help_text='Список пользователей, у кого рецепт в избранном',
        related_name='favorites',
    )
    cart = models.ManyToManyField(
        User,
        verbose_name='Список покупок',
        help_text='Список пользователей, у кого рецепт в списке покупок',
        related_name='user_cart',
    )

    def __str__(self):
        return f'{self.name} от автора {self.author.get_full_name()}'

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ['-created']
        unique_together = ['name', 'author']


class IngredientAmount(models.Model):
    """Model for linking recipes and ingredients with quantities."""
    ingredient = models.ForeignKey(
        Ingredient,
        verbose_name='Ингредиент',
        on_delete=models.PROTECT,
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        on_delete=models.CASCADE,
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество',
        help_text='Количество ингредиента в рецепте',
        validators=(
            MinValueValidator(1, 'В рецепте должен быть хотя бы 1 ингредиент'),
            MaxValueValidator(5000, 'В рецепте не может быть более 5000 '
                                    'ингредиентов')
        ),
    )

    def __str__(self):
        return (f'Ингредиент {self.ingredient.name} '
                f'в рецепте {self.recipe.name}')

    class Meta:
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецепте'
        ordering = ['recipe']
        unique_together = ['ingredient', 'recipe']
