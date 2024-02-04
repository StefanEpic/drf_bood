from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _


def validate_name_field(value: str) -> None:
    """
    Name length and contain letters validator.
    """

    if len(value) < 2:
        raise ValidationError(
            _("The name field length must be between 2 and 30 letters"), code="invalid", params={"value": value}
        )

    incorrect_symbols = r"0123456789!\"#$%&'()*+,./:;<=>?@[\]^_{|}~ "
    for symbol in value:
        if symbol in incorrect_symbols:
            raise ValidationError(
                _("The name field can only contain letters or the sign '-'"), code="invalid", params={"value": value}
            )


class PasswordMaxLengthValidator:
    """
    Validate that the password is of a maximum length.
    """

    def __init__(self, max_length=30) -> None:
        self.max_length = max_length

    def validate(self, password: str, user=None) -> None:
        if len(password) > self.max_length:
            raise ValidationError(
                _("This password must contain no more than %(max_length)d characters."),
                code="password_too_long",
                params={"max_length": self.max_length},
            )

    def get_help_text(self) -> str:
        return _("Your password must contain no more than %(max_length)d characters." % {"max_length": self.max_length})


class LetterPasswordValidator:
    """
    Validate that the password is not entirely letter.
    """

    def validate(self, password: str, user=None) -> None:
        if password.isalpha():
            raise ValidationError(
                _("This password is entirely letter."),
                code="password_entirely_letter",
            )

    def get_help_text(self) -> str:
        return _("Your password can’t be entirely letter.")


class SymbolPasswordValidator:
    """
    Validate that the password is not entirely symbol.
    """

    def validate(self, password: str, user=None) -> None:
        symbols = r"!\"#$%&'()*+,-./:;<=>?@[]^_`{|}~\\"
        only_symbols = True
        for s in password:
            if s not in symbols:
                only_symbols = False
        if only_symbols:
            raise ValidationError(
                _("This password is entirely symbol."),
                code="password_entirely_symbol",
            )

    def get_help_text(self) -> str:
        return _("Your password can’t be entirely symbol.")
