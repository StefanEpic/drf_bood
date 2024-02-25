## 🍎 Bood

![Django](https://img.shields.io/badge/Django-darkgreen?style=flat&logo=django&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-blue?style=flat&logo=postgresql&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-DC382D?style=flat&logo=redis&logoColor=white)
![Elasticsearch](https://img.shields.io/badge/Elasticsearch-005571?style=flat&logo=elastic&logoColor=white)

💪 АPI for for counting calories, proteins, fats and carbohydrates.

The project was developed in [Pinappl practice](https://pnpl.site/)

## 🍏 Usage
- Users can create personal cards, keep measurements and keep a food diary.
- There are 6400 products in the database.
- Based on the food diary and measurements, the user can track their calories, proteins, fats and carbohydrates.
- Users can also receive dietary recommendations based on your food diary.


## 🍪 API demo
You can test:

👉 [Backend API](https://api.bood.pnpl.tech/api/v1/schema/swagger-ui/)

👉 [Front APP](https://front.bood.pnpl.tech/)


## 🍩 Tests
```
Name                                                                             Stmts   Miss  Cover
----------------------------------------------------------------------------------------------------
bood/__init__.py                                                                     0      0   100%
bood/settings.py                                                                    46      0   100%
bood/urls.py                                                                         6      0   100%
bood_account/__init__.py                                                             0      0   100%
bood_account/admin.py                                                               13      0   100%
bood_account/apps.py                                                                 5      0   100%
bood_account/email.py                                                                9      0   100%
bood_account/migrations/0001_initial.py                                              5      0   100%
bood_account/migrations/0002_alter_person_email_alter_person_name.py                 5      0   100%
bood_account/migrations/__init__.py                                                  0      0   100%
bood_account/models.py                                                              41      0   100%
bood_account/serializers.py                                                          6      0   100%
bood_account/tests.py                                                              106      0   100%
bood_account/urls.py                                                                 3      0   100%
bood_account/validators.py                                                          34      0   100%
bood_account/views.py                                                               12      0   100%
bood_app/__init__.py                                                                 0      0   100%
bood_app/admin.py                                                                   64      0   100%
bood_app/api_docs.py                                                                16      0   100%
bood_app/apps.py                                                                     7      0   100%
bood_app/documents.py                                                               30      6    80%
bood_app/filters.py                                                                  5      0   100%
bood_app/migrations/0001_initial.py                                                  8      0   100%
bood_app/migrations/0002_productcategory_alter_faq_options_and_more.py               5      0   100%
bood_app/migrations/0003_alter_product_microelements_alter_product_vitamins.py       5      0   100%
bood_app/migrations/0004_alter_personcard_target.py                                  4      0   100%
bood_app/migrations/0005_alter_personcard_target.py                                  4      0   100%
bood_app/migrations/__init__.py                                                      0      0   100%
bood_app/models.py                                                                 165      0   100%
bood_app/permissions.py                                                              7      0   100%
bood_app/serializers.py                                                            264      0   100%
bood_app/services/__init__.py                                                        0      0   100%
bood_app/services/calculate.py                                                      84      8    90%
bood_app/services/recommendation.py                                                100     20    80%
bood_app/signals.py                                                                 27      0   100%
bood_app/tests/__init__.py                                                           0      0   100%
bood_app/tests/base_classes.py                                                      45      0   100%
bood_app/tests/test_calculate.py                                                    44      0   100%
bood_app/tests/test_eating.py                                                      116      0   100%
bood_app/tests/test_faq.py                                                          14      0   100%
bood_app/tests/test_femaletype.py                                                   14      0   100%
bood_app/tests/test_measurements.py                                                 76      0   100%
bood_app/tests/test_personcard.py                                                  145      0   100%
bood_app/tests/test_products.py                                                     27      0   100%
bood_app/tests/test_recipes.py                                                      68      0   100%
bood_app/tests/test_recommendation.py                                               69      0   100%
bood_app/urls.py                                                                    13      0   100%
bood_app/utils/__init__.py                                                           0      0   100%
bood_app/utils/cache.py                                                             20      1    95%
bood_app/utils/models/__init__.py                                                    0      0   100%
bood_app/utils/models/resources.py                                                   3      0   100%
bood_app/utils/serializers/__init__.py                                               0      0   100%
bood_app/utils/serializers/calculate_date_validation.py                             12      0   100%
bood_app/utils/serializers/eating_validation.py                                     11      0   100%
bood_app/utils/serializers/person_card_validation.py                                 8      0   100%
bood_app/utils/serializers/product_weight_create.py                                  4      0   100%
bood_app/utils/views/__init__.py                                                     0      0   100%
bood_app/utils/views/view_validation.py                                             11      1    91%
bood_app/views.py                                                                  193     11    94%
config.py                                                                           16      0   100%
manage.py                                                                           12      2    83%
----------------------------------------------------------------------------------------------------
TOTAL                                                                             2007     49    98%
```
