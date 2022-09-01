from django.contrib import admin
from django.utils.safestring import mark_safe

from .models import Ingredient, IngredientAmount, Recipe, Tag


class IngredientAmountInline(admin.TabularInline):
    model = IngredientAmount
    extra = 2


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'get_image', 'amount_favorites')
    raw_id_fields = ('author', 'tags',)
    search_fields = ('name', 'author',)
    list_filter = ('name', 'author__username', 'tags')
    exclude = ('cart', 'favorite')
    inlines = (IngredientAmountInline,)

    @staticmethod
    def get_image(obj):
        return mark_safe(f'<img src={obj.image.url} width="80" height="30"')

    @staticmethod
    def amount_favorites(obj):
        return obj.favorite.count()

    get_image.short_description = 'Изображение'
    amount_favorites.short_description = 'В избранном'


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit',)
    search_fields = ('name',)
    list_filter = ('name',)


class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'slug',)
    search_fields = ('name', 'color')


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Ingredient, IngredientAdmin)
