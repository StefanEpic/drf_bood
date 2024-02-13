from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter

from bood_app.serializers import (
    CalculateSerializer,
    RecommendationIncludeSerializer,
    RecommendationExcludeSerializer,
    ProductSearchSerializer,
)

product_list_summary = extend_schema_view(
    list=extend_schema(summary="Получение списка продуктов (есть фильтрация)", description="Поиск по названию продукта")
)

product_search_summary = extend_schema(
    parameters=[OpenApiParameter("title", OpenApiTypes.STR, OpenApiParameter.QUERY)],
    summary="Поиск продукта по названию",
    description="Поиск продукта по названию",
    request=None,
    responses=ProductSearchSerializer(many=True),
)

categoryrecommendation_list_summary = extend_schema_view(
    list=extend_schema(
        summary="Получение списка категорий продуктов (есть фильтрация)",
        description="Поиск по названию категории",
    ),
)

faq_list_summary = extend_schema_view(
    list=extend_schema(summary="Часто задаваемые вопросы", description="Поиск по названию вопроса")
)

person_card_summary = extend_schema_view(
    list=extend_schema(summary="Получить свою карточку"),
    partial_update=extend_schema(summary="Изменение карточки пользователя по id карточки"),
    create=extend_schema(summary="Создание карточки пользователя"),
    destroy=extend_schema(summary="Удаление карточки пользователя по id карточки"),
)

female_type_summary = extend_schema_view(
    list=extend_schema(summary="Получить типы женщин"),
)

measurement_summary = extend_schema_view(
    list=extend_schema(summary="Получить все свои замеры"),
    retrieve=extend_schema(summary="Получить свой замер по id замера"),
    create=extend_schema(summary="Создание замеров пользователя"),
    partial_update=extend_schema(summary="Частичное изменение замеров пользователя по id замера"),
    destroy=extend_schema(summary="Удаление замеров пользователя по id замера"),
)

recipe_summary = extend_schema_view(
    list=extend_schema(summary="Получить свой список рецептов"),
    retrieve=extend_schema(summary="Получить свой рецепт по ID"),
    create=extend_schema(summary="Создание нового рецепта"),
    partial_update=extend_schema(summary="Частичное изменение рецепта по ID"),
    destroy=extend_schema(summary="Удаление рецепта по ID"),
)

eating_summary = extend_schema_view(
    list=extend_schema(
        summary="Получение списка приемов пищи пользователя", description="Получить список приемов пищи пользователя"
    ),
    retrieve=extend_schema(
        summary="Получить информацию о приеме пищи по ID",
        description="Получить подробную информацию о конкретном приеме пищи по его ID",
    ),
    create=extend_schema(
        summary="Создание нового приема пищи", description="Создать новую запись о приеме пищи для пользователя"
    ),
    partial_update=extend_schema(
        summary="Частичное изменение информации о приеме пищи по ID",
        description="Внести частичные изменения в информацию о приеме пищи по его ID",
    ),
    destroy=extend_schema(
        summary="Удаление приема пищи по ID", description="Удалить информацию о приеме пищи по его ID"
    ),
)

calculate_current_retrieve_summary = extend_schema(
    parameters=[OpenApiParameter("date", OpenApiTypes.DATE, OpenApiParameter.QUERY)],
    summary="Получение текущих КБЖУ пользователя на определенную дату",
    description="Получение текущих КБЖУ пользователя на определенную дату."
    "Если дата не передана, значения передаются на текущую дату",
    request=None,
    responses=CalculateSerializer,
)

calculate_standard_retrieve_summary = extend_schema(
    parameters=[OpenApiParameter("date", OpenApiTypes.DATE, OpenApiParameter.QUERY)],
    summary="Получение нормативных КБЖУ пользователя на определенную дату",
    description="Получение нормативных КБЖУ пользователя на определенную дату."
    "Если дата не передана, значения передаются на текущую дату",
    request=None,
    responses=CalculateSerializer,
)

recommendation_include_summary = extend_schema(
    summary="Получить рекомендацию по питанию",
    description="В зависимости от съеденных за сегодня продуктов выдается рекомендация "
    "о предлагаемых к включению в рацион продуктов",
    request=None,
    responses=RecommendationIncludeSerializer,
)

recommendation_exclude_summary = extend_schema(
    summary="Получить рекомендацию по питанию",
    description="В зависимости от съеденных за сегодня продуктов выдается рекомендация "
    "о предлагаемом к исключению из рациона продукте",
    request=None,
    responses=RecommendationExcludeSerializer,
)
