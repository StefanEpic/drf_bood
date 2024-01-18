from djoser.serializers import UserCreateSerializer
from .models import Person


class PersonCreateSerializer(UserCreateSerializer):
    class Meta(UserCreateSerializer.Meta):
        model = Person
        fields = ("id", "email", "name", "password")
