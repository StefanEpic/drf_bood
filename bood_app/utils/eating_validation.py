from rest_framework import serializers, status


def eating_validation(product_weight: dict, recipe: int, water: dict) -> None:
    """
    Проверка наличия только одного элемента
    """
    elements = [product_weight, recipe, water]

    if not any(elements):
        raise serializers.ValidationError(
            {
                "status": status.HTTP_400_BAD_REQUEST,
                "error": "product_weight, recipe and water cannot be NULL at the same time",
            },
        )

    count = 0
    for e in elements:
        if e is not None:
            count += 1
        if count == 2:
            raise serializers.ValidationError(
                {
                    "status": status.HTTP_400_BAD_REQUEST,
                    "error": "only one value can be passed (product_weight, recipe or water)",
                },
            )
