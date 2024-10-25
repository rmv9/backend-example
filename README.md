# Kittygram final

### <b>Для ревью</b>
Адрес: http://89.169.171.110/  

Админ-зона: http://89.169.171.110/admin/  

login - admin  
password - admin  
mail - admin@admin.com  


## Описание
Foodgram - дипломный проект, является платформой для публикации своих рецептов. С его помощью можно создавать свои рецепты, публиковать их, а также добавлять в избранное рецепты других пользователей. Проект позволяет скачивать pdf список ингредиентов любого доступного рецепта.

## **Технологии:**

Django==4.2.11
djangorestframework==3.15.1
djoser==2.2.2
psycopg2-binary==2.9.9
Pillow==10.3.0
django-cleanup==8.1.0
django-filter==2.4.0
gunicorn==21.2.0
fpdf2==2.7.8
uharfbuzz==0.39.1
drf_extra_fields==3.7.0

## Подготовка сервера
На примере Linux сервера

1. Подготовка виртуального окружения в директории проекта:
```
nano .env
```

2. Необходимы следующие переменные:
```nano
SECRET_KEY='your_django_secret_key'

DEBUG=False
ALLOWED_HOSTS='your_host_name, your_server_ip, 127.0.0.1, localhost'

POSTGRES_DB=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432
```

3. Устанавливаем к Docker утилиту Docker Compose:
```
sudo apt update
sudo apt-get install docker-compose-plugin 
```

4. Копируем `docker-compose.production.yml` в корневую деректорию проекта.

Сервер готов к деплою проекта.

## Деплой (Linux)  

Для запуска необходим пуш любой ветки проекта:  
```
git add .
git commit -m "any commit"
git push
```

База данных проекта заполняется ингредиентами и тегами на этапе развертывания.  

После автоматического деплоя, на сервере необходимо добавить суперпользователя:  
```
sudo docker compose -f docker-compose.production.yml exec backend python manage.py createsuperuser
```  

Проект готов к использованию.

## Эндпоинты API

* ```/api/users/```  Get-список пользователей. POST-регистрация.

* ```/api/users/{id}``` GET - страница пользователя. 

* ```/api/users/set_password``` POST - смена пароля

* ```/api/auth/token/login/``` POST - получение токена по логину и паролю.

* ```/api/auth/token/logout/``` POST - удаление токена. 

* ```/api/tags/``` GET - получение списка тегов.

* ```/api/tags/{id}``` GET - информация о теге.


## Об авторе
>[Maxim Razdorozhnyi](https://github.com/rmv9).