from django.core.exceptions import ValidationError

import re


def validate_username(value):
    if value == 'me':
        raise ValidationError(
            ('Имя пользователя "me" запрещено!'),
            params={'value': value}
        )
    if re.search(r'^[a-zA-Z][a-zA-Z0-9-_\.]{1,20}$', value) is None:
        raise ValidationError(
            (f'Cимволы <{value}> - запрещены для использования в нике!'),
            params={'value': value},
        )
