from django.utils import timezone
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
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
from .services.calculate import CalculateService
from .services.recommendation import RecommendationService
from bood_app.utils.serializers.calculate_date_validation import check_dateformat_or_get_current_date
from bood_app.utils.serializers.eating_validation import eating_validation
from bood_app.utils.serializers.person_card_validation import get_person_card
from .utils.serializers.product_weight_create import create_product_weight_instances


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ("id", "title", "proteins", "fats", "carbohydrates", "calories", "water")
        read_only_fields = ("id", "title", "proteins", "fats", "carbohydrates", "calories", "water")


class ProductSearchSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField()
    proteins = serializers.FloatField()
    fats = serializers.FloatField()
    carbohydrates = serializers.FloatField()
    calories = serializers.FloatField()
    water = serializers.FloatField()


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
        gender = validated_data.get("gender")
        femaletype = validated_data.get("femaletype")
        exclude_products = validated_data.get("exclude_products")
        exclude_category = validated_data.get("exclude_category")
        user_id = self.context["user_id"]

        person_card = PersonCard.objects.filter(person__id=user_id).first()
        if person_card is not None:
            raise ValidationError({"status": "400", "error": "You already have person card"})

        if femaletype:
            if gender == "male":
                raise ValidationError({"status": "400", "error": "Male gender can't have female type"})

        if exclude_products:
            if len(exclude_products) > 20:
                raise ValidationError({"status": "400", "error": "Limit of excluded products 20"})

        if exclude_category:
            if len(exclude_category) > 5:
                raise ValidationError({"status": "400", "error": "Limit of excluded products categories 5"})

        validated_data.update({"person_id": user_id})
        return super().create(validated_data)

    def update(self, instance, validated_data):
        gender = validated_data.get("gender", None)
        femaletype = validated_data.get("femaletype", None)
        exclude_products = validated_data.get("exclude_products", None)
        exclude_category = validated_data.get("exclude_category", None)

        if femaletype and instance.gender == "male" and gender != "female" or femaletype and gender == "male":
            raise ValidationError({"status": "400", "error": "Male gender can't have female type"})

        if gender == "male":
            validated_data.update({"femaletype": []})

        if exclude_products:
            if len(exclude_products) > 20:
                raise ValidationError({"status": "400", "error": "Limit of excluded products 20"})

        if exclude_category:
            if len(exclude_category) > 5:
                raise ValidationError({"status": "400", "error": "Limit of excluded products categories 5"})

        return super().update(instance, validated_data)


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

        create_product_weight_instances(product_weight, recipe)
        return recipe

    def update(self, instance, validated_data):
        instance.is_active = False
        instance.save()
        instance.pk = None
        instance.is_active = True
        instance.save()
        product_weight = validated_data.pop("product_weight")

        create_product_weight_instances(product_weight, instance)

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
            calculate_type = context["calculate_type"]
            date = check_dateformat_or_get_current_date(str_date)
            person_card = get_person_card(user_id)
            person = CalculateService(person_card, date)
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


class RecommendationIncludeSerializer(serializers.Serializer):
    products = serializers.SerializerMethodField()

    def __init__(self, context=None, instance=None, *args, **kwargs):
        super().__init__(instance, *args, **kwargs)
        if context:
            user_id = context["user_id"]
            person_card = get_person_card(user_id)
            date = timezone.now().date()
            person = RecommendationService(person_card, date)
            self.recommendation = person.get_include_products()

    @extend_schema_field(ProductSerializerWithCategory(many=True))
    def get_products(self, obj):
        return ProductSerializerWithCategory(self.recommendation, many=True).data


class RecommendationExcludeSerializer(serializers.Serializer):
    product = serializers.SerializerMethodField()

    def __init__(self, context=None, instance=None, *args, **kwargs):
        super().__init__(instance, *args, **kwargs)
        if context:
            user_id = context["user_id"]
            person_card = get_person_card(user_id)
            date = timezone.now().date()
            person = RecommendationService(person_card, date)
            self.recommendation = person.get_exclude_product()

    @extend_schema_field(ProductSerializerWithCategory)
    def get_product(self, obj):
        return ProductSerializerWithCategory(self.recommendation).data
