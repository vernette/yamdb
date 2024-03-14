import re

from django.utils import timezone
from rest_framework import serializers
from django.core.exceptions import ValidationError

from reviews.constants import NAME_MAX_LENGTH_LIMIT, EMAIL_MAX_LENGTH_LIMIT


def validate_username(value):
    pattern = re.compile(r'^[\w.@+-]+\Z')
    if (
            value.lower() != "me"
            and pattern.match(value)
            and len(value) < NAME_MAX_LENGTH_LIMIT):
        return value
    raise serializers.ValidationError(
        f'Никнейм {value} недопустим!'
    )


def validate_email(value):
    if len(value) > EMAIL_MAX_LENGTH_LIMIT:
        raise serializers.ValidationError(
            'Адрес электронной почты '
            'не может быть длиннее 150 символов!'
        )
    else:
        return value


def validate_current_year(value):
    if value > timezone.now().year:
        raise ValidationError('Год не может быть больше текущего.')
