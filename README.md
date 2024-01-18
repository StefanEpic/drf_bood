## 🍎 Bood

![Django](https://img.shields.io/badge/Django-darkgreen?style=flat&logo=django&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-blue?style=flat&logo=postgresql&logoColor=white)

💪 АPI for for counting calories, proteins, fats and carbohydrates.

The project was developed in [Pinappl practice](https://pnpl.site/)

## 🍏 Usage
- Users can create personal cards, keep measurements and keep a food diary.
- There are 6400 products in the database.
- Based on the food diary and measurements, the user can track their calories, proteins, fats and carbohydrates.
- Users can also receive dietary recommendations based on your food diary.


## 🍪 API demo
You can test:

👉 [Swagger](http://stefanepic.ru/bood/schema/swagger-ui/):

- username: admin@admin.com
- password: 12345

## 🍩 Tests
```Name                                       Stmts   Miss  Cover
--------------------------------------------------------------
bood/__init__.py                               0      0   100%
bood/settings.py                              41      0   100%
bood/urls.py                                   6      0   100%
bood_account/__init__.py                       0      0   100%
bood_account/admin.py                         13      0   100%
bood_account/apps.py                           5      0   100%
bood_account/email.py                          9      0   100%
bood_account/migrations/0001_initial.py        5      0   100%
bood_account/migrations/__init__.py            0      0   100%
bood_account/models.py                        40      0   100%
bood_account/serializers.py                    6      0   100%
bood_account/tests.py                         73      0   100%
bood_account/urls.py                           3      0   100%
bood_account/views.py                         12      0   100%
bood_app/__init__.py                           0      0   100%
bood_app/admin.py                             62      5    92%
bood_app/api_docs.py                          14      0   100%
bood_app/apps.py                               7      0   100%
bood_app/filters.py                            5      0   100%
bood_app/migrations/0001_initial.py            8      0   100%
bood_app/migrations/__init__.py                0      0   100%
bood_app/models.py                           136      0   100%
bood_app/permissions.py                        7      0   100%
bood_app/serializers.py                      257      0   100%
bood_app/services/__init__.py                  0      0   100%
bood_app/services/kbjy.py                    129      8    94%
bood_app/signals.py                           27      0   100%
bood_app/tests/__init__.py                     0      0   100%
bood_app/tests/base_classes.py                42      0   100%
bood_app/tests/test_calculate.py              44      0   100%
bood_app/tests/test_eating.py                104      0   100%
bood_app/tests/test_faq.py                    14      0   100%
bood_app/tests/test_femaletype.py             14      0   100%
bood_app/tests/test_measurements.py           76      0   100%
bood_app/tests/test_personcard.py            100      0   100%
bood_app/tests/test_products.py               27      0   100%
bood_app/tests/test_recipes.py                66      0   100%
bood_app/tests/test_recommendation.py         33      0   100%
bood_app/urls.py                              13      0   100%
bood_app/utils/__init__.py                     0      0   100%
bood_app/utils/eating_validation.py           11      0   100%
bood_app/utils/person_card_validation.py       8      0   100%
bood_app/utils/resources.py                    3      0   100%
bood_app/utils/view_validation.py             11      1    91%
bood_app/views.py                            151      7    95%
config.py                                     16      0   100%
manage.py                                     12      2    83%
--------------------------------------------------------------
TOTAL                                       1610     23    99%
```
