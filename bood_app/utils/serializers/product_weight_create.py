from bood_app.models import ProductWeight, Recipe


def create_product_weight_instances(product_weight: list, recipe: Recipe) -> None:
    """
    Создать экземпляры product_weight для рецепта.
    """
    for product_weight in product_weight:
        ProductWeight.objects.create(recipe=recipe, **product_weight)
