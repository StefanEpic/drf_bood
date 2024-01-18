from datetime import datetime

from django.utils import timezone
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from bood_account.models import Person
from bood_account.serializers import PersonCreateSerializer
from .models import (
    Product,
    PersonCard,
    Eating,
    ProductWeight,
    Measurement,
    Recipe,
    Water,
    FemaleType,
    ProductCategory,
    FAQ,
)
from .services.kbjy import KBJYService, RecommendationService
from .utils.eating_validation import eating_validation
from .utils.person_card_validation import get_person_card


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ("id", "title", "proteins", "fats", "carbohydrates", "calories", "water")
        read_only_fields = ("id", "title", "proteins", "fats", "carbohydrates", "calories", "water")


class ProductCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCategory
        fields = ("id", "title", "description", "image")
        read_only_fields = ("id", "title", "description", "image")


class ProductSerializerWithCategory(serializers.ModelSerializer):
    category = ProductCategorySerializer()

    class Meta:
        model = Product
        fields = ("id", "title", "proteins", "fats", "carbohydrates", "calories", "water", "category")
        read_only_fields = ("id", "title", "proteins", "fats", "carbohydrates", "calories", "water", "category")


class FAQSerializer(serializers.ModelSerializer):
    class Meta:
        model = FAQ
        fields = ("id", "question", "answer")
        read_only_fields = ("id", "question", "answer")


class MeasurementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Measurement
        fields = ("id", "weight", "chest", "waist", "hips", "hand", "datetime_add", "person_card")
        read_only_fields = ("id", "datetime_add", "person_card")

    def create(self, validated_data):
        user_id = self.context["user_id"]
        person_card = get_person_card(user_id)
        measurement = Measurement.objects.create(person_card=person_card, **validated_data)
        return measurement


class FemaleTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = FemaleType
        fields = ("id", "title")
        read_only_fields = ("id", "title")


class PostPersonCardSerializer(serializers.ModelSerializer):
    measurements = MeasurementSerializer(read_only=True, many=True)

    class Meta:
        model = PersonCard
        fields = (
            "id",
            "height",
            "age",
            "gender",
            "target",
            "activity",
            "image",
            "person",
            "femaletype",
            "exclude_products",
            "exclude_category",
            "measurements",
        )
        read_only_fields = ("id", "person", "measurements")

    def create(self, validated_data) -> dict:
        height = validated_data.pop("height")
        age = validated_data.pop("age")
        gender = validated_data.pop("gender")
        target = validated_data.pop("target", "")
        activity = validated_data.pop("activity")
        image = validated_data.pop("image", "")
        femaletype = validated_data.pop("femaletype", None)
        exclude_products = validated_data.pop("exclude_products", None)
        exclude_category = validated_data.pop("exclude_category", None)
        user_id = self.context["user_id"]
        person = Person.objects.get(id=user_id)

        person_card = PersonCard.objects.filter(person__id=user_id).first()
        if person_card is not None:
            raise ValidationError({"status": "400", "error": "You already have person card"})

        person_card = PersonCard.objects.create(
            person=person,
            height=height,
            age=age,
            gender=gender,
            target=target,
            activity=activity,
            image=image,
        )

        if femaletype:
            if gender == 'male':
                raise ValidationError({"status": "400", "error": "Male gender can't have female type"})
            person_card.femaletype.set(femaletype)
        if exclude_products:
            person_card.exclude_products.set(exclude_products)
        if exclude_category:
            person_card.exclude_category.set(exclude_category)

        person_card.save()
        return person_card


class GetPersonCardSerializer(PostPersonCardSerializer):
    femaletype = FemaleTypeSerializer(many=True)
    exclude_products = ProductSerializer(many=True)
    exclude_category = ProductCategorySerializer(many=True)
    person = PersonCreateSerializer()


class ProductWeightSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductWeight
        fields = ("product", "weight")


class ProductWeightDetailSerializer(serializers.ModelSerializer):
    product = ProductSerializer()

    class Meta:
        model = ProductWeight
        fields = ("product", "weight")
        read_only_fields = ("product", "weight")


class PostRecipeSerializer(serializers.ModelSerializer):
    product_weight = ProductWeightSerializer(many=True)

    class Meta:
        model = Recipe
        fields = ("id", "title", "description", "person_card", "image", "is_active", "product_weight")
        read_only_fields = ("id", "person_card", "is_active")

    def create(self, validated_data):
        product_weight = validated_data.pop("product_weight")
        if not product_weight:
            raise serializers.ValidationError({"status": "400", "error": "Product not found"})

        user_id = self.context["user_id"]
        person_card = get_person_card(user_id)
        recipe = Recipe.objects.create(person_card=person_card, **validated_data)
        recipe.save()

        for product in product_weight:
            added_products = ProductWeight.objects.filter(recipe=recipe)
            if added_products and product["product"].pk in [name.product.pk for name in added_products]:
                for added_product in added_products:
                    if added_product.product.pk == product["product"].pk:
                        added_product.weight += product["weight"]
                        added_product.save()
                        break
                continue
            ProductWeight.objects.create(recipe=recipe, **product)
        return recipe

    def update(self, instance, validated_data):
        instance.is_active = False
        instance.save()
        instance.pk = None
        instance.is_active = True
        instance.save()
        product_weight = validated_data.pop("product_weight")

        for product in product_weight:
            added_products = ProductWeight.objects.filter(recipe=instance)
            if added_products and product["product"].pk in [name.product.pk for name in added_products]:
                for added_product in added_products:
                    if added_product.product.pk == product["product"].pk:
                        added_product.weight += product["weight"]
                        added_product.save()
                        break
                continue
            ProductWeight.objects.create(recipe=instance, **product)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return instance


