from django.contrib import admin
from .models import (
    Product,
    Measurement,
    PersonCard,
    Vitamin,
    MicroElement,
    ProductWeight,
    Recipe,
    Eating,
    FemaleType,
    ProductCategory,
    Water,
    FAQ,
)


class ProductAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "proteins", "fats", "carbohydrates", "calories", "water", "category")
    list_display_links = ("title",)
    search_fields = (
        "title",
        "id",
    )
    list_filter = ("category",)
    list_per_page = 20
    ordering = ["title"]
    fieldsets = [
        ("Основная информация", {"fields": ["title"]}),
        ("Пищевая ценность", {"fields": ["proteins", "fats", "carbohydrates", "calories", "water"]}),
        ("Микроэлементы и Витамины", {"fields": ["microelements", "vitamins"]}),
        ("Пропорции", {"fields": ["proteins_proportion", "fats_proportion", "carbohydrates_proportion"]}),
        ("Категория рекомендаций", {"fields": ["category"]}),
    ]
    readonly_fields = (
        "id",
        "title",
        "proteins",
        "fats",
        "carbohydrates",
        "calories",
        "water",
        "microelements",
        "vitamins",
        "proteins_proportion",
        "fats_proportion",
        "carbohydrates_proportion",
    )


class VitaminAdmin(admin.ModelAdmin):
    list_per_page = 20
    readonly_fields = (
        "id",
        "a",
        "b1",
        "b2",
        "b3",
        "e",
        "c",
    )


class MicroElementAdmin(admin.ModelAdmin):
    list_per_page = 20
    readonly_fields = (
        "id",
        "iron",
        "calcium",
        "sodium",
        "potassium",
        "phosphorus",
    )


class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "description", "image")
    list_display_links = ("title",)
    list_per_page = 20


class PersonCardAdmin(admin.ModelAdmin):
    list_display = ("id", "person", "person_id", "height", "age", "gender", "target", "activity")
    list_display_links = ("person",)
    list_per_page = 20


class MeasurementAdmin(admin.ModelAdmin):
    list_display = ("id", "person_card", "weight", "chest", "waist", "hips", "hand", "datetime_add")
    list_filter = ("datetime_add",)
    search_fields = ("person_card__person__email",)
    list_per_page = 20


class EatingAdmin(admin.ModelAdmin):
    list_display = ("id", "datetime_add", "product_weight", "recipe", "water", "person_card", "get_weight")
    list_filter = ("datetime_add",)
    search_fields = ("person_card__person__email",)
    list_display_links = ("datetime_add",)
    list_per_page = 20

    def get_weight(self, obj):
        if obj.product_weight:
            return obj.product_weight.weight
        if obj.recipe:
            return sum(ProductWeight.objects.filter(recipe=obj.recipe).values_list("weight", flat=True))
        if obj.water:
            return obj.water.weight

    get_weight.short_description = "Weight"


class ProductWeightInline(admin.TabularInline):
    model = ProductWeight
    extra = 1


class RecipeAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "description", "person_card", "is_active")
    list_display_links = ("title",)
    inlines = [ProductWeightInline]
    list_per_page = 20


admin.site.register(Vitamin, VitaminAdmin)
admin.site.register(MicroElement, MicroElementAdmin)
admin.site.register(ProductWeight)
admin.site.register(Water)
admin.site.register(Eating, EatingAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(ProductCategory, ProductCategoryAdmin)
admin.site.register(Measurement, MeasurementAdmin)
admin.site.register(PersonCard, PersonCardAdmin)
admin.site.register(FemaleType)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(FAQ)
