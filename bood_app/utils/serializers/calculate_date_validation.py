import datetime
from typing import Union

from django.utils import timezone
from rest_framework.exceptions import ValidationError


def check_dateformat_or_get_current_date(str_date: str) -> Union[datetime.date, None]:
    """
    Проверка формата даты или получение текущей даты.
    """
    if str_date:
        try:
            date = datetime.datetime.strptime(str_date, "%Y-%m-%d")
        except ValueError:
            raise ValidationError({"status": 400, "error": "Invalid date format"})
    else:
        date = timezone.now().date()
    return date
