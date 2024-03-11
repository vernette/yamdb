# YaMDb API
Проект YaMDb представляет собой платформу для сбора отзывов пользователей на различные произведения и работы. В YaMDb произведения не хранятся напрямую, но здесь пользователи могут оставлять свои отзывы и оценки к фильмам, книгам, музыке и другим произведениям.

## Установка и запуск проекта

1.  Склонируйте репозиторий:

    ```bash
    git clone https://github.com/vernette/api_yamdb
    ```

2.  Перейдите в каталог с проектом:

    ```bash
    cd api_yamdb
    ```

3. Создайте и активируйте виртуальное окружение

    ### Linux/macOS

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

    ### Windows

    ```bash
    python -m venv venv
    venv\Scripts\activate
    ```

4.  Установите зависимости:

    ```bash
    pip install -r requirements.txt
    ```

4.  Выполните миграции:

    ```bash
    python api_yamdb/manage.py migrate
    ```

5.  Запустите сервер:

    ```bash
    python api_yamdb/manage.py runserver
    ```

## Примеры запросов

### Регистрация нового пользователя

Отправьте POST-запрос с параметрами email и username на эндпоинт `/api/v1/auth/signup/`. После этого пользователю на электронную почту придёт код подтверждения.

```http request
POST /api/v1/auth/signup/
Content-Type: application/json

{
    "email": "example@example.com",
    "username": "example_user"
}
```

### Получение токена аутентификации

Отправьте POST-запрос с параметрами username и confirmation_code на эндпоинт `/api/v1/auth/token/`. В ответ на запрос вы получите JWT-токен.

```http request
POST /api/v1/auth/token/
Content-Type: application/json

{
    "username": "example_user",
    "confirmation_code": "ваш_код_подтверждения"
}
```

Для повторного получения JWT токена пользователю требуется заного пройти этап регистрации и отправить запрос уже с новым кодом подтверждения.

### Получение списка произведений

Отправьте GET-запрос на эндпоинт `/api/v1/titles/` для получения списка всех произведений.

```http request
GET /api/v1/titles/
```

Для этого и подобных запросов поддерживается пагинация, а также есть возможность ограничить число получаемых объектов.

```http request
GET /api/v1/titles/?limit=10&offset=0
```

### Получение списка категорий

Отправьте GET-запрос на эндпоинт `/api/v1/categories/` для получения списка всех категорий произведений.

```http request
GET /api/v1/categories/
```

### Создание отзыва

Отправьте POST-запрос с данными отзыва на эндпоинт `/api/v1/titles/{title_id}/reviews/`. Обратите внимание, что для создания отзыва пользователь должен быть аутентифицирован. Пользователь может поставить оценку от 0 до 10.

```http request
POST /api/v1/titles/{title_id}/reviews/
Content-Type: application/json
Authorization: Bearer ваш_jwt_токен

{
    "text": "Текст вашего отзыва",
    "score": 8
}
```
### Оставить комментарий к отзыву
Отправьте POST-запрос с данными отзыва на эндпоинт `/api/v1/titles/{title_id}/reviews/{review_id}/comments/`. Обратите внимание, что для создания отзыва пользователь должен быть аутентифицирован.


```http request
POST /api/v1/titles/{title_id}/reviews/{review_id}/comments/
Content-Type: application/json
Authorization: Bearer ваш_jwt_токен

{
    "text": "Текст вашего комментария"
}
```

## Полная документация доступна по [ссылке](http://127.0.0.1:8000/redoc/)