class GetRecipeSerializer(PostRecipeSerializer):
    product_weight = ProductWeightDetailSerializer(many=True)


class WaterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Water
        fields = ("weight",)


class PostEatingSerializer(serializers.ModelSerializer):
    product_weight = ProductWeightSerializer(required=False)
    water = WaterSerializer(required=False)

    class Meta:
        model = Eating
        fields = ("id", "datetime_add", "product_weight", "recipe", "water")
        read_only_fields = ("id", "datetime_add")

    def create(self, validated_data) -> dict:
        product_weight = validated_data.pop("product_weight", None)
        recipe = validated_data.pop("recipe", None)
        water = validated_data.pop("water", None)
        eating_validation(product_weight, recipe, water)

        user_id = self.context["user_id"]
        person_card = get_person_card(user_id)

        if product_weight:
            product_weight = ProductWeight.objects.create(**product_weight)

        if water:
            water = Water.objects.create(**water)

        eating = Eating.objects.create(
            product_weight=product_weight, recipe=recipe, water=water, person_card=person_card
        )
        eating.save()
        return eating

    def update(self, instance, validated_data):
        product_weight_data = validated_data.get("product_weight", None)
        recipe = validated_data.get("recipe", None)
        water_data = validated_data.get("water", None)
        eating_validation(product_weight_data, recipe, water_data)

        if instance.product_weight:
            product_weight_old = instance.product_weight
            instance.product_weight = None
            product_weight_old.delete()
        if instance.water:
            water_old = instance.water
            instance.water = None
            water_old.delete()
        instance.recipe = None

        if product_weight_data:
            instance.product_weight = ProductWeight.objects.create(**product_weight_data)
        if recipe:
            instance.recipe = recipe
        if water_data:
            instance.water = Water.objects.create(**water_data)

        instance.save()
        return instance


class GetEatingSerializer(PostEatingSerializer):
    recipe = GetRecipeSerializer()
    product_weight = ProductWeightDetailSerializer()


class CalculateSerializer(serializers.Serializer):
    imt_type = serializers.SerializerMethodField()
    imt_value = serializers.SerializerMethodField()
    calories = serializers.SerializerMethodField()
    proteins = serializers.SerializerMethodField()
    fats = serializers.SerializerMethodField()
    carbohydrates = serializers.SerializerMethodField()
    water = serializers.SerializerMethodField()

    def __init__(self, context=None, instance=None, *args, **kwargs):
        super().__init__(instance, *args, **kwargs)
        if context:
            user_id = context["user_id"]
            str_date = context["date"]
            if str_date:
                try:
                    date = datetime.strptime(str_date, "%Y-%m-%d")
                except ValueError:
                    raise ValidationError({"status": 400, "error": "Invalid date format"})
            else:
                date = timezone.now().date()

            calculate_type = context["calculate_type"]
            person_card = get_person_card(user_id)
            person = KBJYService(person_card, date)
            imt = person.get_imt()
            if calculate_type == "standard":
                result = person.get_standard()
            if calculate_type == "current":
                result = person.get_current()

            self.instance = {
                "imt_type": imt["type"],
                "imt_value": imt["value"],
                "calories": result["calories"],
                "proteins": result["proteins"],
                "fats": result["fats"],
                "carbohydrates": result["carbohydrates"],
                "water": result["water"],
            }

    @extend_schema_field(OpenApiTypes.STR)
    def get_imt_type(self, obj):
        return self.instance["imt_type"]

    @extend_schema_field(OpenApiTypes.INT)
    def get_imt_value(self, obj):
        return self.instance["imt_value"]

    @extend_schema_field(OpenApiTypes.INT)
    def get_calories(self, obj):
        return self.instance["calories"]

    @extend_schema_field(OpenApiTypes.INT)
    def get_proteins(self, obj):
        return self.instance["proteins"]

    @extend_schema_field(OpenApiTypes.INT)
    def get_fats(self, obj):
        return self.instance["fats"]

    @extend_schema_field(OpenApiTypes.INT)
    def get_carbohydrates(self, obj):
        return self.instance["carbohydrates"]

    @extend_schema_field(OpenApiTypes.INT)
    def get_water(self, obj):
        return self.instance["water"]


class RecommendationSerializer(serializers.Serializer):
    products = serializers.SerializerMethodField()

    def __init__(self, context=None, instance=None, *args, **kwargs):
        super().__init__(instance, *args, **kwargs)
        if context:
            user_id = context["user_id"]
            person_card = get_person_card(user_id)
            person = RecommendationService(person_card)
            self.recommendation = person.get_recommendation()

    @extend_schema_field(ProductSerializerWithCategory)
    def get_products(self, obj):
        if self.recommendation.get("include", None):
            return {"include": ProductSerializerWithCategory(self.recommendation["include"], many=True).data}
        if self.recommendation.get("exclude", None):
            return {"exclude": ProductSerializerWithCategory(self.recommendation["exclude"], many=True).data}
