from typing import Union

from rest_framework.exceptions import ValidationError

from bood_app.models import PersonCard


def get_person_card(user_id: int) -> Union[PersonCard, None]:
    """
    Проверка наличия person card.
    """
    person_card = PersonCard.objects.filter(person__id=user_id).first()
    if person_card is None:
        raise ValidationError({"status": "400", "error": "Person card not found"})
    return person_card
