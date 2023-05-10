# api_yamdb. Запуск docker-compose.

https://github.com/Hottys/yamdb_final/actions/workflows/yamdb_workflow.yml/badge.svg

## Описание проекта api_yamdb:

Проект **YaMDb** собирает отзывы пользователей на произведения. Сами произведения в **YaMDb** не хранятся, здесь нельзя посмотреть фильм или послушать музыку.
Произведения делятся на ***категории***, такие как «Книги», «Фильмы», «Музыка».
Произведению может быть присвоен ***жанр*** из списка предустановленных (например, «Сказка», «Рок» или «Артхаус»). 
Добавлять произведения, категории и жанры может _только администратор_.
Благодарные или возмущённые пользователи оставляют к произведениям текстовые ***отзывы*** и ставят произведению оценку в диапазоне от одного до десяти (целое число); из пользовательских оценок формируется усреднённая оценка произведения — ***рейтинг*** (целое число).
На одно произведение пользователь может оставить _только один отзыв_.
Пользователи могут оставлять ***комментарии*** к отзывам.
Добавлять отзывы, комментарии и ставить оценки могут только _аутентифицированные пользователи_.

## Установка

1. **Клонировать репозиторий и перейти в него в командной строке:**

   ```
   git clone git@github.com:Hottys/infra_sp2.git
   ```
   ```
   cd infra_sp2
   ```
2. **В директории infra создать файл `.env`, согласно примеру:**

   ```
   DB_ENGINE=django.db.backends.postgresql
   DB_NAME=postgres
   POSTGRES_USER=postgres
   POSTGRES_PASSWORD=postgres
   DB_HOST=db
   DB_PORT=5432
   ```

3. **Запустить docker-compose**

   Выполнить из корневой директории команду:

   ```
   docker-compose up -d
   ```

4.  **Создать и выполнить миграции:**

   ```
   docker-compose exec web python manage.py makemigrations reviews
   docker-compose exec web python manage.py makemigrations users
   docker-compose exec web python manage.py migrate
   ```

5. **Создать суперпользователя**

   ```
   docker-compose exec web python manage.py createsuperuser
   ```

6. **Подгрузить статику**

   ```
   docker-compose exec web python manage.py collectstatic --no-input
   ```

7. **Заполнить БД тестовыми данными**

   Для заполнения базы использовать админку
