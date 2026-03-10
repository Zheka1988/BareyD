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
3. Запустить:

```bash
docker compose up --build -d
```

4. Готово:

| Ресурс | Адрес |
|--------|-------|
| Сайт | http://localhost |
| Админка | http://localhost/admin/ |
| БД (извне) | localhost:5444 |

Логин по умолчанию: `admin` / `admin` (настраивается в `.env`).

## Остановка

```bash
docker compose down
```

Для полной очистки (включая данные БД):

```bash
docker compose down -v
```
