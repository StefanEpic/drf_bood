from rest_framework import viewsets, mixins
from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .api_docs import (
    product_list_summary,
    person_card_summary,
    measurement_summary,
    recipe_summary,
    eating_summary,
    calculate_current_retrieve_summary,
    calculate_standard_retrieve_summary,
    female_type_summary,
    recommendation_include_summary,
    recommendation_exclude_summary,
    categoryrecommendation_list_summary,
    faq_list_summary,
)
from .filters import TitleSearchFilter, DateSearchFilter
from .models import Product, PersonCard, Eating, Measurement, Recipe, FemaleType, ProductCategory, FAQ
from .permissions import IsOwnerOrAdminPersonCard, IsOwnerOrAdmin
from .serializers import (
    ProductSerializer,
    PostPersonCardSerializer,
    GetPersonCardSerializer,
    MeasurementSerializer,
    GetRecipeSerializer,
    PostRecipeSerializer,
    PostEatingSerializer,
    GetEatingSerializer,
    CalculateSerializer,
    RecommendationIncludeSerializer,
    RecommendationExcludeSerializer,
    FemaleTypeSerializer,
    ProductCategorySerializer,
    FAQSerializer,
)
from .utils.view_validation import view_validation, calculate_view_validation


@product_list_summary
class ProductViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = Product.objects.all().order_by("id")
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "head", "options"]
    filter_backends = [TitleSearchFilter]
    search_fields = ["title"]


@categoryrecommendation_list_summary
class ProductCategoryViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = ProductCategory.objects.all().order_by("id")
    serializer_class = ProductCategorySerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "head", "options"]
    filter_backends = [TitleSearchFilter]
    search_fields = ["title"]


@faq_list_summary
class FAQViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = FAQ.objects.all().order_by("id")
    serializer_class = FAQSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "head", "options"]
    filter_backends = [TitleSearchFilter]
    search_fields = ["question"]


@female_type_summary
class FemaleTypeViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = FemaleType.objects.all().order_by("id")
    serializer_class = FemaleTypeSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "head", "options"]


@person_card_summary
class PersonCardView(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    queryset = PersonCard.objects.all()
    serializer_class = GetPersonCardSerializer
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]
    permission_classes = [IsAuthenticated, IsOwnerOrAdminPersonCard]

    def get_queryset(self):
        if self.request.user:
            return PersonCard.objects.filter(person=self.request.user.pk)
        return super().get_queryset()

    def get_serializer_class(self):
        if self.request.method == "POST" or self.request.method == "PATCH":
            return PostPersonCardSerializer
        return super().get_serializer_class()

    def create(self, request, *args, **kwargs):
        user_id = request.user.id
        serializer = PostPersonCardSerializer(data=request.data, context={"user_id": user_id})
        return view_validation(serializer)

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = PostPersonCardSerializer(instance, data=request.data, partial=True)
        return view_validation(serializer)


@eating_summary
class EatingViewSet(viewsets.ModelViewSet):
    queryset = Eating.objects.all()
    serializer_class = GetEatingSerializer
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
    filter_backends = [DateSearchFilter]
    search_fields = ["datetime_add"]

    def get_queryset(self):
        if self.request.user:
            return Eating.objects.filter(person_card__person=self.request.user.pk)
        return super().get_queryset()

    def get_serializer_class(self):
        if self.request.method == "POST" or self.request.method == "PATCH":
            return PostEatingSerializer
        return super().get_serializer_class()

    def create(self, request, *args, **kwargs):
        user_id = request.user.id
        serializer = PostEatingSerializer(data=request.data, context={"user_id": user_id})
        return view_validation(serializer)

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = PostEatingSerializer(instance, data=request.data, partial=True)
        return view_validation(serializer)


class StandardValuesView(RetrieveAPIView):
    permission_classes = [IsAuthenticated]

    @calculate_standard_retrieve_summary
    def get(self, request, *args, **kwargs) -> Response:
        date = request.query_params.get("date", None)
        user_id = request.user.id
        serializer = CalculateSerializer(
            data=request.data, context={"date": date, "user_id": user_id, "calculate_type": "standard"}
        )
        return calculate_view_validation(serializer)


class CurrentValuesView(RetrieveAPIView):
    permission_classes = [IsAuthenticated]

    @calculate_current_retrieve_summary
    def get(self, request, *args, **kwargs) -> Response:
        date = request.query_params.get("date", None)
        user_id = request.user.id
        serializer = CalculateSerializer(
            data=request.data, context={"date": date, "user_id": user_id, "calculate_type": "current"}
        )
        return calculate_view_validation(serializer)


@measurement_summary
class MeasurementViewSet(viewsets.ModelViewSet):
    queryset = Measurement.objects.all()
    serializer_class = MeasurementSerializer
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]

    def get_queryset(self):
        if self.request.user:
            return Measurement.objects.filter(person_card__person=self.request.user.pk)
        return super().get_queryset()

    def create(self, request, *args, **kwargs):
        user_id = request.user.id
        serializer = MeasurementSerializer(data=request.data, context={"user_id": user_id})
        return view_validation(serializer)

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = MeasurementSerializer(instance, data=request.data, partial=True)
        return view_validation(serializer)


@recipe_summary
class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = GetRecipeSerializer
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
    filter_backends = [TitleSearchFilter]
    search_fields = ["title"]

    def get_queryset(self):
        if self.request.user:
            return Recipe.objects.filter(person_card__person=self.request.user.pk, is_active=True)
        return super().get_queryset()

    def get_serializer_class(self):
        if self.request.method == "POST" or self.request.method == "PATCH":
            return PostRecipeSerializer
        return super().get_serializer_class()

    def create(self, request, *args, **kwargs):
        user_id = request.user.id
        serializer = PostRecipeSerializer(data=request.data, context={"user_id": user_id})
        return view_validation(serializer)

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = PostRecipeSerializer(instance, data=request.data, partial=True)
        return view_validation(serializer)


class RecommendationIncludeView(RetrieveAPIView):
    permission_classes = [IsAuthenticated]

    @recommendation_include_summary
    def get(self, request, *args, **kwargs) -> Response:
        user_id = request.user.id
        serializer = RecommendationIncludeSerializer(data=request.data, context={"user_id": user_id})
        return calculate_view_validation(serializer)


class RecommendationExcludeView(RetrieveAPIView):
    permission_classes = [IsAuthenticated]

    @recommendation_exclude_summary
    def get(self, request, *args, **kwargs) -> Response:
        user_id = request.user.id
        serializer = RecommendationExcludeSerializer(data=request.data, context={"user_id": user_id})
        return calculate_view_validation(serializer)
