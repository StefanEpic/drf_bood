from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    ProductViewSet,
    PersonCardView,
    EatingViewSet,
    StandardValuesView,
    CurrentValuesView,
    MeasurementViewSet,
    RecipeViewSet,
    RecommendationIncludeView,
    RecommendationExcludeView,
    FemaleTypeViewSet,
    ProductCategoryViewSet,
    FAQViewSet,
)

router = DefaultRouter()
router.register(r"products", ProductViewSet, basename="products")
router.register(r"products/category", ProductCategoryViewSet, basename="products_category")
router.register(r"personcard", PersonCardView, basename="person_card")
router.register(r"femaletypes", FemaleTypeViewSet, basename="femaletypes")
router.register(r"eating", EatingViewSet, basename="eating")
router.register(r"measurements", MeasurementViewSet, basename="measurements")
router.register(r"recipes", RecipeViewSet, basename="recipes")
router.register(r"faq", FAQViewSet, basename="faq")

urlpatterns = [
    path("", include(router.urls)),
    path("calculate/standard/", StandardValuesView.as_view(), name="standard"),
    path("calculate/current/", CurrentValuesView.as_view(), name="current"),
    path("recommendation/include", RecommendationIncludeView.as_view(), name="recommendation_include"),
    path("recommendation/exclude", RecommendationExcludeView.as_view(), name="recommendation_exclude"),
]
