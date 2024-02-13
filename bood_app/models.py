from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from bood_account.models import Person
from bood_app.utils.cache import delete_model_cache_for_current_user
from bood_app.utils.resources import GENDER_TYPE, TARGET_TYPE, ACTIVITY_TYPE


class PersonCard(models.Model):
    height = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(100), MaxValueValidator(250)], verbose_name="Рост"
    )
    age = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(18), MaxValueValidator(100)], verbose_name="Возраст"
    )
    gender = models.CharField(max_length=6, choices=GENDER_TYPE, verbose_name="Пол")
    target = models.CharField(blank=True, default="", max_length=4, choices=TARGET_TYPE, verbose_name="Цель")
    activity = models.CharField(max_length=5, choices=ACTIVITY_TYPE, verbose_name="Активность")
    image = models.URLField(blank=True, default="", verbose_name="Фото")
    person = models.OneToOneField(Person, on_delete=models.CASCADE, verbose_name="Пользователь")
    femaletype = models.ManyToManyField("FemaleType", related_name="personcard", blank=True, verbose_name="Тип женщины")
    exclude_products = models.ManyToManyField(
        "Product", related_name="personcard", blank=True, verbose_name="Исключенные продукты"
    )
    exclude_category = models.ManyToManyField(
        "ProductCategory",
        related_name="personcard",
        blank=True,
        verbose_name="Исключенные категории продуктов",
    )

    class Meta:
        verbose_name = "Карточка пользователя"
        verbose_name_plural = "Карточки пользователей"

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        delete_model_cache_for_current_user("person_card", self.person.id)
        delete_model_cache_for_current_user("calculate_standard", self.person.id)
        delete_model_cache_for_current_user("calculate_current", self.person.id)
        return super().save()

    def __str__(self) -> str:
        return str(self.person.email)


class FemaleType(models.Model):
    title = models.CharField(max_length=255, unique=True, verbose_name="Название")

    class Meta:
        verbose_name = "Тип женщины"
        verbose_name_plural = "Типы женщины"

    def __str__(self) -> str:
        return str(self.title)


class Measurement(models.Model):
    weight = models.FloatField(validators=[MinValueValidator(15.0), MaxValueValidator(350.0)], verbose_name="Вес")
    chest = models.FloatField(
        validators=[MinValueValidator(30.0), MaxValueValidator(300.0)], verbose_name="Объем груди"
    )
    waist = models.FloatField(
        validators=[MinValueValidator(30.0), MaxValueValidator(300.0)], verbose_name="Объем талии"
    )
    hips = models.FloatField(validators=[MinValueValidator(30.0), MaxValueValidator(300.0)], verbose_name="Объем бедер")
    hand = models.FloatField(validators=[MinValueValidator(10.0), MaxValueValidator(30.0)], verbose_name="Объем кисти")
    datetime_add = models.DateTimeField(auto_now_add=True, verbose_name="Дата и время замера")
    person_card = models.ForeignKey(
        "PersonCard", on_delete=models.CASCADE, related_name="measurements", verbose_name="Карточка пользователя"
    )

    class Meta:
        verbose_name = "Замер"
        verbose_name_plural = "Замеры"

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        delete_model_cache_for_current_user("measurement", self.person_card.person.id)
        delete_model_cache_for_current_user("calculate_standard", self.person_card.person.id)
        delete_model_cache_for_current_user("calculate_current", self.person_card.person.id)
        return super().save()

    def __str__(self) -> str:
        return str(self.person_card.person.email)


class Product(models.Model):
    title = models.CharField(max_length=255, unique=True, db_index=True, verbose_name="Название")
    proteins = models.FloatField(
        null=True, blank=True, default=0.0, validators=[MinValueValidator(0.0)], verbose_name="Белки"
    )
    fats = models.FloatField(
        null=True, blank=True, default=0.0, validators=[MinValueValidator(0.0)], verbose_name="Жиры"
    )
    carbohydrates = models.FloatField(
        null=True, blank=True, default=0.0, validators=[MinValueValidator(0.0)], verbose_name="Углеводы"
    )
    calories = models.FloatField(
        null=True, blank=True, default=0.0, validators=[MinValueValidator(0.0)], verbose_name="Калории"
    )
    water = models.FloatField(
        null=True, blank=True, default=0.0, validators=[MinValueValidator(0.0)], verbose_name="Вода"
    )
    proteins_proportion = models.FloatField(
        null=True, blank=True, default=0.0, db_index=True, validators=[MinValueValidator(0.0)], verbose_name="Б"
    )
    fats_proportion = models.FloatField(
        null=True, blank=True, default=0.0, db_index=True, validators=[MinValueValidator(0.0)], verbose_name="Ж"
    )
    carbohydrates_proportion = models.FloatField(
        null=True, blank=True, default=0.0, db_index=True, validators=[MinValueValidator(0.0)], verbose_name="У"
    )
    category = models.ForeignKey(
        "ProductCategory",
        on_delete=models.PROTECT,
        related_name="product",
        verbose_name="Категория",
        null=True,
        blank=True,
        db_index=True,
    )
    vitamins = models.OneToOneField(
        "Vitamin", on_delete=models.CASCADE, null=True, related_name="product", verbose_name="Витамины"
    )
    microelements = models.OneToOneField(
        "MicroElement", on_delete=models.CASCADE, null=True, related_name="product", verbose_name="Микроэлементы"
    )

    class Meta:
        verbose_name = "Продукт"
        verbose_name_plural = "Продукты"

    def __str__(self) -> str:
        return str(self.title)


