from django.db import models
from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry
from elasticsearch_dsl import analyzer, tokenizer
from bood_app.models import Product

product_tokenizer = tokenizer("product_tokenizer", type="edge_ngram", min_gram=3, max_gram=10, token_chars=["letter"])

product_analyzer = analyzer("product_analyzer", type="custom", tokenizer=product_tokenizer, filter=["lowercase"])


@registry.register_document
class ProductDocument(Document):
    id = fields.LongField(required=True, index=False)
    title = fields.TextField(required=True, multi=True, analyzer=product_analyzer)
    proteins = fields.FloatField(required=True, index=False)
    fats = fields.FloatField(required=True, index=False)
    carbohydrates = fields.FloatField(required=True, index=False)
    calories = fields.FloatField(required=True, index=False)
    water = fields.FloatField(required=True, index=False)

    class Index:
        name = "bood_products"
        settings = {"number_of_shards": 5, "number_of_replicas": 5}

    class Django:
        model = Product


class ElasticFind:
    """
    Base class for search
    """

    def __init__(self, model: models.Model, document: Document):
        self.model = model
        self.document = document

    def get_find(self, query_type: str, **kwargs) -> list:
        """
        Return search result by kwargs
        """
        search = self.document.search().query(query_type, **kwargs)
        response = search.execute()
        result = [p._source.to_dict() for p in response.hits.hits]
        return result
