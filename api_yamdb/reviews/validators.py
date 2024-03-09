from django.core.exceptions import ValidationError

import re


def validate_username(value):
    if value == 'me':
        raise ValidationError(
            'Имя пользователя "me" запрещено!'
        )
    elif re.search(r'^[\w.@+-]+\Z', value) is None:
        raise ValidationError(
            f'Cимволы <{value}> - запрещены для использования в нике!'
        )
    else:
        return value
