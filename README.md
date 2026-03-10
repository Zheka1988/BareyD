# Maps

Веб-приложение на Django + PostGIS для работы с геоданными на интерактивной карте Leaflet.
Включает справочники, фильтрацию объектов, экспорт и инструменты рисования.

## Стек

- Python 3.11, Django 5.2
- PostgreSQL 16 + PostGIS 3.4
- GDAL / GEOS
- Leaflet, HTMX
- Gunicorn + Nginx

## Требования

- Docker и Docker Compose

## Запуск

1. Склонировать репозиторий
2. Настроить `.env` (пример уже в репозитории)
3. Сгенерировать SSL-сертификат (см. раздел ниже)
4. Запустить:

```bash
docker compose up --build -d
```

5. Готово:

| Ресурс | Адрес |
|--------|-------|
| Сайт | https://localhost |
| Админка | https://localhost/admin/ |
| БД (извне) | localhost:5444 |

HTTP (порт 80) автоматически перенаправляет на HTTPS (порт 443).

## SSL-сертификат

Сертификаты не хранятся в репозитории. Перед первым запуском необходимо сгенерировать самоподписанный сертификат.

**Требования:** установленный OpenSSL (входит в состав Git for Windows, Linux, macOS).

**Генерация:**

```bash
mkdir -p nginx/ssl

openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout nginx/ssl/selfsigned.key \
  -out nginx/ssl/selfsigned.crt \
  -subj "/C=KZ/ST=Local/L=Local/O=Maps/CN=localhost"
```

Файлы будут созданы в `nginx/ssl/`:
- `selfsigned.crt` — сертификат
- `selfsigned.key` — закрытый ключ

Срок действия — 365 дней. Для перегенерации повторить команду выше.

Браузер покажет предупреждение о недоверенном сертификате — это нормально для самоподписанного. Нажать «Дополнительно» -> «Продолжить».

Логин по умолчанию: `admin` / `admin` (настраивается в `.env`).

## Контейнеры

| Контейнер | Сервис | Назначение |
|-----------|--------|-----------|
| bareyd-db-1 | db | PostgreSQL 16 + PostGIS 3.4 |
| bareyd-web-1 | web | Django-приложение (Gunicorn) |
| bareyd-nginx-1 | nginx | Веб-сервер, раздача статики, проксирование |
| bareyd-scheduler-1 | scheduler | Очистка логов аудита старше 90 дней (раз в сутки) |

## Безопасность

### HTTPS и шифрование
- Принудительный редирект HTTP → HTTPS
- TLS 1.2 / 1.3, сильные шифры (ECDHE-AES-GCM)
- Самоподписанный сертификат (RSA 2048)

### Security headers (Nginx)
- `Strict-Transport-Security` (HSTS, 1 год)
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection: 1; mode=block`
- `Referrer-Policy: strict-origin-when-cross-origin`

### Django
- Secure cookies (`SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE`, `HTTPONLY`)
- Сессия истекает через 1 час или при закрытии браузера
- CSRF-защита на всех формах
- XSS-экранирование пользовательских данных на фронтенде
- Все endpoints требуют аутентификации (`@login_required`)
- Ограничение длины поискового запроса (100 символов)
- `DEBUG=False` в production

### Rate limiting

Защита от перебора паролей и злоупотребления API.

| Endpoint | Лимит | По чему |
|----------|-------|---------|
| `/login/` (POST) | 5 запросов/мин | IP-адрес |
| `/objects/api/markers/` | 60 запросов/мин | Пользователь |
| `/objects/api/search/` | 30 запросов/мин | Пользователь |
| `/objects/api/filters/` | 60 запросов/мин | Пользователь |

При превышении лимита возвращается ответ `429 Too Many Requests`.

### Аудит-логирование

Все действия пользователей логируются в журнал аудита (просмотр в админке):
- CRUD операции (объекты, справочники, пользователи, группы)
- Вход, выход, неудачные попытки входа (с IP)
- Поиск, фильтрация, экспорт
- Автоочистка записей старше 90 дней

## Обновление статики

При изменении JS, CSS или других статических файлов необходимо пересобрать статику внутри контейнера:

```bash
docker compose exec web python manage.py collectstatic --noinput
```

После этого сделать hard refresh в браузере (Ctrl+Shift+R).

## Остановка

```bash
docker compose down
```

Для полной очистки (включая данные БД):

```bash
docker compose down -v
```
