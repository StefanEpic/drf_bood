from django.urls import reverse

from bood_account.models import Person
from bood_app.models import (
    Product,
    Vitamin,
    MicroElement,
    ProductCategory,
    FemaleType,
    Measurement,
    PersonCard,
    Recipe,
    ProductWeight,
    Eating,
    Water,
    FAQ,
)
from rest_framework.test import APITestCase


class BaseInitTestCase(APITestCase):
    def setUp(self):
        self.vitamin1 = Vitamin.objects.create(
            a=0.0,
            b1=0.0,
            b2=0.0,
            b3=0.0,
            e=0.0,
            c=0.0,
        )
        self.vitamin2 = Vitamin.objects.create(
            a=0.0,
            b1=0.0,
            b2=0.0,
            b3=0.0,
            e=0.0,
            c=0.0,
        )
        self.vitamin3 = Vitamin.objects.create(
            a=0.0,
            b1=0.0,
            b2=0.0,
            b3=0.0,
            e=0.0,
            c=0.0,
        )
        self.microelement1 = MicroElement.objects.create(
            iron=0.0, calcium=0.0, sodium=0.0, potassium=0.0, phosphorus=0.0
        )
        self.microelement2 = MicroElement.objects.create(
            iron=0.0, calcium=0.0, sodium=0.0, potassium=0.0, phosphorus=0.0
        )
        self.microelement3 = MicroElement.objects.create(
            iron=0.0, calcium=0.0, sodium=0.0, potassium=0.0, phosphorus=0.0
        )
        self.category1 = ProductCategory.objects.create(title="Овощи")
        self.category2 = ProductCategory.objects.create(title="Птица")
        self.category3 = ProductCategory.objects.create(title="Хлеб")
        self.product1 = Product.objects.create(
            title="Лук",
            proteins=0.014,
            fats=0.002,
            carbohydrates=0.082,
            calories=0.41,
            water=0.86,
            proteins_proportion=7.0,
            fats_proportion=1.0,
            carbohydrates_proportion=41.0,
            category_id=1,
            vitamins_id=1,
            microelements_id=1,
        )
        self.product2 = Product.objects.create(
            title="Курица",
            proteins=0.182,
            fats=0.184,
            carbohydrates=0.0,
            calories=2.38,
            water=0.626,
            proteins_proportion=1.0,
            fats_proportion=1.01,
            carbohydrates_proportion=0.0,
            category_id=2,
            vitamins_id=2,
            microelements_id=2,
        )
        self.product3 = Product.objects.create(
            title="Батон",
            proteins=0.077,
            fats=0.03,
            carbohydrates=0.501,
            calories=2.59,
            water=0.341,
            proteins_proportion=3.21,
            fats_proportion=1.0,
            carbohydrates_proportion=22.04,
            category_id=3,
            vitamins_id=3,
            microelements_id=3,
        )
        self.femaletype = FemaleType.objects.create(title="Беременная")
        self.person1 = Person.objects.create_superuser(email="admin@admin.com", password="12345")
        self.person2 = Person.objects.create_superuser(email="admin2@admin.com", password="12345")
        self.person_card1 = PersonCard.objects.create(
            height=175,
            age=30,
            gender="male",
            activity=1.2,
            person=self.person1,
        )
        self.person_card1.femaletype.set([self.femaletype])
        self.person_card1.exclude_category.set([self.category2])
        self.measurement = Measurement.objects.create(
            weight=80,
            chest=100,
            waist=70,
            hips=90,
            hand=16,
            person_card=self.person_card1,
        )
        self.recipe = Recipe.objects.create(title="Бутерброд с курицей", person_card=self.person_card1)
        self.productweight1 = ProductWeight.objects.create(weight=100, product=self.product2, recipe=self.recipe)
        self.productweight2 = ProductWeight.objects.create(weight=100, product=self.product3, recipe=self.recipe)
        self.water1 = Water.objects.create(weight=100)
        self.eating1 = Eating.objects.create(product_weight=self.productweight1, person_card=self.person_card1)
        self.eating2 = Eating.objects.create(recipe=self.recipe, person_card=self.person_card1)
        self.eating3 = Eating.objects.create(water=self.water1, person_card=self.person_card1)
        self.faq = FAQ.objects.create(question="Question", answer="Answer")

    def get_authorization(self, person_id: int) -> dict:
        create_jwt_url = reverse("jwt-create")
        if person_id == 1:
            create_jwt_data = {"email": "admin@admin.com", "password": "12345"}
        if person_id == 2:
            create_jwt_data = {"email": "admin2@admin.com", "password": "12345"}
        response = self.client.post(create_jwt_url, create_jwt_data)
        access_token = response.data["access"]
        return {"Authorization": f"JWT {access_token}"}