class Vitamin(models.Model):
    a = models.FloatField(
        null=True, blank=True, default=0.0, validators=[MinValueValidator(0.0)], verbose_name="Витамин А"
    )
    b1 = models.FloatField(
        null=True, blank=True, default=0.0, validators=[MinValueValidator(0.0)], verbose_name="Витамин В1"
    )
    b2 = models.FloatField(
        null=True, blank=True, default=0.0, validators=[MinValueValidator(0.0)], verbose_name="Витамин В2"
    )
    b3 = models.FloatField(
        null=True, blank=True, default=0.0, validators=[MinValueValidator(0.0)], verbose_name="Витамин В3"
    )
    e = models.FloatField(
        null=True, blank=True, default=0.0, validators=[MinValueValidator(0.0)], verbose_name="Витамин Е"
    )
    c = models.FloatField(
        null=True, blank=True, default=0.0, validators=[MinValueValidator(0.0)], verbose_name="Витамин С"
    )

    class Meta:
        verbose_name = "Витамин"
        verbose_name_plural = "Витамины"

    def __str__(self) -> str:
        return f"Витамины для: {self.product.title}"


class MicroElement(models.Model):
    iron = models.FloatField(
        null=True, blank=True, default=0.0, validators=[MinValueValidator(0.0)], verbose_name="Железо"
    )
    calcium = models.FloatField(
        null=True, blank=True, default=0.0, validators=[MinValueValidator(0.0)], verbose_name="Кальций"
    )
    sodium = models.FloatField(
        null=True, blank=True, default=0.0, validators=[MinValueValidator(0.0)], verbose_name="Натрий"
    )
    potassium = models.FloatField(
        null=True, blank=True, default=0.0, validators=[MinValueValidator(0.0)], verbose_name="Калий"
    )
    phosphorus = models.FloatField(
        null=True, blank=True, default=0.0, validators=[MinValueValidator(0.0)], verbose_name="Фосфор"
    )

    class Meta:
        verbose_name = "Микроэлемент"
        verbose_name_plural = "Микроэлементы"

    def __str__(self) -> str:
        return f"Микроэлементы для: {self.product.title}"


class ProductCategory(models.Model):
    title = models.CharField(max_length=255, unique=True, db_index=True, verbose_name="Название")
    description = models.TextField(blank=True, default="", verbose_name="Описание")
    image = models.URLField(blank=True, default="", verbose_name="Изображение")

    class Meta:
        verbose_name = "Категория продуктов"
        verbose_name_plural = "Категории продуктов"

    def __str__(self) -> str:
        return str(self.title)


class Eating(models.Model):
    datetime_add = models.DateTimeField(auto_now_add=True, verbose_name="Дата и время")
    product_weight = models.OneToOneField(
        "ProductWeight",
        on_delete=models.CASCADE,
        related_name="eating",
        null=True,
        blank=True,
        verbose_name="Продукт с весом",
    )
    recipe = models.ForeignKey(
        "Recipe", on_delete=models.CASCADE, related_name="eating", null=True, blank=True, verbose_name="Рецепт"
    )
    water = models.OneToOneField(
        "Water", on_delete=models.CASCADE, related_name="eating", null=True, blank=True, verbose_name="Вода"
    )
    person_card = models.ForeignKey(
        "PersonCard", on_delete=models.CASCADE, related_name="eating", verbose_name="Карточка пользователя"
    )

    class Meta:
        verbose_name = "Прием пищи"
        verbose_name_plural = "Приемы пищи"

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        delete_model_cache_for_current_user("eating", self.person_card.person.id)
        return super().save()

    def __str__(self) -> str:
        return str(self.person_card.person.email)


class FAQ(models.Model):
    question = models.CharField(max_length=255, verbose_name="Вопрос")
    answer = models.TextField(verbose_name="Ответ")

    class Meta:
        verbose_name = "FAQ"
        verbose_name_plural = "FAQ"

    def __str__(self) -> str:
        return str(self.question)


class ProductWeight(models.Model):
    weight = models.PositiveSmallIntegerField(validators=[MinValueValidator(1)], verbose_name="Вес")
    product = models.ForeignKey(
        "Product", on_delete=models.CASCADE, related_name="product_weight", verbose_name="Продукт"
    )
    recipe = models.ForeignKey(
        "Recipe", on_delete=models.CASCADE, related_name="product_weight", null=True, blank=True, verbose_name="Рецепт"
    )

    class Meta:
        verbose_name = "Продукт с весом"
        verbose_name_plural = "Продукты с весом"

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        eating = Eating.objects.filter(product_weight=self.id).first()
        if eating:
            delete_model_cache_for_current_user("eating", eating.person_card.person.id)
        if self.recipe:
            delete_model_cache_for_current_user("recipe", self.recipe.person_card.person.id)
        return super().save()

    def __str__(self) -> str:
        return str(self.product.title)


class Recipe(models.Model):
    title = models.CharField(max_length=255, db_index=True, verbose_name="Название")
    description = models.TextField(blank=True, default="", verbose_name="Описание")
    person_card = models.ForeignKey(
        "PersonCard", on_delete=models.CASCADE, related_name="recipe", verbose_name="Карточка пользователя"
    )
    image = models.URLField(blank=True, default="", verbose_name="Изображение")
    is_active = models.BooleanField(default=True, verbose_name="Активен")

    class Meta:
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        delete_model_cache_for_current_user("recipe", self.person_card.person.id)
        return super().save()

    def __str__(self) -> str:
        return str(self.title)


class Water(models.Model):
    weight = models.PositiveSmallIntegerField(validators=[MinValueValidator(1)], verbose_name="Объем")

    class Meta:
        verbose_name = "Вода"
        verbose_name_plural = "Вода"

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        eating = Eating.objects.filter(water=self.id).first()
        if eating:
            delete_model_cache_for_current_user("eating", eating.person_card.person.id)
        return super().save()

    def __str__(self) -> str:
        return str(self.weight)
