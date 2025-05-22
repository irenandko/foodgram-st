# FOODGRAM-ST
## :ice_cream: Описание проекта
**"Фудграм"** — это веб-приложение, объединяющее любителей кулинарии. Делитесь своими рецептами, добавляйте понравившиеся в избранное и подписывайтесь на интересных авторов. Упростите процесс покупок с помощью удобного сервиса "Список покупок", который поможет вам собрать все необходимые ингредиенты для приготовления ваших любимых блюд.

## :dizzy: Перед тем как запускать проект
Установите Docker, используя инструкции с официального сайта и зарегистрируйтесь:
* для [Windows и MacOS](https://www.docker.com/products/docker-desktop/)
* для [Linux](https://docs.docker.com/engine/install/ubuntu/). Отдельно потребуется установть [Docker Compose](https://docs.docker.com/compose/install/)

## :rocket: Клонирование и запуск проекта
Проверьте, что Docker работает (Engine running).
Склонируйте репозиторий с проектом на свой компьютер - в терминале из рабочей директории выполните команду:
```
git clone https://github.com/irenandko/foodgram-st.git
```
Перейдите в главную директорию проекта
```
cd foodgram-st
```
В корне проекта разместите .env файл со следующей структурой:

```
POSTGRES_USER=django_user
POSTGRES_PASSWORD=django_password
POSTGRES_DB=django_db
DB_HOST=db
DB_PORT=5432
SECRET_KEY="django-insecure-64hnnmqdw4a9y^9koemq$r1m+!o(*#=)0pbroo9g-j6&8&%l2p" # для примера
```

## Сборка 
Находясь в корне проекта начните сборку проекта командой:
```
docker-compose up -d --build
```

Далее откройте новое окно терминала и в нем примените миграции:
```
docker-compose exec backend python manage.py migrate
```

Соберите статические материалы:
```
docker-compose exec backend python manage.py collectstatic --noinput
```

Создайте суперпользователя для админки:
```
docker-compose exec backend python manage.py createsuperuser
```

На данном этапе проект уже работает, но стоит заполнить его данными, поэтому загрузите пользователей, ингридиенты и рецепты:
```
docker-compose exec backend python manage.py load_author_list
```
```
docker-compose exec backend python manage.py load_ingridient_list
```
```
docker-compose exec backend python manage.py load_recipe_list
```

## Основные страницы
- Главная страница - http://localhost
- Админка - http://localhost/admin/

* Если Вам отображается приветствие Nginx, попробуйте открыть сайт в режиме Инкогнито (возможен остаточный кэш страниц)

Чтобы остановить работу проекта нажмите Ctrl+C, а затем выполните команду:
```
docker compose down
```

## Автор проекта
Лазаренко Ирина

